/**
 * Edit Claim Page Component
 * 
 * Form for editing existing claims with pre-populated data.
 */

import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useEffect } from 'react';
import toast from 'react-hot-toast';

import { useClaim, useUpdateClaim } from '@/hooks/useClaims';
import { ClaimUpdate, ClaimType } from '@/types';
import Input from '@/components/ui/Input';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

// Validation schema (similar to create but all fields optional)
const editClaimSchema = z.object({
  claim_number: z.string()
    .min(1, 'Claim number is required')
    .regex(/^CLM[A-Z0-9]{6,}$/, 'Invalid claim number format')
    .optional(),
  policy_number: z.string()
    .min(1, 'Policy number is required')
    .min(5, 'Policy number must be at least 5 characters')
    .optional(),
  patient_name: z.string()
    .min(1, 'Patient name is required')
    .min(2, 'Patient name must be at least 2 characters')
    .max(100, 'Patient name is too long')
    .optional(),
  date_of_service: z.string()
    .min(1, 'Date of service is required')
    .refine((date) => !isNaN(Date.parse(date)), 'Invalid date format')
    .optional(),
  claim_amount: z.number()
    .positive('Claim amount must be positive')
    .min(0.01, 'Claim amount must be at least $0.01')
    .max(1000000, 'Claim amount is too large')
    .optional(),
  claim_type: z.nativeEnum(ClaimType).optional(),
  provider_name: z.string().optional(),
  diagnosis_codes: z.array(z.string()).optional(),
  procedure_codes: z.array(z.string()).optional(),
});

export function EditClaim() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const { data: claim, isLoading, error } = useClaim(id!);
  const updateMutation = useUpdateClaim(id!);

  const form = useForm<ClaimUpdate>({
    resolver: zodResolver(editClaimSchema),
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isDirty },
    reset,
    watch,
  } = form;

  // Populate form when claim data loads
  useEffect(() => {
    if (claim) {
      reset({
        claim_number: claim.claim_number,
        policy_number: claim.policy_number,
        patient_name: claim.patient_name,
        date_of_service: claim.date_of_service.split('T')[0], // Format for date input
        claim_amount: claim.claim_amount,
        claim_type: claim.claim_type,
        provider_name: claim.provider_name || '',
        diagnosis_codes: claim.diagnosis_codes || [],
        procedure_codes: claim.procedure_codes || [],
      });
    }
  }, [claim, reset]);

  const watchClaimType = watch('claim_type');

  const onSubmit = async (data: ClaimUpdate) => {
    try {
      await updateMutation.mutateAsync(data);
      toast.success('Claim updated successfully!');
      navigate(`/claims/${id}`);
    } catch (error) {
      console.error('Failed to update claim:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-96">
        <LoadingSpinner text="Loading claim..." />
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

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Edit Claim</h1>
        <p className="mt-1 text-sm text-gray-600">
          Update the claim details for {claim.claim_number}
        </p>
      </div>

      {/* Form */}
      <div className="card p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Claim Number - readonly since it shouldn't change */}
          <Input
            id="claim_number"
            label="Claim Number"
            {...register('claim_number')}
            error={errors.claim_number?.message}
            readOnly
          />

          {/* Policy Number */}
          <Input
            id="policy_number"
            label="Policy Number"
            placeholder="Enter policy number"
            {...register('policy_number')}
            error={errors.policy_number?.message}
          />

          {/* Patient Name */}
          <Input
            id="patient_name"
            label="Patient Name"
            placeholder="Enter patient full name"
            {...register('patient_name')}
            error={errors.patient_name?.message}
          />

          {/* Date of Service and Claim Type */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <Input
              id="date_of_service"
              label="Date of Service"
              type="date"
              {...register('date_of_service')}
              error={errors.date_of_service?.message}
            />

            <div>
              <label htmlFor="claim_type" className="block text-sm font-medium text-gray-700 mb-1">
                Claim Type
              </label>
              <select
                id="claim_type"
                {...register('claim_type')}
                className={`input ${errors.claim_type ? 'input-error' : ''}`}
              >
                {Object.values(ClaimType).map((type) => (
                  <option key={type} value={type}>
                    {type.charAt(0) + type.slice(1).toLowerCase()}
                  </option>
                ))}
              </select>
              {errors.claim_type && (
                <p className="text-sm text-red-600 mt-1">{errors.claim_type.message}</p>
              )}
            </div>
          </div>

          {/* Claim Amount */}
          <div>
            <label htmlFor="claim_amount" className="block text-sm font-medium text-gray-700 mb-1">
              Claim Amount
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <span className="text-gray-500 sm:text-sm">$</span>
              </div>
              <input
                id="claim_amount"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                {...register('claim_amount', { valueAsNumber: true })}
                className={`input pl-7 ${errors.claim_amount ? 'input-error' : ''}`}
              />
            </div>
            {errors.claim_amount && (
              <p className="text-sm text-red-600 mt-1">{errors.claim_amount.message}</p>
            )}
          </div>

          {/* Provider Name */}
          <Input
            id="provider_name"
            label="Provider Name"
            placeholder="Enter healthcare provider name"
            {...register('provider_name')}
            error={errors.provider_name?.message}
          />

          {/* Medical Details for Medical claims */}
          {watchClaimType === ClaimType.MEDICAL && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Medical Details</h3>
              
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <Input
                  id="diagnosis_codes"
                  label="Diagnosis Codes"
                  placeholder="e.g., M54.5, Z00.00"
                  {...register('diagnosis_codes.0')}
                />

                <Input
                  id="procedure_codes"
                  label="Procedure Codes"
                  placeholder="e.g., 99213, 73060"
                  {...register('procedure_codes.0')}
                />
              </div>
            </div>
          )}

          {/* Form Actions */}
          <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t">
            <button
              type="submit"
              disabled={isSubmitting || !isDirty}
              className="btn btn-primary flex-1 sm:flex-none"
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
            
            <button
              type="button"
              onClick={() => navigate(`/claims/${id}`)}
              className="btn btn-secondary flex-1 sm:flex-none"
            >
              Cancel
            </button>
          </div>

          {/* Unsaved changes warning */}
          {isDirty && (
            <div className="card p-4 bg-yellow-50 border-yellow-200">
              <p className="text-sm text-yellow-800">
                ⚠️ You have unsaved changes. Make sure to save before leaving this page.
              </p>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}

export default EditClaim;