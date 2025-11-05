/**
 * Claims API Service
 * 
 * Service functions for all claim-related API operations.
 * Provides typed interfaces for CRUD operations and error handling.
 */

import { apiClient, apiRequest, buildQueryParams } from './api';
import type { 
  Claim, 
  ClaimCreate, 
  ClaimUpdate, 
  ClaimsResponse, 
  ClaimFilters,
  ClaimStatus,
  AgentStatus,
  OCRResult
} from '@/types';

/**
 * Claims Service Class
 */
export class ClaimsService {
  
  /**
   * Get paginated list of claims with optional filtering
   */
  static async getClaims(filters: ClaimFilters = {}): Promise<ClaimsResponse> {
    const queryString = buildQueryParams({
      skip: filters.skip || 0,
      limit: filters.limit || 20,
      status: filters.status,
      search: filters.search,
      date_from: filters.date_from,
      date_to: filters.date_to,
      claim_type: filters.claim_type,
    });

    return apiRequest(() => 
      apiClient.get<ClaimsResponse>(`/api/v1/claims?${queryString}`)
    );
  }

  /**
   * Get a single claim by ID
   */
  static async getClaimById(id: string): Promise<Claim> {
    return apiRequest(() => 
      apiClient.get<Claim>(`/api/v1/claims/${id}`)
    );
  }

  /**
   * Create a new claim
   */
  static async createClaim(claimData: ClaimCreate): Promise<Claim> {
    return apiRequest(() => 
      apiClient.post<Claim>('/api/v1/claims', claimData)
    );
  }

  /**
   * Update an existing claim
   */
  static async updateClaim(id: string, claimData: ClaimUpdate): Promise<Claim> {
    return apiRequest(() => 
      apiClient.patch<Claim>(`/api/v1/claims/${id}`, claimData)
    );
  }

  /**
   * Delete a claim
   */
  static async deleteClaim(id: string): Promise<void> {
    return apiRequest(() => 
      apiClient.delete(`/api/v1/claims/${id}`)
    );
  }

  /**
   * Get claims by status
   */
  static async getClaimsByStatus(
    status: ClaimStatus, 
    skip = 0, 
    limit = 20
  ): Promise<ClaimsResponse> {
    const queryString = buildQueryParams({ skip, limit });
    
    return apiRequest(() => 
      apiClient.get<ClaimsResponse>(`/api/v1/claims/status/${status}?${queryString}`)
    );
  }

  /**
   * Get claim statistics
   */
  static async getClaimStats(): Promise<{
    total_claims: number;
    by_status: Record<ClaimStatus, number>;
    recent_claims: Claim[];
  }> {
    return apiRequest(() => 
      apiClient.get('/api/v1/claims/stats')
    );
  }
}

/**
 * OCR Agent Service Class
 */
export class OCRService {
  
  /**
   * Process document with OCR for a claim
   */
  static async processDocument(claimId: string, file: File): Promise<{
    processing_status: string;
    claim_status: ClaimStatus;
    confidence_score: number;
    requires_human_review: boolean;
    extracted_data: Record<string, any>;
  }> {
    const formData = new FormData();
    formData.append('file', file);

    return apiRequest(() => 
      apiClient.post(`/api/v1/agents/ocr/process/${claimId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    );
  }

  /**
   * Get OCR processing status for a claim
   */
  static async getOCRStatus(claimId: string): Promise<AgentStatus> {
    return apiRequest(() => 
      apiClient.get<AgentStatus>(`/api/v1/agents/ocr/status/${claimId}`)
    );
  }

  /**
   * List documents associated with a claim
   */
  static async getClaimDocuments(claimId: string): Promise<{
    claim_id: string;
    document_count: number;
    documents: Array<{
      name: string;
      filename: string;
      size: number;
      content_type: string;
      created: string;
      gcs_uri: string;
    }>;
  }> {
    return apiRequest(() => 
      apiClient.get(`/api/v1/agents/ocr/documents/${claimId}`)
    );
  }

  /**
   * Delete a specific document from a claim
   */
  static async deleteClaimDocument(claimId: string, filename: string): Promise<void> {
    return apiRequest(() => 
      apiClient.delete(`/api/v1/agents/ocr/documents/${claimId}/${filename}`)
    );
  }

  /**
   * Reprocess a claim with existing documents
   */
  static async reprocessClaim(claimId: string): Promise<{
    reprocessing_status: string;
    new_confidence_score: number;
    requires_human_review: boolean;
    extracted_data: Record<string, any>;
  }> {
    return apiRequest(() => 
      apiClient.post(`/api/v1/agents/ocr/reprocess/${claimId}`)
    );
  }
}

/**
 * Health Check Service
 */
export class HealthService {
  
  /**
   * Check API health status
   */
  static async getHealthStatus(): Promise<{
    status: string;
    timestamp: string;
    version: string;
  }> {
    return apiRequest(() => 
      apiClient.get('/health')
    );
  }
}

// Export individual service methods for convenience
export const claimsApi = {
  getClaims: ClaimsService.getClaims,
  getClaimById: ClaimsService.getClaimById,
  createClaim: ClaimsService.createClaim,
  updateClaim: ClaimsService.updateClaim,
  deleteClaim: ClaimsService.deleteClaim,
  getClaimsByStatus: ClaimsService.getClaimsByStatus,
  getClaimStats: ClaimsService.getClaimStats,
};

export const ocrApi = {
  processDocument: OCRService.processDocument,
  getOCRStatus: OCRService.getOCRStatus,
  getClaimDocuments: OCRService.getClaimDocuments,
  deleteClaimDocument: OCRService.deleteClaimDocument,
  reprocessClaim: OCRService.reprocessClaim,
};

export const healthApi = {
  getHealthStatus: HealthService.getHealthStatus,
};

export default {
  claims: claimsApi,
  ocr: ocrApi,
  health: healthApi,
};