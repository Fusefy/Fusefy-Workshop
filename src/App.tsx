import React, { useState, useEffect } from 'react';
import { Message, Module } from './types'; // Agent removed
import { modules } from './data/modules';
import { generateMockResponse } from './data/mockResponses';
import ModuleSelector from './components/ModuleSelector';
import HistoryList from './components/HistoryList'; // Import HistoryList
// AgentSelector import removed
import ChatInterface from './components/ChatInterface';
import LoginPage from './components/LoginPage';
import LoadingSpinner from './components/LoadingSpinner';
import { Brain, Zap, LogOut } from 'lucide-react';
import { onAuthChange, logOut } from './services/auth.service';
import { User } from 'firebase/auth';

function App() {
  const [selectedModule, setSelectedModule] = useState<Module | null>(null);
  // selectedAgent state removed
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthChange((user) => {
      setUser(user);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // useEffect for selectedAgent removed

  const handleLogout = async () => {
    try {
      await logOut();
      setSelectedModule(null);
      // setSelectedAgent(null) removed;
      setMessages([]);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const handleSelectModule = (module: Module) => {
    setSelectedModule(module);
    // setSelectedAgent(null) removed;
    const storageKey = `chatHistory_${module.id}`;
    const storedMessages = localStorage.getItem(storageKey);
    if (storedMessages) {
      try {
        const parsedMessages = JSON.parse(storedMessages) as Message[];
        // Convert timestamp strings back to Date objects
        const messagesWithDateObjects = parsedMessages.map(msg => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }));
        setMessages(messagesWithDateObjects);
      } catch (error) {
        console.error("Failed to parse messages from localStorage:", error);
        setMessages([]);
      }
    } else {
      setMessages([]);
    }
  };

  // handleSelectAgent function removed

  // handleBackToModules function removed

  const handleSelectHistory = (moduleId: string) => {
    const moduleToSelect = modules.find(m => m.id === moduleId);
    if (moduleToSelect) {
      handleSelectModule(moduleToSelect); // This will also load messages
    } else {
      console.warn(`Module with ID ${moduleId} not found from history selection.`);
      // Optionally, clear selection or show an error
      // setSelectedModule(null);
      // setMessages([]);
    }
  };

  const handleSendMessage = (content: string) => {
    if (!selectedModule) return; // Changed from selectedAgent to selectedModule

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    // Save user message to localStorage
    if (selectedModule) {
      const storageKey = `chatHistory_${selectedModule.id}`;
      const currentMessagesRaw = localStorage.getItem(storageKey);
      const currentMessages: Message[] = currentMessagesRaw ? JSON.parse(currentMessagesRaw) : [];
      localStorage.setItem(storageKey, JSON.stringify([...currentMessages, userMessage]));
    }

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    // Simulate AI response delay
    setTimeout(() => {
      const agentResponse = generateMockResponse(selectedModule ? selectedModule.id : "general", content); // Changed from selectedAgent.id

      // Save agent response to localStorage
      if (selectedModule) {
        const storageKey = `chatHistory_${selectedModule.id}`;
        const currentMessagesRaw = localStorage.getItem(storageKey);
        // Ensure user message was saved, then add agent response
        const currentMessages: Message[] = currentMessagesRaw ? JSON.parse(currentMessagesRaw) : [userMessage];
        localStorage.setItem(storageKey, JSON.stringify([...currentMessages, agentResponse]));
      }

      setMessages(prev => [...prev, agentResponse]);
      setIsTyping(false);
    }, 1000 + Math.random() * 2000); // Random delay between 1-3 seconds
  };

  const getTotalAgents = () => {
    return modules.reduce((total, module) => total + module.agents.length, 0);
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return <LoginPage />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl">
                <Brain className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  AI Assistant Hub
                </h1>
                <p className="text-sm text-gray-600">
                  HR Onboarding & Interview Scheduling Platform
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-2 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                <Zap className="w-4 h-4" />
                <span>{getTotalAgents()} Agents Active</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <img 
                    src={user.photoURL || undefined}
                    alt={user.displayName || 'User'}
                    className="w-10 h-10 rounded-full"
                  />
                  <span className="text-sm font-medium text-gray-700">{user.displayName}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 text-gray-600 hover:text-gray-900 transition-colors"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="mx-auto px-6 py-8">
        <div className="flex h-[calc(80vh)] gap-8"> {/* Changed to flex layout */}
          {/* Sidebar */}
          <div className="w-1/4">
            {selectedModule ? (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 h-full flex flex-col">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">{selectedModule.name}</h2>

                {/* HistoryList added here, placeholder <p> removed */}
                <div className="flex-grow overflow-y-auto mb-4">
                  <HistoryList onSelectHistory={handleSelectHistory} modules={modules} />
                </div>

                <button
                  onClick={() => {
                    setSelectedModule(null);
                    setMessages([]); // Clear messages when going back
                  }}
                  className="mt-auto px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
                >
                  Back to Module Selection
                </button>
              </div>
            ) : (
              // Wrapper for ModuleSelector and HistoryList when no module is selected
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 h-full flex flex-col space-y-4 overflow-y-auto">
                <ModuleSelector
                  modules={modules}
                  selectedModule={selectedModule}
                  onSelectModule={handleSelectModule}
                />
                <HistoryList onSelectHistory={handleSelectHistory} modules={modules} />
              </div>
            )}
          </div>

          {/* Chat Interface Panel */}
          <div className="flex-1">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 h-full overflow-hidden">
              <ChatInterface
                messages={messages}
                selectedAgent={null} // selectedAgent passed as null
                selectedModule={selectedModule}
                onSendMessage={handleSendMessage}
                isTyping={isTyping}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      {/* <footer className="bg-white/80 backdrop-blur-sm border-t border-gray-200 mt-8">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <p>© 2024 AI Assistant Hub. Powered by Gemini + Vertex AI</p>
            <div className="flex gap-4">
              <button className="hover:text-gray-800 transition-colors">Privacy Policy</button>
              <button className="hover:text-gray-800 transition-colors">Terms of Service</button>
              <button className="hover:text-gray-800 transition-colors">Support</button>
            </div>
          </div>
        </div>
      </footer> */}
    </div>
  );
}

export default App;