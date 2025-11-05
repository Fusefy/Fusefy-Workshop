/**
 * Create Claim Page Component
 * 
 * Form for creating new claims with validation and error handling.
 */

import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';

import { useCreateClaim } from '@/hooks/useClaims';
import { ClaimCreate, ClaimType } from '@/types';
import { generateClaimNumber } from '@/utils';
import Input from '@/components/ui/Input';

// Validation schema
const claimSchema = z.object({
  claim_number: z.string()
    .min(1, 'Claim number is required')
    .regex(/^CLM[A-Z0-9]{6,}$/, 'Invalid claim number format'),
  policy_number: z.string()
    .min(1, 'Policy number is required')
    .min(5, 'Policy number must be at least 5 characters'),
  patient_name: z.string()
    .min(1, 'Patient name is required')
    .min(2, 'Patient name must be at least 2 characters')
    .max(100, 'Patient name is too long'),
  date_of_service: z.string()
    .min(1, 'Date of service is required')
    .refine((date) => !isNaN(Date.parse(date)), 'Invalid date format'),
  claim_amount: z.number()
    .positive('Claim amount must be positive')
    .min(0.01, 'Claim amount must be at least $0.01')
    .max(1000000, 'Claim amount is too large'),
  claim_type: z.nativeEnum(ClaimType, {
    errorMap: () => ({ message: 'Please select a claim type' })
  }),
  provider_name: z.string().optional(),
  diagnosis_codes: z.array(z.string()).optional(),
  procedure_codes: z.array(z.string()).optional(),
});

export function CreateClaim() {
  const navigate = useNavigate();
  const createMutation = useCreateClaim();

  const form = useForm<ClaimCreate>({
    resolver: zodResolver(claimSchema),
    defaultValues: {
      claim_number: generateClaimNumber(),
      policy_number: '',
      patient_name: '',
      date_of_service: '',
      claim_amount: 0,
      claim_type: ClaimType.MEDICAL,
      provider_name: '',
      diagnosis_codes: [],
      procedure_codes: [],
    },
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
    setValue,
  } = form;

  const watchClaimType = watch('claim_type');

  const onSubmit = async (data: ClaimCreate) => {
    try {
      const claim = await createMutation.mutateAsync(data);
      toast.success('Claim created successfully!');
      navigate(`/claims/${claim.id}`);
    } catch (error) {
      // Error is handled by the mutation hook
      console.error('Failed to create claim:', error);
    }
  };

  const handleGenerateNewClaimNumber = () => {
    setValue('claim_number', generateClaimNumber());
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Create New Claim</h1>
        <p className="mt-1 text-sm text-gray-600">
          Enter the claim details below to create a new insurance claim.
        </p>
      </div>

      {/* Form */}
      <div className="card p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Claim Number */}
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                id="claim_number"
                label="Claim Number"
                {...register('claim_number')}
                error={errors.claim_number?.message}
                required
                readOnly
              />
            </div>
            <div className="flex items-end">
              <button
                type="button"
                onClick={handleGenerateNewClaimNumber}
                className="btn btn-secondary"
              >
                Generate New
              </button>
            </div>
          </div>

          {/* Policy Number */}
          <Input
            id="policy_number"
            label="Policy Number"
            placeholder="Enter policy number"
            {...register('policy_number')}
            error={errors.policy_number?.message}
            required
          />

          {/* Patient Name */}
          <Input
            id="patient_name"
            label="Patient Name"
            placeholder="Enter patient full name"
            {...register('patient_name')}
            error={errors.patient_name?.message}
            required
          />

          {/* Date of Service and Claim Type */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <Input
              id="date_of_service"
              label="Date of Service"
              type="date"
              {...register('date_of_service')}
              error={errors.date_of_service?.message}
              required
            />

            <div>
              <label htmlFor="claim_type" className="block text-sm font-medium text-gray-700 mb-1">
                Claim Type <span className="text-red-500">*</span>
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
              Claim Amount <span className="text-red-500">*</span>
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
            label="Provider Name (Optional)"
            placeholder="Enter healthcare provider name"
            {...register('provider_name')}
            error={errors.provider_name?.message}
          />

          {/* Conditional fields based on claim type */}
          {watchClaimType === ClaimType.MEDICAL && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Medical Details</h3>
              
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <Input
                  id="diagnosis_codes"
                  label="Diagnosis Codes (Optional)"
                  placeholder="e.g., M54.5, Z00.00"
                  {...register('diagnosis_codes.0')}
                />

                <Input
                  id="procedure_codes"
                  label="Procedure Codes (Optional)"
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
              disabled={isSubmitting}
              className="btn btn-primary flex-1 sm:flex-none"
            >
              {isSubmitting ? 'Creating...' : 'Create Claim'}
            </button>
            
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="btn btn-secondary flex-1 sm:flex-none"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>

      {/* Help Text */}
      <div className="card p-4 bg-blue-50 border-blue-200">
        <div className="flex">
          <div className="flex-1">
            <h3 className="text-sm font-medium text-blue-800">Tips for creating claims</h3>
            <div className="mt-2 text-sm text-blue-700">
              <ul className="list-disc list-inside space-y-1">
                <li>Ensure all required fields are filled out accurately</li>
                <li>Double-check the claim number is unique</li>
                <li>Verify the date of service is correct</li>
                <li>Include diagnosis and procedure codes when available</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CreateClaim;