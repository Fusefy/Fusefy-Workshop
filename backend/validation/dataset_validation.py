"""
Golden Dataset Validation for Claims Processing System
Validates data quality, drift, and consistency of the golden dataset
"""

import json
from datetime import datetime
import statistics
from typing import Dict, List, Any
import os
import re

class DatasetValidator:
    def __init__(self):
        self.dataset_name = "Golden Dataset - Claims Processing"
        self.version = "v1.0.0"
        self.validation_date = datetime.now().isoformat()
        
    def load_golden_dataset(self) -> List[Dict]:
        """Load the golden dataset from Dataset/golden_dataset.json"""
        dataset_path = "../Dataset/golden_dataset.json"
        
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Golden dataset not found at {dataset_path}")
            
        with open(dataset_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    def validate_schema(self, dataset: List[Dict]) -> Dict[str, Any]:
        """Validate dataset schema and structure"""
        issues = []
        
        required_fields = ['claim_document_id', 'raw_claim_record', 'masked_claim_record', 'token_mapping_table']
        
        for i, record in enumerate(dataset):
            for field in required_fields:
                if field not in record:
                    issues.append(f"Record {i}: Missing field '{field}'")
        
        return {
            "status": "PASS" if len(issues) == 0 else "FAIL",
            "issues_count": len(issues),
            "issues": issues[:5],  # Show first 5 issues only
            "coverage": 100 - (len(issues) / (len(dataset) * len(required_fields)) * 100)
        }
    
    def validate_data_quality(self, dataset: List[Dict]) -> Dict[str, Any]:
        """Validate data quality and formats"""
        issues = []
        
        for i, record in enumerate(dataset):
            # Check claim ID format
            claim_id = record.get('claim_document_id', '')
            if not re.match(r'^CD\d{9}$', claim_id):
                issues.append(f"Record {i}: Invalid claim ID format")
            
            raw_record = record.get('raw_claim_record', {})
            
            # Check patient ID format
            patient_id = raw_record.get('patient_details', {}).get('patient_id', '')
            if not re.match(r'^P\d{6}$', patient_id):
                issues.append(f"Record {i}: Invalid patient ID format")
            
            # Check confidence scores
            conf_score = raw_record.get('confidence_scores', {}).get('overall', 0)
            if conf_score < 85:
                issues.append(f"Record {i}: Low confidence score ({conf_score})")
            
            # Check amounts
            for j, line in enumerate(raw_record.get('invoice_lines', [])):
                amount = line.get('amount_claimed', 0)
                if amount <= 0:
                    issues.append(f"Record {i}, Line {j}: Invalid amount ({amount})")
        
        return {
            "status": "PASS" if len(issues) == 0 else "FAIL",
            "issues_count": len(issues),
            "issues": issues[:5],
            "quality_score": max(0, 100 - (len(issues) / len(dataset) * 10))
        }
    
    def validate_pii_masking(self, dataset: List[Dict]) -> Dict[str, Any]:
        """Validate PII masking in masked records"""
        issues = []
        
        for i, record in enumerate(dataset):
            masked_record = record.get('masked_claim_record', {})
            
            # Check sensitive fields are masked
            sensitive_checks = [
                ('patient_details.name', 'Confidential'),
                ('patient_details.date_of_birth', 'Confidential'),
                ('policy_number', 'Confidential')
            ]
            
            for field_path, expected in sensitive_checks:
                try:
                    current = masked_record
                    for part in field_path.split('.'):
                        current = current[part]
                    
                    if current != expected:
                        issues.append(f"Record {i}: Field {field_path} not properly masked")
                except (KeyError, TypeError):
                    issues.append(f"Record {i}: Missing field {field_path}")
        
        masking_rate = max(0, 100 - (len(issues) / (len(dataset) * 3) * 100))
        
        return {
            "status": "PASS" if masking_rate >= 95 else "FAIL",
            "masking_rate": round(masking_rate, 1),
            "issues_count": len(issues),
            "issues": issues[:5]
        }
    
    def validate_token_mapping(self, dataset: List[Dict]) -> Dict[str, Any]:
        """Validate token mapping consistency"""
        issues = []
        all_tokens = set()
        
        for i, record in enumerate(dataset):
            token_mapping = record.get('token_mapping_table', {})
            
            for field, token in token_mapping.items():
                # Check token format
                if not re.match(r'^TKN\d{7}$', token):
                    issues.append(f"Record {i}: Invalid token format for {field}")
                
                # Check uniqueness
                if token in all_tokens:
                    issues.append(f"Record {i}: Duplicate token {token}")
                else:
                    all_tokens.add(token)
        
        return {
            "status": "PASS" if len(issues) == 0 else "FAIL",
            "unique_tokens": len(all_tokens),
            "issues_count": len(issues),
            "issues": issues[:5]
        }
    
    def detect_anomalies(self, dataset: List[Dict]) -> Dict[str, Any]:
        """Detect statistical anomalies in amounts and confidence scores"""
        amounts = []
        confidence_scores = []
        anomalies = []
        
        for record in dataset:
            raw_record = record.get('raw_claim_record', {})
            
            # Collect amounts
            for line in raw_record.get('invoice_lines', []):
                amount = line.get('amount_claimed', 0)
                if amount > 0:
                    amounts.append(amount)
            
            # Collect confidence scores
            conf_score = raw_record.get('confidence_scores', {}).get('overall', 0)
            if conf_score > 0:
                confidence_scores.append(conf_score)
        
        # Simple anomaly detection using standard deviation
        if len(amounts) > 1:
            mean_amount = statistics.mean(amounts)
            stdev_amount = statistics.stdev(amounts)
            
            for amount in amounts:
                z_score = abs((amount - mean_amount) / stdev_amount) if stdev_amount > 0 else 0
                if z_score > 3:  # 3 standard deviations
                    anomalies.append(f"Amount anomaly: ${amount:,.2f}")
        
        return {
            "status": "PASS" if len(anomalies) == 0 else "WARNING",
            "anomalies_count": len(anomalies),
            "anomalies": anomalies[:3],
            "amount_range": f"${min(amounts):,.2f} - ${max(amounts):,.2f}" if amounts else "N/A"
        }
    
    def calculate_statistics(self, dataset: List[Dict]) -> Dict[str, Any]:
        """Calculate dataset statistics"""
        amounts = []
        confidence_scores = []
        document_types = {}
        
        for record in dataset:
            raw_record = record.get('raw_claim_record', {})
            
            # Collect amounts
            for line in raw_record.get('invoice_lines', []):
                amount = line.get('amount_claimed', 0)
                if amount > 0:
                    amounts.append(amount)
            
            # Collect confidence scores
            conf_score = raw_record.get('confidence_scores', {}).get('overall', 0)
            confidence_scores.append(conf_score)
            
            # Document types
            doc_type = raw_record.get('document_type', 'Unknown')
            document_types[doc_type] = document_types.get(doc_type, 0) + 1
        
        return {
            "total_records": len(dataset),
            "avg_amount": round(statistics.mean(amounts), 2) if amounts else 0,
            "avg_confidence": round(statistics.mean(confidence_scores), 1) if confidence_scores else 0,
            "document_types": document_types,
            "total_invoice_lines": sum(len(r.get('raw_claim_record', {}).get('invoice_lines', [])) for r in dataset)
        }
    
    def run_validation(self) -> Dict[str, Any]:
        """Run comprehensive dataset validation"""
        print("📂 Loading golden dataset...")
        dataset = self.load_golden_dataset()
        
        print("🔍 Running validation checks...")
        
        # Run all validation checks
        schema_results = self.validate_schema(dataset)
        quality_results = self.validate_data_quality(dataset)
        pii_results = self.validate_pii_masking(dataset)
        token_results = self.validate_token_mapping(dataset)
        anomaly_results = self.detect_anomalies(dataset)
        statistics_data = self.calculate_statistics(dataset)
        
        # Determine overall status
        failed_checks = [
            result for result in [schema_results, quality_results, pii_results, token_results]
            if result['status'] == 'FAIL'
        ]
        
        overall_status = "PASS" if len(failed_checks) == 0 else "FAIL"
        
        return {
            "validation_info": {
                "dataset_name": self.dataset_name,
                "version": self.version,
                "validation_date": self.validation_date,
                "overall_status": overall_status
            },
            "schema_validation": schema_results,
            "data_quality": quality_results,
            "pii_masking": pii_results,
            "token_mapping": token_results,
            "anomaly_detection": anomaly_results,
            "statistics": statistics_data,
            "summary": {
                "total_checks": 5,
                "passed_checks": len([r for r in [schema_results, quality_results, pii_results, token_results, anomaly_results] if r['status'] == 'PASS']),
                "failed_checks": len(failed_checks),
                "warning_checks": len([r for r in [anomaly_results] if r['status'] == 'WARNING'])
            }
        }
    
    def save_validation_results(self, results: Dict[str, Any]) -> str:
        """Save validation results to JSON file"""
        # Ensure validation_results directory exists
        os.makedirs("validation_results", exist_ok=True)
        
        # Save detailed results
        results_file = "validation_results/dataset_validation_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Validation results saved to: {results_file}")
        return results_file

