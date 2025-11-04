import React, { useEffect, useRef } from 'react';
import { Message, Agent, Module } from '../types';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { Bot, Sparkles, UserPlus, Calendar } from 'lucide-react';

interface ChatInterfaceProps {
  messages: Message[];
  selectedAgent: Agent | null;
  selectedModule: Module | null;
  onSendMessage: (message: string) => void;
  isTyping?: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  messages, 
  selectedAgent,
  selectedModule,
  onSendMessage,
  isTyping = false
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getModuleIcon = () => {
    if (selectedModule?.id === 'onboarding') return UserPlus;
    if (selectedModule?.id === 'interview-scheduler') return Calendar;
    return Bot;
  };

  const ModuleIcon = getModuleIcon();

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-gray-50 to-white">
      {/* Chat Header */}
      <div className="bg-white border-b border-gray-200 p-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${
            selectedModule ? selectedModule.color : 'bg-gradient-to-br from-indigo-500 to-purple-600'
          }`}>
            <ModuleIcon className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900">
              {selectedModule ? selectedModule.name : 'AI Assistant'}
            </h3>
            <p className="text-sm text-gray-600">
              {selectedModule
                ? selectedModule.description
                : 'Select a module to begin'
              }
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
            </div>
            <span className="text-sm text-green-600 font-medium">Online</span>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className={`p-4 rounded-full mb-4 ${
              selectedModule ? selectedModule.color : 'bg-gradient-to-br from-blue-100 to-indigo-100'
            }`}>
              <Sparkles className="w-12 h-12 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              {selectedModule
                  ? `Welcome to ${selectedModule.name}`
                  : 'Welcome to AI Assistant Hub'
              }
            </h3>
            <p className="text-gray-600 max-w-md mb-6">
              {selectedModule
                  ? selectedModule.description
                  : 'Select a module from the sidebar to start a conversation.'
              }
            </p>
            {/* Agent-specific capabilities and agent list removed */}
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isTyping && (
              <div className="flex gap-3 mb-6">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-white rounded-2xl rounded-bl-md border border-gray-200 p-4 shadow-sm">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <ChatInput 
        onSendMessage={onSendMessage}
        disabled={!selectedModule} // Changed from !selectedAgent
        placeholder={
          selectedModule
            ? `Message ${selectedModule.name}...`
            : 'Select a module to begin...'
        }
      />
    </div>
  );
};

export default ChatInterface;