import React from 'react';
import { signInWithGoogle } from '../services/auth.service';
import { Brain } from 'lucide-react';

const LoginPage: React.FC = () => {
  const handleGoogleLogin = async () => {
    try {
      await signInWithGoogle();
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-2xl shadow-lg w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl mb-4">
            <Brain className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            AI Assistant Hub
          </h1>
          <p className="text-gray-600 mt-2 text-center">
            Sign in to access HR Onboarding & Interview Scheduling Platform
          </p>
        </div>
        
        <button
          onClick={handleGoogleLogin}
          className="w-full flex items-center justify-center gap-3 bg-white border border-gray-300 rounded-lg px-6 py-3 text-gray-700 font-medium hover:bg-gray-50 transition-colors"
        >
          <img src="https://www.google.com/favicon.ico" alt="Google" className="w-5 h-5" />
          Continue with Google
        </button>
      </div>
    </div>
  );
};

export default LoginPage;
