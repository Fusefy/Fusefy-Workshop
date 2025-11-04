import React from 'react';
import { MessageAction } from '../types';
import { ExternalLink, FileText, Calendar, Settings, Download } from 'lucide-react';

interface MessageActionsProps {
  actions: MessageAction[];
  onActionClick: (action: MessageAction) => void;
}

const MessageActions: React.FC<MessageActionsProps> = ({ actions, onActionClick }) => {
  const getActionIcon = (action: MessageAction) => {
    if (action.type === 'link') return <ExternalLink className="w-4 h-4" />;
    if (action.action.includes('download')) return <Download className="w-4 h-4" />;
    if (action.action.includes('schedule') || action.action.includes('calendar')) return <Calendar className="w-4 h-4" />;
    if (action.action.includes('guide') || action.action.includes('document')) return <FileText className="w-4 h-4" />;
    if (action.action.includes('setup') || action.action.includes('config')) return <Settings className="w-4 h-4" />;
    return null;
  };

  const getActionStyle = (action: MessageAction, index: number) => {
    const baseStyle = "inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:shadow-md transform hover:scale-105";
    
    if (index === 0) {
      return `${baseStyle} bg-blue-500 text-white hover:bg-blue-600`;
    } else if (action.type === 'link') {
      return `${baseStyle} bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300`;
    } else {
      return `${baseStyle} bg-white text-gray-700 hover:bg-gray-50 border border-gray-300`;
    }
  };

  return (
    <div className="flex flex-wrap gap-2 mt-4">
      {actions.map((action, index) => (
        <button
          key={action.id}
          onClick={() => onActionClick(action)}
          className={getActionStyle(action, index)}
        >
          {getActionIcon(action)}
          <span>{action.label}</span>
        </button>
      ))}
    </div>
  );
};

export default MessageActions;