/**
 * React Query Hooks for Claims Management
 * 
 * Custom hooks for data fetching, caching, and state management
 * using TanStack Query (React Query).
 */

import { 
  useQuery, 
  useMutation, 
  useQueryClient,
  UseQueryResult,
  UseMutationResult,
} from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { claimsApi, ocrApi } from '@/services/claims';
import type { 
  Claim, 
  ClaimsResponse, 
  ClaimCreate, 
  ClaimUpdate, 
  ClaimFilters,
  AgentStatus,
  QUERY_KEYS
} from '@/types';

/**
 * Query key factory for consistent cache keys
 */
export const queryKeys = {
  all: ['claims'] as const,
  lists: () => [...queryKeys.all, 'list'] as const,
  list: (filters: ClaimFilters) => [...queryKeys.lists(), filters] as const,
  details: () => [...queryKeys.all, 'detail'] as const,
  detail: (id: string) => [...queryKeys.details(), id] as const,
  stats: () => [...queryKeys.all, 'stats'] as const,
  ocr: {
    all: ['ocr'] as const,
    status: (id: string) => [...queryKeys.ocr.all, 'status', id] as const,
    documents: (id: string) => [...queryKeys.ocr.all, 'documents', id] as const,
  },
};

/**
 * Hook to fetch paginated claims list
 */
export function useClaims(
  filters: ClaimFilters = {},
  options?: { enabled?: boolean }
): UseQueryResult<ClaimsResponse, Error> {
  return useQuery({
    queryKey: queryKeys.list(filters),
    queryFn: () => claimsApi.getClaims(filters),
    enabled: options?.enabled !== false,
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 10, // 10 minutes (formerly cacheTime)
    refetchOnWindowFocus: true,
    retry: (failureCount, error: any) => {
      // Don't retry on 4xx errors
      if (error?.response?.status >= 400 && error?.response?.status < 500) {
        return false;
      }
      return failureCount < 3;
    },
  });
}

/**
 * Hook to fetch a single claim by ID
 */
export function useClaim(
  id: string,
  options?: { enabled?: boolean }
): UseQueryResult<Claim, Error> {
  return useQuery({
    queryKey: queryKeys.detail(id),
    queryFn: () => claimsApi.getClaimById(id),
    enabled: !!id && options?.enabled !== false,
    staleTime: 1000 * 60 * 2, // 2 minutes
    gcTime: 1000 * 60 * 5, // 5 minutes
    retry: (failureCount, error: any) => {
      // Don't retry on 404s
      if (error?.response?.status === 404) {
        return false;
      }
      return failureCount < 2;
    },
  });
}

/**
 * Hook to fetch claim statistics
 */
export function useClaimStats(): UseQueryResult<{
  total_claims: number;
  by_status: Record<string, number>;
  recent_claims: Claim[];
}, Error> {
  return useQuery({
    queryKey: queryKeys.stats(),
    queryFn: () => claimsApi.getClaimStats(),
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
    retry: 2,
  });
}

/**
 * Hook to create a new claim
 */
export function useCreateClaim(): UseMutationResult<
  Claim,
  Error,
  ClaimCreate,
  unknown
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (claimData: ClaimCreate) => claimsApi.createClaim(claimData),
    onSuccess: (newClaim) => {
      // Invalidate and refetch claims list
      queryClient.invalidateQueries({ queryKey: queryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: queryKeys.stats() });
      
      // Add the new claim to the cache
      queryClient.setQueryData(queryKeys.detail(newClaim.id), newClaim);
      
      toast.success('Claim created successfully!');
    },
    onError: (error: Error) => {
      console.error('Create claim error:', error);
      toast.error('Failed to create claim. Please try again.');
    },
  });
}

/**
 * Hook to update an existing claim
 */
export function useUpdateClaim(id: string): UseMutationResult<
  Claim,
  Error,
  ClaimUpdate,
  unknown
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (claimData: ClaimUpdate) => claimsApi.updateClaim(id, claimData),
    onSuccess: (updatedClaim) => {
      // Update the claim in cache
      queryClient.setQueryData(queryKeys.detail(id), updatedClaim);
      
      // Invalidate lists to ensure consistency
      queryClient.invalidateQueries({ queryKey: queryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: queryKeys.stats() });
      
      toast.success('Claim updated successfully!');
    },
    onError: (error: Error) => {
      console.error('Update claim error:', error);
      toast.error('Failed to update claim. Please try again.');
    },
  });
}

/**
 * Hook to delete a claim
 */
export function useDeleteClaim(): UseMutationResult<
  void,
  Error,
  string,
  unknown
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => claimsApi.deleteClaim(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: queryKeys.detail(deletedId) });
      
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: queryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: queryKeys.stats() });
      
      toast.success('Claim deleted successfully!');
    },
    onError: (error: Error) => {
      console.error('Delete claim error:', error);
      toast.error('Failed to delete claim. Please try again.');
    },
  });
}

/**
 * Hook to get OCR processing status
 */
export function useOCRStatus(
  claimId: string,
  options?: { enabled?: boolean; refetchInterval?: number }
): UseQueryResult<AgentStatus, Error> {
  return useQuery({
    queryKey: queryKeys.ocr.status(claimId),
    queryFn: () => ocrApi.getOCRStatus(claimId),
    enabled: !!claimId && options?.enabled !== false,
    refetchInterval: options?.refetchInterval || false,
    staleTime: 1000 * 30, // 30 seconds
    retry: 1,
  });
}

/**
 * Hook to process document with OCR
 */
export function useProcessDocument(): UseMutationResult<
  {
    processing_status: string;
    claim_status: string;
    confidence_score: number;
    requires_human_review: boolean;
    extracted_data: Record<string, any>;
  },
  Error,
  { claimId: string; file: File },
  unknown
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ claimId, file }) => ocrApi.processDocument(claimId, file),
    onSuccess: (result, { claimId }) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: queryKeys.detail(claimId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.ocr.status(claimId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.lists() });
      
      toast.success('Document processed successfully!');
    },
    onError: (error: Error) => {
      console.error('OCR processing error:', error);
      toast.error('Failed to process document. Please try again.');
    },
  });
}

/**
 * Hook to get claim documents
 */
export function useClaimDocuments(
  claimId: string,
  options?: { enabled?: boolean }
): UseQueryResult<{
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
}, Error> {
  return useQuery({
    queryKey: queryKeys.ocr.documents(claimId),
    queryFn: () => ocrApi.getClaimDocuments(claimId),
    enabled: !!claimId && options?.enabled !== false,
    staleTime: 1000 * 60 * 2, // 2 minutes
    retry: 1,
  });
}

/**
 * Hook to reprocess a claim
 */
export function useReprocessClaim(): UseMutationResult<
  {
    reprocessing_status: string;
    new_confidence_score: number;
    requires_human_review: boolean;
    extracted_data: Record<string, any>;
  },
  Error,
  string,
  unknown
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (claimId: string) => ocrApi.reprocessClaim(claimId),
    onSuccess: (_, claimId) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: queryKeys.detail(claimId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.ocr.status(claimId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.lists() });
      
      toast.success('Claim reprocessed successfully!');
    },
    onError: (error: Error) => {
      console.error('Reprocess claim error:', error);
      toast.error('Failed to reprocess claim. Please try again.');
    },
  });
}

/**
 * Hook to prefetch a claim (useful for hover states)
 */
export function usePrefetchClaim() {
  const queryClient = useQueryClient();

  return (id: string) => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.detail(id),
      queryFn: () => claimsApi.getClaimById(id),
      staleTime: 1000 * 60 * 2, // 2 minutes
    });
  };
}