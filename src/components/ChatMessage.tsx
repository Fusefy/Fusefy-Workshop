import React from 'react';
import { Message, MessageAction } from '../types';
import { Bot, User, Clock } from 'lucide-react';
import MessageActions from './MessageActions';

interface ChatMessageProps {
  message: Message;
  onActionClick?: (action: MessageAction) => void;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, onActionClick }) => {
  const isUser = message.sender === 'user';
  
  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }).format(date);
  };

  const handleActionClick = (action: MessageAction) => {
    if (onActionClick) {
      onActionClick(action);
    } else {
      // Default action handling
      console.log('Action clicked:', action);
      
      // Simulate different action types
      switch (action.type) {
        case 'link':
          // In a real app, this would open a link
          alert(`Opening: ${action.label}`);
          break;
        case 'button':
          alert(`Executing: ${action.label}`);
          break;
        case 'form':
          alert(`Opening form: ${action.label}`);
          break;
        default:
          alert(`Action: ${action.label}`);
      }
    }
  };

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} mb-6`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser 
          ? 'bg-blue-500 text-white' 
          : 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white'
      }`}>
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>
      
      <div className={`flex-1 max-w-4xl ${isUser ? 'flex flex-col items-end' : ''}`}>
        <div className={`px-4 py-3 rounded-2xl ${
          isUser 
            ? 'bg-blue-500 text-white rounded-br-md' 
            : 'bg-white text-gray-800 border border-gray-200 rounded-bl-md shadow-sm'
        }`}>
          {message.content.split('\n').map((line, index) => {
            // Handle bold text
            if (line.includes('**')) {
              const parts = line.split('**');
              return (
                <p key={index} className={`${index > 0 ? 'mt-2' : ''} leading-relaxed`}>
                  {parts.map((part, partIndex) => 
                    partIndex % 2 === 1 ? (
                      <span key={partIndex} className="font-semibold">{part}</span>
                    ) : (
                      <span key={partIndex}>{part}</span>
                    )
                  )}
                </p>
              );
            }
            
            // Handle empty lines
            if (line.trim() === '') {
              return <div key={index} className="h-2" />;
            }
            
            // Handle bullet points
            if (line.trim().startsWith('- ')) {
              return (
                <div key={index} className="flex items-start gap-2 mt-1">
                  <span className={`font-bold mt-1 ${isUser ? 'text-blue-200' : 'text-blue-400'}`}>•</span>
                  <span className="leading-relaxed">{line.trim().substring(2)}</span>
                </div>
              );
            }
            
            // Handle numbered lists
            if (/^\d+\./.test(line.trim())) {
              return (
                <div key={index} className="flex items-start gap-2 mt-1">
                  <span className={`font-semibold mt-1 ${isUser ? 'text-blue-200' : 'text-blue-400'}`}>
                    {line.trim().match(/^\d+/)?.[0]}.
                  </span>
                  <span className="leading-relaxed">
                    {line.trim().replace(/^\d+\.\s*/, '')}
                  </span>
                </div>
              );
            }
            
            // Handle checkboxes and emojis
            if (line.includes('✅') || line.includes('⏳') || line.includes('📋') || line.includes('📧') || line.includes('📱') || line.includes('🔔')) {
              return (
                <div key={index} className="flex items-start gap-2 mt-1">
                  <span className="text-lg">{line.match(/[✅⏳📋📧📱🔔]/)?.[0]}</span>
                  <span className="leading-relaxed">
                    {line.replace(/[✅⏳📋📧📱🔔]\s*/, '')}
                  </span>
                </div>
              );
            }
            
            return (
              <p key={index} className={`${index > 0 ? 'mt-2' : ''} leading-relaxed`}>
                {line}
              </p>
            );
          })}
        </div>
        
        {/* Message Actions */}
        {!isUser && message.actions && message.actions.length > 0 && (
          <div className="mt-3 w-full">
            <MessageActions 
              actions={message.actions} 
              onActionClick={handleActionClick}
            />
          </div>
        )}
        
        <div className={`flex items-center gap-1 mt-2 text-xs text-gray-500 ${
          isUser ? 'flex-row-reverse' : ''
        }`}>
          <Clock className="w-3 h-3" />
          <span>{formatTime(message.timestamp)}</span>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;