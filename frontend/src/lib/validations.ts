/**
 * Form Validation Schemas
 * 
 * Zod schemas for form validation across the application.
 */

import { z } from 'zod';
import { ClaimType } from '@/types';

// Base claim validation schema
export const claimValidationSchema = z.object({
  claim_number: z.string()
    .min(1, 'Claim number is required')
    .regex(/^CLM[A-Z0-9]{6,}$/, 'Claim number must start with CLM followed by 6+ alphanumeric characters'),
  
  policy_number: z.string()
    .min(1, 'Policy number is required')
    .min(5, 'Policy number must be at least 5 characters')
    .max(50, 'Policy number is too long'),
  
  patient_name: z.string()
    .min(1, 'Patient name is required')
    .min(2, 'Patient name must be at least 2 characters')
    .max(100, 'Patient name is too long')
    .regex(/^[a-zA-Z\s\-'\.]+$/, 'Patient name contains invalid characters'),
  
  date_of_service: z.string()
    .min(1, 'Date of service is required')
    .refine((date) => {
      const parsedDate = new Date(date);
      return !isNaN(parsedDate.getTime());
    }, 'Invalid date format')
    .refine((date) => {
      const parsedDate = new Date(date);
      const now = new Date();
      return parsedDate <= now;
    }, 'Date of service cannot be in the future'),
  
  claim_amount: z.number({
    required_error: 'Claim amount is required',
    invalid_type_error: 'Claim amount must be a number',
  })
    .positive('Claim amount must be positive')
    .min(0.01, 'Claim amount must be at least $0.01')
    .max(1000000, 'Claim amount cannot exceed $1,000,000')
    .refine((amount) => {
      // Ensure only 2 decimal places
      return Number(amount.toFixed(2)) === amount;
    }, 'Claim amount can have at most 2 decimal places'),
  
  claim_type: z.nativeEnum(ClaimType, {
    errorMap: () => ({ message: 'Please select a valid claim type' })
  }),
  
  provider_name: z.string()
    .max(200, 'Provider name is too long')
    .optional()
    .transform(val => val?.trim() || undefined),
  
  diagnosis_codes: z.array(z.string().min(1))
    .max(10, 'Too many diagnosis codes (max 10)')
    .optional(),
  
  procedure_codes: z.array(z.string().min(1))
    .max(10, 'Too many procedure codes (max 10)')
    .optional(),
});

// Schema for creating new claims
export const createClaimSchema = claimValidationSchema;

// Schema for updating claims (all fields optional except IDs)
export const updateClaimSchema = claimValidationSchema.partial().extend({
  id: z.string().uuid('Invalid claim ID'),
});

// Search and filter schema
export const claimFiltersSchema = z.object({
  search: z.string()
    .max(100, 'Search term is too long')
    .optional(),
  
  status: z.nativeEnum(ClaimType)
    .optional(),
  
  claim_type: z.nativeEnum(ClaimType)
    .optional(),
  
  date_from: z.string()
    .refine((date) => !date || !isNaN(Date.parse(date)), 'Invalid from date')
    .optional(),
  
  date_to: z.string()
    .refine((date) => !date || !isNaN(Date.parse(date)), 'Invalid to date')
    .optional(),
  
  skip: z.number()
    .min(0, 'Skip cannot be negative')
    .default(0),
  
  limit: z.number()
    .min(1, 'Limit must be at least 1')
    .max(100, 'Limit cannot exceed 100')
    .default(20),
}).refine((data) => {
  if (data.date_from && data.date_to) {
    return new Date(data.date_from) <= new Date(data.date_to);
  }
  return true;
}, {
  message: 'From date must be before or equal to to date',
  path: ['date_to'],
});

// File upload schema (for future OCR functionality)
export const fileUploadSchema = z.object({
  file: z.instanceof(File, { message: 'Please select a file' })
    .refine((file) => file.size <= 50 * 1024 * 1024, 'File size must be less than 50MB')
    .refine((file) => {
      const allowedTypes = [
        'application/pdf',
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/tiff',
        'image/tif',
      ];
      return allowedTypes.includes(file.type);
    }, 'File must be a PDF or image (JPEG, PNG, TIFF)'),
});

// User feedback schema (for contact forms, etc.)
export const feedbackSchema = z.object({
  name: z.string()
    .min(1, 'Name is required')
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name is too long'),
  
  email: z.string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  
  subject: z.string()
    .min(1, 'Subject is required')
    .max(200, 'Subject is too long'),
  
  message: z.string()
    .min(1, 'Message is required')
    .min(10, 'Message must be at least 10 characters')
    .max(2000, 'Message is too long'),
  
  priority: z.enum(['low', 'medium', 'high'])
    .default('medium'),
});

// Export types inferred from schemas
export type ClaimFormData = z.infer<typeof claimValidationSchema>;
export type CreateClaimFormData = z.infer<typeof createClaimSchema>;
export type UpdateClaimFormData = z.infer<typeof updateClaimSchema>;
export type ClaimFiltersData = z.infer<typeof claimFiltersSchema>;
export type FileUploadData = z.infer<typeof fileUploadSchema>;
export type FeedbackFormData = z.infer<typeof feedbackSchema>;

export default {
  claimValidationSchema,
  createClaimSchema,
  updateClaimSchema,
  claimFiltersSchema,
  fileUploadSchema,
  feedbackSchema,
};