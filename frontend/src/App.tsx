/**
 * Main App Component
 * 
 * Root component that handles routing and global layout
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import { Suspense, lazy } from 'react';

import Layout from '@/components/layout/Layout';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

// Lazy load page components for code splitting
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const CreateClaim = lazy(() => import('@/pages/CreateClaim'));
const ClaimDetail = lazy(() => import('@/pages/ClaimDetail'));
const EditClaim = lazy(() => import('@/pages/EditClaim'));
const NotFound = lazy(() => import('@/pages/NotFound'));

function App() {
  return (
    <Layout>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          {/* Default redirect to dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          {/* Main application routes */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/claims/new" element={<CreateClaim />} />
          <Route path="/claims/:id" element={<ClaimDetail />} />
          <Route path="/claims/:id/edit" element={<EditClaim />} />
          
          {/* 404 page */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </Layout>
  );
}

export default App;