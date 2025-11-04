import React, { useState, useEffect } from 'react';
import { Module } from '../types'; // Import Module type

interface HistoryListProps {
  onSelectHistory: (moduleId: string) => void;
  modules: Module[]; // Add modules prop
}

const HistoryList: React.FC<HistoryListProps> = ({ onSelectHistory, modules }) => {
  const [historyModuleIds, setHistoryModuleIds] = useState<string[]>([]);

  useEffect(() => {
    const keys = Object.keys(localStorage);
    const chatHistoryKeys = keys.filter(key => key.startsWith('chatHistory_'));
    const moduleIds = chatHistoryKeys.map(key => key.replace('chatHistory_', ''));
    setHistoryModuleIds(moduleIds);
  }, []); // Runs once on mount

  // Optional: Add a refresh mechanism if localStorage changes often from other tabs,
  // or a prop to trigger refresh if needed. For now, it loads on mount.

  if (historyModuleIds.length === 0) {
    return (
      <div className="mt-6">
        <h4 className="text-sm font-semibold text-gray-700 mb-2 px-2">Chat Histories</h4>
        <p className="text-sm text-gray-500 px-2">No chat history found.</p>
      </div>
    );
  }

  return (
    <div className="mt-6">
      <h4 className="text-sm font-semibold text-gray-700 mb-2 px-2">Chat Histories</h4>
      <ul className="space-y-1">
        {historyModuleIds.map(moduleId => {
          const module = modules.find(m => m.id === moduleId);
          const displayName = module ? module.name : moduleId; // Get module name
          return (
            <li key={moduleId}>
              <button
                onClick={() => onSelectHistory(moduleId)}
                className="w-full text-left px-2 py-1.5 text-sm text-gray-600 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {displayName} {/* Display module name */}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default HistoryList;