def main():
    """Main execution function"""
    print("🚀 Starting Golden Dataset Validation...")
    print("=" * 60)
    
    try:
        # Initialize validator
        validator = DatasetValidator()
        
        # Run validation
        print("📋 Running comprehensive dataset validation...")
        results = validator.run_validation()
        
        # Save results
        print("💾 Saving validation results...")
        results_file = validator.save_validation_results(results)
        
        # Display summary
        print("\n" + "=" * 60)
        print("🎯 VALIDATION RESULTS SUMMARY")
        print("=" * 60)
        
        summary = results['summary']
        stats = results['statistics']
        
        print(f"Dataset: {results['validation_info']['dataset_name']}")
        print(f"Total Records: {stats['total_records']}")
        print(f"Total Invoice Lines: {stats['total_invoice_lines']}")
        print(f"Average Amount: ${stats['avg_amount']:,.2f}")
        print(f"Average Confidence: {stats['avg_confidence']}%")
        
        print(f"\nValidation Status: {results['validation_info']['overall_status']}")
        print(f"✅ Passed: {summary['passed_checks']}/{summary['total_checks']}")
        print(f"❌ Failed: {summary['failed_checks']}")
        print(f"⚠️ Warnings: {summary['warning_checks']}")
        
        # Show key issues if any
        if results['data_quality']['issues_count'] > 0:
            print(f"\n🔍 Data Quality Issues: {results['data_quality']['issues_count']}")
        if results['pii_masking']['masking_rate'] < 100:
            print(f"🔒 PII Masking Rate: {results['pii_masking']['masking_rate']}%")
        
        print("\n" + "=" * 60)
        status_msg = "✅ DATASET VALIDATION COMPLETED" if results['validation_info']['overall_status'] == 'PASS' else "⚠️ DATASET VALIDATION COMPLETED WITH ISSUES"
        print(status_msg)
        print("📁 Results available in validation_results/ directory")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())