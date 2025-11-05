/**
 * Type definitions for the Claims Management System
 * 
 * These types match the backend FastAPI schemas and provide
 * type safety throughout the React application.
 */

// Enums matching backend
export enum ClaimStatus {
  RECEIVED = 'RECEIVED',
  OCR_PROCESSING = 'OCR_PROCESSING',
  PII_MASKED = 'PII_MASKED',
  DQ_VALIDATED = 'DQ_VALIDATED',
  HUMAN_REVIEW = 'HUMAN_REVIEW',
  CONSENT_VERIFIED = 'CONSENT_VERIFIED',
  CLAIM_VALIDATED = 'CLAIM_VALIDATED',
  PAYER_SUBMITTED = 'PAYER_SUBMITTED',
  SETTLED = 'SETTLED',
  REJECTED = 'REJECTED',
}

export enum ClaimType {
  MEDICAL = 'MEDICAL',
  DENTAL = 'DENTAL',
  VISION = 'VISION',
  PHARMACY = 'PHARMACY',
}

// Base claim interface
export interface Claim {
  id: string;
  claim_number: string;
  policy_number: string;
  patient_name: string;
  date_of_service: string; // ISO date string
  claim_amount: number;
  claim_type: ClaimType;
  status: ClaimStatus;
  provider_name?: string;
  diagnosis_codes?: string[];
  procedure_codes?: string[];
  document_url?: string;
  
  // OCR fields
  ocr_processed_at?: string; // ISO date string
  ocr_confidence_score?: number;
  requires_human_review?: boolean;
  
  // Timestamps
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  
  // Raw data for extensibility
  raw_data?: Record<string, any>;
}

// Form data for creating claims
export interface ClaimCreate {
  claim_number: string;
  policy_number: string;
  patient_name: string;
  date_of_service: string;
  claim_amount: number;
  claim_type: ClaimType;
  provider_name?: string;
  diagnosis_codes?: string[];
  procedure_codes?: string[];
}

// Form data for updating claims
export interface ClaimUpdate {
  claim_number?: string;
  policy_number?: string;
  patient_name?: string;
  date_of_service?: string;
  claim_amount?: number;
  claim_type?: ClaimType;
  status?: ClaimStatus;
  provider_name?: string;
  diagnosis_codes?: string[];
  procedure_codes?: string[];
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export interface ClaimsResponse extends PaginatedResponse<Claim> {}

// API Error types
export interface ApiError {
  detail: string;
  status_code: number;
  type?: string;
}

// Pagination parameters
export interface PaginationParams {
  skip?: number;
  limit?: number;
}

// Filter parameters
export interface ClaimFilters extends PaginationParams {
  status?: ClaimStatus;
  search?: string;
  date_from?: string;
  date_to?: string;
  claim_type?: ClaimType;
}

// Status badge configuration
export interface StatusBadgeConfig {
  label: string;
  color: string;
  bgColor: string;
  textColor: string;
}

export type StatusConfigMap = Record<ClaimStatus, StatusBadgeConfig>;

// Form validation schemas (for Zod)
export interface FormFieldError {
  message: string;
  type: string;
}

export interface FormErrors {
  [key: string]: FormFieldError;
}

// Component prop types
export interface TableColumn<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: any, item: T) => any;
  width?: string;
}

export interface TableProps<T> {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  error?: string | null;
  onSort?: (key: keyof T, direction: 'asc' | 'desc') => void;
  sortKey?: keyof T;
  sortDirection?: 'asc' | 'desc';
}

// Navigation and routing
export interface NavItem {
  label: string;
  href: string;
  icon?: any;
  active?: boolean;
}

// Toast notification types
export interface ToastOptions {
  title?: string;
  description?: string;
  variant?: 'default' | 'success' | 'error' | 'warning';
  duration?: number;
}

// Query keys for React Query
export const QUERY_KEYS = {
  CLAIMS: 'claims',
  CLAIM: 'claim',
  CLAIM_STATUS: 'claimStatus',
} as const;

// API endpoints
export const API_ENDPOINTS = {
  CLAIMS: '/api/v1/claims',
  CLAIM_BY_ID: (id: string) => `/api/v1/claims/${id}`,
  CLAIMS_BY_STATUS: (status: ClaimStatus) => `/api/v1/claims/status/${status}`,
  OCR_PROCESS: (id: string) => `/api/v1/agents/ocr/process/${id}`,
  OCR_STATUS: (id: string) => `/api/v1/agents/ocr/status/${id}`,
} as const;

// Environment configuration
export interface AppConfig {
  apiBaseUrl: string;
  environment: 'development' | 'staging' | 'production';
  enableDevTools: boolean;
}

// Loading states
export interface LoadingState {
  isLoading: boolean;
  error: string | null;
  data: any;
}

// Sort configuration
export interface SortConfig<T> {
  key: keyof T;
  direction: 'asc' | 'desc';
}

// File upload types (for future OCR functionality)
export interface FileUpload {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

// OCR processing result
export interface OCRResult {
  gcs_uri: string;
  extracted_text: string;
  structured_data: Record<string, any>;
  confidence_scores: Record<string, number>;
  overall_confidence: number;
  requires_human_review: boolean;
  ocr_metadata: Record<string, any>;
}

// Agent processing status
export interface AgentStatus {
  claim_id: string;
  ocr_processed: boolean;
  ocr_processed_at?: string;
  confidence_score?: number;
  requires_human_review?: boolean;
  extracted_data?: Record<string, any>;
}

export default {
  ClaimStatus,
  ClaimType,
  QUERY_KEYS,
  API_ENDPOINTS,
};