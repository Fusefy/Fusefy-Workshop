/**
 * Claim Detail Page Component
 * 
 * Displays detailed view of a single claim with actions
 * and OCR processing information.
 */

import { useParams, useNavigate, Link } from 'react-router-dom';
import { useClaim, useOCRStatus, useProcessDocument } from '@/hooks/useClaims';
import { formatCurrency, formatDateTime, getStatusConfig, getConfidenceColor, formatConfidence } from '@/utils';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export function ClaimDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const { data: claim, isLoading, error } = useClaim(id!);
  const { data: ocrStatus } = useOCRStatus(id!, { 
    enabled: !!id,
    refetchInterval: claim?.status === 'OCR_PROCESSING' ? 5000 : undefined,
  });
  
  const processDocumentMutation = useProcessDocument();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-96">
        <LoadingSpinner text="Loading claim details..." />
      </div>
    );
  }

  if (error || !claim) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          {error ? 'Error loading claim' : 'Claim not found'}
        </div>
        <button 
          onClick={() => navigate('/dashboard')} 
          className="btn btn-primary"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  const statusConfig = getStatusConfig(claim.status);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <nav className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
            <Link to="/dashboard" className="hover:text-gray-700">
              Dashboard
            </Link>
            <span>/</span>
            <span>Claim Details</span>
          </nav>
          <h1 className="text-2xl font-bold text-gray-900">
            Claim {claim.claim_number}
          </h1>
          <div className="mt-2 flex items-center space-x-4">
            <span className={`status-badge ${statusConfig.color}`}>
              {statusConfig.label}
            </span>
            {claim.requires_human_review && (
              <span className="status-badge bg-orange-100 text-orange-800">
                Needs Review
              </span>
            )}
          </div>
        </div>
        
        <div className="mt-4 sm:mt-0 flex gap-3">
          <Link
            to={`/claims/${claim.id}/edit`}
            className="btn btn-secondary"
          >
            Edit Claim
          </Link>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn btn-ghost"
          >
            Back to Dashboard
          </button>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Claim Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
            
            <dl className="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Claim Number</dt>
                <dd className="mt-1 text-sm text-gray-900 font-mono">{claim.claim_number}</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Policy Number</dt>
                <dd className="mt-1 text-sm text-gray-900">{claim.policy_number}</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Patient Name</dt>
                <dd className="mt-1 text-sm text-gray-900">{claim.patient_name}</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Claim Type</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {claim.claim_type.charAt(0) + claim.claim_type.slice(1).toLowerCase()}
                </dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Date of Service</dt>
                <dd className="mt-1 text-sm text-gray-900">{formatDateTime(claim.date_of_service)}</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Claim Amount</dt>
                <dd className="mt-1 text-lg font-semibold text-gray-900">
                  {formatCurrency(claim.claim_amount)}
                </dd>
              </div>
              
              {claim.provider_name && (
                <div className="sm:col-span-2">
                  <dt className="text-sm font-medium text-gray-500">Provider</dt>
                  <dd className="mt-1 text-sm text-gray-900">{claim.provider_name}</dd>
                </div>
              )}
            </dl>
          </div>

          {/* Medical Codes */}
          {(claim.diagnosis_codes?.length || claim.procedure_codes?.length) && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Medical Codes</h2>
              
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {claim.diagnosis_codes?.length && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500 mb-2">Diagnosis Codes</dt>
                    <dd className="flex flex-wrap gap-2">
                      {claim.diagnosis_codes.map((code, index) => (
                        <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {code}
                        </span>
                      ))}
                    </dd>
                  </div>
                )}
                
                {claim.procedure_codes?.length && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500 mb-2">Procedure Codes</dt>
                    <dd className="flex flex-wrap gap-2">
                      {claim.procedure_codes.map((code, index) => (
                        <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          {code}
                        </span>
                      ))}
                    </dd>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* OCR Information */}
          {claim.ocr_processed_at && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">OCR Processing</h2>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-500">Processing Status</span>
                  <span className="text-sm text-green-600">✓ Completed</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-500">Processed At</span>
                  <span className="text-sm text-gray-900">{formatDateTime(claim.ocr_processed_at)}</span>
                </div>
                
                {claim.ocr_confidence_score && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-500">Confidence Score</span>
                    <span className={`text-sm font-medium ${getConfidenceColor(claim.ocr_confidence_score)}`}>
                      {formatConfidence(claim.ocr_confidence_score)}
                    </span>
                  </div>
                )}
                
                {claim.requires_human_review !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-500">Human Review Required</span>
                    <span className={`text-sm font-medium ${claim.requires_human_review ? 'text-orange-600' : 'text-green-600'}`}>
                      {claim.requires_human_review ? 'Yes' : 'No'}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Actions & Status */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions</h2>
            
            <div className="space-y-3">
              <button
                className="btn btn-primary w-full"
                disabled={processDocumentMutation.isPending}
              >
                {processDocumentMutation.isPending ? 'Processing...' : 'Process with OCR'}
              </button>
              
              <Link
                to={`/claims/${claim.id}/edit`}
                className="btn btn-secondary w-full text-center"
              >
                Edit Claim
              </Link>
              
              <button className="btn btn-ghost w-full">
                Download Report
              </button>
              
              <button className="btn btn-danger w-full">
                Delete Claim
              </button>
            </div>
          </div>

          {/* Metadata */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Metadata</h2>
            
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Created</dt>
                <dd className="mt-1 text-sm text-gray-900">{formatDateTime(claim.created_at)}</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                <dd className="mt-1 text-sm text-gray-900">{formatDateTime(claim.updated_at)}</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Claim ID</dt>
                <dd className="mt-1 text-xs text-gray-600 font-mono break-all">{claim.id}</dd>
              </div>
            </dl>
          </div>

          {/* Document Status */}
          {claim.document_url && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Documents</h2>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Document attached</span>
                  <span className="text-sm text-green-600">✓</span>
                </div>
                
                <button className="btn btn-secondary w-full text-sm">
                  View Document
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ClaimDetail;