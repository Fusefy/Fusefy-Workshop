/**
 * Dashboard Page Component
 * 
 * Main dashboard showing claims list with filtering, pagination,
 * and quick actions.
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useClaims, usePrefetchClaim } from '@/hooks/useClaims';
import { formatCurrency, formatDate, getStatusConfig } from '@/utils';
import { ClaimStatus, ClaimFilters } from '@/types';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export function Dashboard() {
  const [filters, setFilters] = useState<ClaimFilters>({
    skip: 0,
    limit: 20,
    status: undefined,
    search: '',
  });

  const { data, isLoading, error } = useClaims(filters);
  const prefetchClaim = usePrefetchClaim();

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    ...Object.values(ClaimStatus).map(status => ({
      value: status,
      label: getStatusConfig(status).label,
    })),
  ];

  // Handle filter changes
  const handleStatusFilter = (status: string) => {
    setFilters(prev => ({
      ...prev,
      status: (status as ClaimStatus) || undefined,
      skip: 0, // Reset pagination
    }));
  };

  const handleSearch = (search: string) => {
    setFilters(prev => ({
      ...prev,
      search,
      skip: 0, // Reset pagination
    }));
  };

  const handlePageChange = (newSkip: number) => {
    setFilters(prev => ({
      ...prev,
      skip: newSkip,
    }));
  };

  // Pagination calculations
  const totalPages = data ? Math.ceil(data.total / filters.limit!) : 0;
  const currentPage = Math.floor((filters.skip || 0) / (filters.limit || 20)) + 1;

  if (isLoading && !data) {
    return (
      <div className="flex justify-center items-center min-h-96">
        <LoadingSpinner text="Loading claims..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">Error loading claims</div>
        <button 
          onClick={() => window.location.reload()} 
          className="btn btn-primary"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Claims Dashboard</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage and track your insurance claims
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Link
            to="/claims/new"
            className="btn btn-primary"
          >
            Create New Claim
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total Claims</p>
              <p className="text-2xl font-bold text-gray-900">
                {data?.total || 0}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Processing</p>
              <p className="text-2xl font-bold text-yellow-600">
                {(data?.items || []).filter(c => 
                  [ClaimStatus.OCR_PROCESSING, ClaimStatus.HUMAN_REVIEW].includes(c.status)
                ).length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Settled</p>
              <p className="text-2xl font-bold text-green-600">
                {(data?.items || []).filter(c => c.status === ClaimStatus.SETTLED).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
              Search Claims
            </label>
            <input
              id="search"
              type="text"
              placeholder="Search by claim number or patient name..."
              value={filters.search || ''}
              onChange={(e) => handleSearch(e.target.value)}
              className="input"
            />
          </div>
          
          <div className="sm:w-48">
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
              Status Filter
            </label>
            <select
              id="status"
              value={filters.status || ''}
              onChange={(e) => handleStatusFilter(e.target.value)}
              className="input"
            >
              {statusOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Claims Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Claim
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Patient
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {(data?.items || []).map((claim) => {
                const statusConfig = getStatusConfig(claim.status);
                
                return (
                  <tr 
                    key={claim.id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onMouseEnter={() => prefetchClaim(claim.id)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {claim.claim_number}
                        </div>
                        <div className="text-sm text-gray-500">
                          {claim.policy_number}
                        </div>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {claim.patient_name}
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {formatCurrency(claim.claim_amount)}
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`status-badge ${statusConfig.color}`}>
                        {statusConfig.label}
                      </span>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(claim.created_at)}
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <Link
                        to={`/claims/${claim.id}`}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Empty state */}
        {(data?.items || []).length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500 mb-4">No claims found</div>
            <Link to="/claims/new" className="btn btn-primary">
              Create Your First Claim
            </Link>
          </div>
        )}

        {/* Pagination */}
        {data && data.total > filters.limit! && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => handlePageChange(Math.max(0, (filters.skip || 0) - filters.limit!))}
                disabled={filters.skip === 0}
                className="btn btn-secondary disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => handlePageChange((filters.skip || 0) + filters.limit!)}
                disabled={!data.has_more}
                className="btn btn-secondary disabled:opacity-50"
              >
                Next
              </button>
            </div>
            
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Showing{' '}
                  <span className="font-medium">{(filters.skip || 0) + 1}</span>
                  {' '}to{' '}
                  <span className="font-medium">
                    {Math.min((filters.skip || 0) + filters.limit!, data.total)}
                  </span>
                  {' '}of{' '}
                  <span className="font-medium">{data.total}</span>
                  {' '}results
                </p>
              </div>
              
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                  <button
                    onClick={() => handlePageChange(Math.max(0, (filters.skip || 0) - filters.limit!))}
                    disabled={filters.skip === 0}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  
                  {/* Page numbers */}
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const pageNumber = Math.max(1, currentPage - 2) + i;
                    if (pageNumber > totalPages) return null;
                    
                    return (
                      <button
                        key={pageNumber}
                        onClick={() => handlePageChange((pageNumber - 1) * filters.limit!)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                          pageNumber === currentPage
                            ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
                            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        {pageNumber}
                      </button>
                    );
                  })}
                  
                  <button
                    onClick={() => handlePageChange((filters.skip || 0) + filters.limit!)}
                    disabled={!data.has_more}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;