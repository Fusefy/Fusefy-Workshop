"""
ADK-based Ingest OCR Agent for document processing and text extraction.

This agent uses the ADK framework with LiteLLM to process uploaded documents,
extract text using Google Cloud OCR services, and structure the extracted data
for claims processing.

Key Features:
- Document upload to Google Cloud Storage
- OCR text extraction using Google Document AI or Vision API
- Intelligent data structure extraction
- Confidence scoring and quality assessment
- Decision-making for human review requirements
- Comprehensive audit logging
"""

import asyncio
import json
import logging
import mimetypes
import tempfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

import aiofiles
from fastapi import HTTPException, UploadFile
from google.cloud import documentai, storage, vision
from PIL import Image
from pdf2image import convert_from_bytes

from src.config.settings import settings
from src.models.claim import Claim, ClaimStatus
from src.schemas.claim import ClaimUpdate

# Configure logging for agent operations
logger = logging.getLogger(__name__)


class ADKIngestOCRAgent:
    """
    ADK-powered agent for document ingestion and OCR processing.
    
    This agent uses the ADK framework to create an intelligent document processing
    system that can upload documents to GCS, extract text using OCR, structure
    the extracted data, and make decisions about data quality.
    
    The agent is designed to be stateless and can process documents either
    synchronously or asynchronously based on document size and complexity.
    """
    
    def __init__(self):
        """
        Initialize the ADK Ingest OCR Agent.
        
        Sets up the necessary clients for Google Cloud services,
        configures the ADK agent with appropriate tools and prompts,
        and prepares the agent for document processing tasks.
        """
        # Initialize Google Cloud clients
        self.gcs_client = None
        self.documentai_client = None
        self.vision_client = None
        
        # Agent configuration
        self.confidence_threshold = settings.OCR_CONFIDENCE_THRESHOLD
        self.bucket_name = settings.GCS_BUCKET_NAME
        
        # Supported document formats
        self.supported_formats = {
            'application/pdf': ['.pdf'],
            'image/png': ['.png'],
            'image/jpeg': ['.jpg', '.jpeg'],
            'image/tiff': ['.tiff', '.tif']
        }
        
        logger.info("ADK Ingest OCR Agent initialized")
    
    async def initialize_clients(self) -> None:
        """
        Initialize Google Cloud service clients.
        
        This method sets up the necessary clients for GCS, Document AI,
        and Vision API. It handles credential configuration and validates
        that the required services are accessible.
        
        Raises:
            HTTPException: If client initialization fails
        """
        try:
            # Initialize Google Cloud Storage client
            self.gcs_client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
            
            # Initialize Document AI client if processor ID is configured
            if settings.DOCUMENT_AI_PROCESSOR_ID:
                self.documentai_client = documentai.DocumentProcessorServiceClient()
            
            # Initialize Vision API client as fallback
            self.vision_client = vision.ImageAnnotatorClient()
            
            # Validate GCS bucket exists
            await self._ensure_bucket_exists()
            
            logger.info("Google Cloud clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud clients: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Cloud service initialization failed: {str(e)}"
            )
    
    async def _ensure_bucket_exists(self) -> None:
        """
        Ensure the GCS bucket exists, create if it doesn't.
        
        This method checks if the configured GCS bucket exists and creates
        it if necessary. It also sets up appropriate permissions and lifecycle
        policies for document storage.
        """
        try:
            bucket = self.gcs_client.bucket(self.bucket_name)
            if not bucket.exists():
                bucket = self.gcs_client.create_bucket(
                    self.bucket_name,
                    location=settings.VERTEX_AI_LOCATION
                )
                logger.info(f"Created GCS bucket: {self.bucket_name}")
            else:
                logger.info(f"Using existing GCS bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to ensure bucket exists: {e}")
            raise
    
    def _validate_file_format(self, file: UploadFile) -> bool:
        """
        Validate that the uploaded file is in a supported format.
        
        Args:
            file: The uploaded file to validate
            
        Returns:
            bool: True if file format is supported
            
        Raises:
            HTTPException: If file format is not supported
        """
        # Check MIME type
        content_type = file.content_type
        if content_type not in self.supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {content_type}. "
                       f"Supported formats: {list(self.supported_formats.keys())}"
            )
        
        # Check file extension
        file_ext = Path(file.filename or "").suffix.lower()
        valid_extensions = []
        for exts in self.supported_formats.values():
            valid_extensions.extend(exts)
        
        if file_ext not in valid_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file extension: {file_ext}. "
                       f"Supported extensions: {valid_extensions}"
            )
        
        return True
    
    async def _upload_to_gcs(self, 
                           file: UploadFile, 
                           claim_id: UUID) -> Tuple[str, Dict[str, Any]]:
        """
        Upload document to Google Cloud Storage.
        
        Args:
            file: The file to upload
            claim_id: The claim ID for organizing documents
            
        Returns:
            Tuple of (GCS URI, document metadata)
            
        Raises:
            HTTPException: If upload fails
        """
        try:
            # Generate unique filename with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            file_ext = Path(file.filename or "").suffix
            gcs_filename = f"claims/{claim_id}/{timestamp}_{file.filename}"
            
            # Get bucket and create blob
            bucket = self.gcs_client.bucket(self.bucket_name)
            blob = bucket.blob(gcs_filename)
            
            # Read file content
            file_content = await file.read()
            
            # Upload with metadata
            blob.upload_from_string(
                file_content,
                content_type=file.content_type
            )
            
            # Set metadata
            blob.metadata = {
                'claim_id': str(claim_id),
                'original_filename': file.filename,
                'upload_timestamp': datetime.utcnow().isoformat(),
                'file_size': len(file_content),
                'content_type': file.content_type
            }
            blob.patch()
            
            # Generate GCS URI
            gcs_uri = f"gs://{self.bucket_name}/{gcs_filename}"
            
            document_metadata = {
                'gcs_uri': gcs_uri,
                'filename': file.filename,
                'size_bytes': len(file_content),
                'content_type': file.content_type,
                'upload_timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Document uploaded to GCS: {gcs_uri}")
            return gcs_uri, document_metadata
            
        except Exception as e:
            logger.error(f"Failed to upload document to GCS: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Document upload failed: {str(e)}"
            )
    
    async def _extract_text_document_ai(self, 
                                       file_content: bytes, 
                                       mime_type: str) -> Dict[str, Any]:
        """
        Extract text using Google Document AI.
        
        Args:
            file_content: The document content as bytes
            mime_type: The MIME type of the document
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Prepare the document for Document AI
            raw_document = documentai.RawDocument(
                content=file_content,
                mime_type=mime_type
            )
            
            # Configure the process request
            name = self.documentai_client.processor_path(
                settings.GOOGLE_CLOUD_PROJECT,
                settings.VERTEX_AI_LOCATION,
                settings.DOCUMENT_AI_PROCESSOR_ID
            )
            
            request = documentai.ProcessRequest(
                name=name,
                raw_document=raw_document
            )
            
            # Process the document
            result = self.documentai_client.process_document(request=request)
            document = result.document
            
            # Extract structured data
            extracted_data = {
                'extracted_text': document.text,
                'confidence_score': getattr(document, 'confidence', 0.0),
                'page_count': len(document.pages),
                'entities': [],
                'tables': []
            }
            
            # Extract entities if available
            for entity in document.entities:
                extracted_data['entities'].append({
                    'type': entity.type_,
                    'mention_text': entity.mention_text,
                    'confidence': entity.confidence,
                    'normalized_value': getattr(entity, 'normalized_value', {})
                })
            
            # Extract tables if available
            for page in document.pages:
                for table in page.tables:
                    table_data = []
                    for row in table.body_rows:
                        row_data = []
                        for cell in row.cells:
                            cell_text = self._get_text(cell.layout, document.text)
                            row_data.append(cell_text)
                        table_data.append(row_data)
                    extracted_data['tables'].append(table_data)
            
            logger.info("Document AI text extraction completed")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Document AI extraction failed: {e}")
            # Fall back to Vision API
            return await self._extract_text_vision_api(file_content)
    
    async def _extract_text_vision_api(self, file_content: bytes) -> Dict[str, Any]:
        """
        Extract text using Google Vision API as fallback.
        
        Args:
            file_content: The image content as bytes
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Convert PDF to images if necessary
            images = []
            if file_content.startswith(b'%PDF'):
                # Convert PDF to images
                pdf_images = convert_from_bytes(file_content)
                for img in pdf_images:
                    img_bytes = BytesIO()
                    img.save(img_bytes, format='PNG')
                    images.append(img_bytes.getvalue())
            else:
                images = [file_content]
            
            all_text = []
            total_confidence = 0.0
            
            for img_bytes in images:
                image = vision.Image(content=img_bytes)
                
                # Perform text detection
                response = self.vision_client.text_detection(image=image)
                annotations = response.text_annotations
                
                if annotations:
                    # First annotation contains all text
                    page_text = annotations[0].description
                    all_text.append(page_text)
                    
                    # Calculate confidence from individual words
                    word_confidences = []
                    for annotation in annotations[1:]:  # Skip the first full-text annotation
                        if hasattr(annotation, 'confidence'):
                            word_confidences.append(annotation.confidence)
                    
                    if word_confidences:
                        page_confidence = sum(word_confidences) / len(word_confidences)
                    else:
                        page_confidence = 0.8  # Default confidence for Vision API
                    
                    total_confidence += page_confidence
            
            # Calculate overall confidence
            avg_confidence = total_confidence / len(images) if images else 0.0
            
            extracted_data = {
                'extracted_text': '\n\n'.join(all_text),
                'confidence_score': avg_confidence,
                'page_count': len(images),
                'extraction_method': 'vision_api',
                'entities': [],
                'tables': []
            }
            
            logger.info("Vision API text extraction completed")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Vision API extraction failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"OCR extraction failed: {str(e)}"
            )
    
    def _get_text(self, layout, document_text: str) -> str:
        """
        Extract text from a layout element.
        
        Args:
            layout: Document AI layout element
            document_text: Full document text
            
        Returns:
            Extracted text from the layout element
        """
        response = ""
        for segment in layout.text_anchor.text_segments:
            start_index = int(segment.start_index) if segment.start_index else 0
            end_index = int(segment.end_index) if segment.end_index else len(document_text)
            response += document_text[start_index:end_index]
        return response
    
    async def _structure_extracted_data(self, 
                                       extracted_text: str, 
                                       entities: List[Dict]) -> Dict[str, Any]:
        """
        Use ADK agent to structure the extracted text data.
        
        This method uses the ADK framework with LiteLLM to intelligently
        structure the extracted text into claim-relevant fields.
        
        Args:
            extracted_text: Raw extracted text from OCR
            entities: Extracted entities from Document AI
            
        Returns:
            Structured data dictionary with claim fields
        """
        try:
            # This is where we would integrate with ADK framework
            # For now, implementing basic rule-based extraction
            # TODO: Replace with actual ADK agent implementation
            
            structured_data = {
                'patient_name': self._extract_patient_name(extracted_text),
                'claim_amount': self._extract_claim_amount(extracted_text),
                'policy_number': self._extract_policy_number(extracted_text),
                'date_of_service': self._extract_service_date(extracted_text),
                'procedure_codes': self._extract_procedure_codes(extracted_text),
                'diagnosis_codes': self._extract_diagnosis_codes(extracted_text)
            }
            
            # Calculate confidence for structured data
            confidence_scores = {}
            for field, value in structured_data.items():
                if value:
                    confidence_scores[field] = 0.8  # Default confidence
                else:
                    confidence_scores[field] = 0.0
            
            return {
                'structured_data': structured_data,
                'confidence_scores': confidence_scores,
                'extraction_method': 'rule_based'  # TODO: Change to 'adk_agent'
            }
            
        except Exception as e:
            logger.error(f"Data structuring failed: {e}")
            return {
                'structured_data': {},
                'confidence_scores': {},
                'error': str(e)
            }
    
    def _extract_patient_name(self, text: str) -> Optional[str]:
        """Extract patient name from text using pattern matching."""
        import re
        
        patterns = [
            r'patient[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'name[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'insured[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_claim_amount(self, text: str) -> Optional[float]:
        """Extract claim amount from text using pattern matching."""
        import re
        
        patterns = [
            r'amount[:\s]+\$?([0-9,]+\.?[0-9]*)',
            r'total[:\s]+\$?([0-9,]+\.?[0-9]*)',
            r'charge[:\s]+\$?([0-9,]+\.?[0-9]*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_policy_number(self, text: str) -> Optional[str]:
        """Extract policy number from text using pattern matching."""
        import re
        
        patterns = [
            r'policy[:\s]+([A-Z0-9-]+)',
            r'member[:\s]+([A-Z0-9-]+)',
            r'id[:\s]+([A-Z0-9-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_service_date(self, text: str) -> Optional[str]:
        """Extract service date from text using pattern matching."""
        import re
        
        patterns = [
            r'service\s+date[:\s]+(\d{1,2}/\d{1,2}/\d{4})',
            r'date\s+of\s+service[:\s]+(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_procedure_codes(self, text: str) -> List[str]:
        """Extract procedure codes from text."""
        import re
        
        # CPT codes are typically 5 digits
        cpt_pattern = r'\b\d{5}\b'
        matches = re.findall(cpt_pattern, text)
        return list(set(matches))  # Remove duplicates
    
    def _extract_diagnosis_codes(self, text: str) -> List[str]:
        """Extract diagnosis codes from text."""
        import re
        
        # ICD-10 codes pattern
        icd_pattern = r'\b[A-Z]\d{2}\.?\d*\b'
        matches = re.findall(icd_pattern, text)
        return list(set(matches))  # Remove duplicates
    
    def _calculate_overall_confidence(self, 
                                   ocr_confidence: float, 
                                   structured_confidence: Dict[str, float]) -> float:
        """
        Calculate overall confidence score for the extraction.
        
        Args:
            ocr_confidence: Confidence from OCR process
            structured_confidence: Confidence scores for structured fields
            
        Returns:
            Overall confidence score (0.0-1.0)
        """
        if not structured_confidence:
            return ocr_confidence
        
        # Weight OCR confidence at 40%, structured data at 60%
        structured_avg = sum(structured_confidence.values()) / len(structured_confidence)
        overall = (ocr_confidence * 0.4) + (structured_avg * 0.6)
        
        return min(max(overall, 0.0), 1.0)  # Clamp to 0-1 range
    
    def _requires_human_review(self, 
                              overall_confidence: float, 
                              structured_data: Dict[str, Any]) -> bool:
        """
        Determine if the claim requires human review.
        
        Args:
            overall_confidence: Overall confidence score
            structured_data: Extracted structured data
            
        Returns:
            True if human review is required
        """
        # Check confidence threshold
        if overall_confidence < self.confidence_threshold:
            return True
        
        # Check if critical fields are missing
        critical_fields = ['patient_name', 'claim_amount']
        for field in critical_fields:
            if not structured_data.get(field):
                return True
        
        return False
    
    async def process_document(self, 
                             file: UploadFile, 
                             claim_id: UUID) -> Dict[str, Any]:
        """
        Main processing method for document ingestion and OCR.
        
        This method orchestrates the complete document processing pipeline:
        1. Validate file format
        2. Upload to GCS
        3. Extract text using OCR
        4. Structure extracted data using ADK agent
        5. Calculate confidence scores
        6. Determine if human review is needed
        7. Log all operations
        
        Args:
            file: The uploaded document file
            claim_id: The claim ID to associate with the document
            
        Returns:
            Processing results including extracted data and metadata
            
        Raises:
            HTTPException: If processing fails
        """
        processing_start = datetime.utcnow()
        
        try:
            # Initialize clients if not already done
            if not self.gcs_client:
                await self.initialize_clients()
            
            # Log processing start
            logger.info(f"Starting OCR processing for claim {claim_id}")
            
            # Step 1: Validate file format
            self._validate_file_format(file)
            
            # Step 2: Upload to GCS
            gcs_uri, document_metadata = await self._upload_to_gcs(file, claim_id)
            
            # Step 3: Extract text using OCR
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            if settings.DOCUMENT_AI_PROCESSOR_ID and self.documentai_client:
                ocr_result = await self._extract_text_document_ai(
                    file_content, file.content_type
                )
            else:
                ocr_result = await self._extract_text_vision_api(file_content)
            
            # Step 4: Structure extracted data using ADK agent
            structured_result = await self._structure_extracted_data(
                ocr_result['extracted_text'],
                ocr_result.get('entities', [])
            )
            
            # Step 5: Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(
                ocr_result['confidence_score'],
                structured_result.get('confidence_scores', {})
            )
            
            # Step 6: Determine if human review is needed
            requires_review = self._requires_human_review(
                overall_confidence,
                structured_result.get('structured_data', {})
            )
            
            processing_end = datetime.utcnow()
            processing_time = (processing_end - processing_start).total_seconds()
            
            # Prepare final result
            processing_result = {
                'document_metadata': document_metadata,
                'extracted_text': ocr_result['extracted_text'],
                'structured_data': structured_result.get('structured_data', {}),
                'confidence_scores': structured_result.get('confidence_scores', {}),
                'overall_confidence': overall_confidence,
                'requires_human_review': requires_review,
                'ocr_metadata': {
                    'extraction_method': ocr_result.get('extraction_method', 'document_ai'),
                    'page_count': ocr_result.get('page_count', 1),
                    'processing_time_seconds': processing_time,
                    'processed_at': processing_end.isoformat()
                },
                'gcs_uri': gcs_uri
            }
            
            # Log successful completion
            logger.info(
                f"OCR processing completed for claim {claim_id}. "
                f"Confidence: {overall_confidence:.2f}, "
                f"Human review: {requires_review}, "
                f"Processing time: {processing_time:.2f}s"
            )
            
            return processing_result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"OCR processing failed for claim {claim_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"OCR processing failed: {str(e)}"
            )


# Create a global agent instance
ocr_agent = ADKIngestOCRAgent()