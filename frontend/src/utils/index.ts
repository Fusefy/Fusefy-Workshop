/**
 * Utility functions for the Claims Management System
 */

import { format, parseISO, isValid, formatDistanceToNow } from 'date-fns';
import { ClaimStatus, StatusConfigMap } from '@/types';

/**
 * Status badge configuration with colors and labels
 */
export const statusConfig: StatusConfigMap = {
  [ClaimStatus.RECEIVED]: {
    label: 'Received',
    color: 'bg-blue-100 text-blue-800 border-blue-200',
    bgColor: 'bg-blue-500',
    textColor: 'text-blue-800',
  },
  [ClaimStatus.OCR_PROCESSING]: {
    label: 'Processing',
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    bgColor: 'bg-yellow-500',
    textColor: 'text-yellow-800',
  },
  [ClaimStatus.PII_MASKED]: {
    label: 'PII Masked',
    color: 'bg-purple-100 text-purple-800 border-purple-200',
    bgColor: 'bg-purple-500',
    textColor: 'text-purple-800',
  },
  [ClaimStatus.DQ_VALIDATED]: {
    label: 'DQ Validated',
    color: 'bg-cyan-100 text-cyan-800 border-cyan-200',
    bgColor: 'bg-cyan-500',
    textColor: 'text-cyan-800',
  },
  [ClaimStatus.HUMAN_REVIEW]: {
    label: 'Human Review',
    color: 'bg-orange-100 text-orange-800 border-orange-200',
    bgColor: 'bg-orange-500',
    textColor: 'text-orange-800',
  },
  [ClaimStatus.CONSENT_VERIFIED]: {
    label: 'Consent Verified',
    color: 'bg-indigo-100 text-indigo-800 border-indigo-200',
    bgColor: 'bg-indigo-500',
    textColor: 'text-indigo-800',
  },
  [ClaimStatus.CLAIM_VALIDATED]: {
    label: 'Validated',
    color: 'bg-green-100 text-green-800 border-green-200',
    bgColor: 'bg-green-500',
    textColor: 'text-green-800',
  },
  [ClaimStatus.PAYER_SUBMITTED]: {
    label: 'Submitted',
    color: 'bg-teal-100 text-teal-800 border-teal-200',
    bgColor: 'bg-teal-500',
    textColor: 'text-teal-800',
  },
  [ClaimStatus.SETTLED]: {
    label: 'Settled',
    color: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    bgColor: 'bg-emerald-500',
    textColor: 'text-emerald-800',
  },
  [ClaimStatus.REJECTED]: {
    label: 'Rejected',
    color: 'bg-red-100 text-red-800 border-red-200',
    bgColor: 'bg-red-500',
    textColor: 'text-red-800',
  },
};

/**
 * Get status configuration for a given claim status
 */
export function getStatusConfig(status: ClaimStatus) {
  return statusConfig[status] || statusConfig[ClaimStatus.RECEIVED];
}

/**
 * Format currency amount
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

/**
 * Format date string
 */
export function formatDate(dateString: string, formatStr = 'MMM dd, yyyy'): string {
  try {
    const date = parseISO(dateString);
    return isValid(date) ? format(date, formatStr) : 'Invalid Date';
  } catch {
    return 'Invalid Date';
  }
}

/**
 * Format date with time
 */
export function formatDateTime(dateString: string): string {
  return formatDate(dateString, 'MMM dd, yyyy hh:mm a');
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(dateString: string): string {
  try {
    const date = parseISO(dateString);
    return isValid(date) ? formatDistanceToNow(date, { addSuffix: true }) : 'Unknown';
  } catch {
    return 'Unknown';
  }
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * Generate initials from a name
 */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .map(part => part.charAt(0).toUpperCase())
    .slice(0, 2)
    .join('');
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Generate a random ID
 */
export function generateId(): string {
  return Math.random().toString(36).substr(2, 9);
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => void>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

/**
 * Deep merge objects
 */
export function deepMerge<T extends Record<string, any>>(
  target: T,
  source: Partial<T>
): T {
  const result = { ...target };
  
  for (const key in source) {
    const value = source[key];
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      (result as any)[key] = deepMerge((result as any)[key] || {}, value);
    } else {
      (result as any)[key] = value;
    }
  }
  
  return result;
}

/**
 * Convert file size to human readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
}

/**
 * Get file extension from filename
 */
export function getFileExtension(filename: string): string {
  return filename.split('.').pop()?.toLowerCase() || '';
}

/**
 * Check if file is an image
 */
export function isImageFile(filename: string): boolean {
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'];
  return imageExtensions.includes(getFileExtension(filename));
}

/**
 * Check if file is a PDF
 */
export function isPDFFile(filename: string): boolean {
  return getFileExtension(filename) === 'pdf';
}

/**
 * Generate a claim number
 */
export function generateClaimNumber(): string {
  const timestamp = Date.now().toString().slice(-6);
  const random = Math.random().toString(36).substr(2, 4).toUpperCase();
  return `CLM${timestamp}${random}`;
}

/**
 * Validate claim number format
 */
export function isValidClaimNumber(claimNumber: string): boolean {
  // CLM followed by 6+ alphanumeric characters
  const claimRegex = /^CLM[A-Z0-9]{6,}$/;
  return claimRegex.test(claimNumber);
}

/**
 * Sort array of objects by key
 */
export function sortBy<T>(
  array: T[],
  key: keyof T,
  direction: 'asc' | 'desc' = 'asc'
): T[] {
  return array.sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    
    if (aVal === bVal) return 0;
    
    const comparison = aVal < bVal ? -1 : 1;
    return direction === 'asc' ? comparison : -comparison;
  });
}

/**
 * Group array by key
 */
export function groupBy<T>(array: T[], key: keyof T): Record<string, T[]> {
  return array.reduce((groups, item) => {
    const group = String(item[key]);
    groups[group] = groups[group] || [];
    groups[group].push(item);
    return groups;
  }, {} as Record<string, T[]>);
}

/**
 * Calculate confidence color
 */
export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-green-600';
  if (confidence >= 0.6) return 'text-yellow-600';
  return 'text-red-600';
}

/**
 * Format confidence percentage
 */
export function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

/**
 * Check if value is empty
 */
export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim() === '';
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
}

/**
 * Safe JSON parse
 */
export function safeJsonParse<T>(json: string, fallback: T): T {
  try {
    return JSON.parse(json);
  } catch {
    return fallback;
  }
}

/**
 * Copy text to clipboard
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    const success = document.execCommand('copy');
    document.body.removeChild(textArea);
    return success;
  }
}