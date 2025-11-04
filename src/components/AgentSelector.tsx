import React from 'react';
import { Agent } from '../types';
import { 
  UserCheck, 
  Heart, 
  Settings, 
  CreditCard, 
  Calendar, 
  Users,
  CheckSquare,
  FileCheck,
  CalendarDays,
  RotateCcw,
  Bell,
  ChevronRight,
  ArrowLeft
} from 'lucide-react';

interface AgentSelectorProps {
  agents: Agent[];
  selectedAgent: Agent | null;
  onSelectAgent: (agent: Agent) => void;
  onBack: () => void;
  moduleName: string;
}

const iconMap = {
  UserCheck,
  Heart,
  Settings,
  CreditCard,
  Calendar,
  Users,
  CheckSquare,
  FileCheck,
  CalendarDays,
  RotateCcw,
  Bell
};

const AgentSelector: React.FC<AgentSelectorProps> = ({ 
  agents, 
  selectedAgent, 
  onSelectAgent,
  onBack,
  moduleName
}) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={onBack}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <div className="flex-1">
          <h2 className="text-xl font-semibold text-gray-800">{moduleName}</h2>
          <p className="text-sm text-gray-500">Select a specialized agent</p>
        </div>
        <div className="flex gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-500">Online</span>
        </div>
      </div>
      
      <div className="space-y-3">
        {agents.map((agent) => {
          const IconComponent = iconMap[agent.icon as keyof typeof iconMap];
          const isSelected = selectedAgent?.id === agent.id;
          
          return (
            <button
              key={agent.id}
              onClick={() => onSelectAgent(agent)}
              className={`w-full p-4 rounded-lg text-left transition-all duration-200 hover:shadow-md group ${
                isSelected 
                  ? 'bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 shadow-sm' 
                  : 'bg-gray-50 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg ${agent.color} flex-shrink-0`}>
                  <IconComponent className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h3 className={`font-medium ${
                      isSelected ? 'text-blue-900' : 'text-gray-900'
                    }`}>
                      {agent.name}
                    </h3>
                    <ChevronRight className={`w-4 h-4 transition-transform ${
                      isSelected ? 'text-blue-500 rotate-90' : 'text-gray-400 group-hover:translate-x-1'
                    }`} />
                  </div>
                  <p className={`text-sm mt-1 ${
                    isSelected ? 'text-blue-700' : 'text-gray-600'
                  }`}>
                    {agent.description}
                  </p>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {agent.capabilities.slice(0, 2).map((capability) => (
                      <span
                        key={capability}
                        className={`px-2 py-1 text-xs rounded-full ${
                          isSelected 
                            ? 'bg-blue-100 text-blue-700' 
                            : 'bg-gray-200 text-gray-600'
                        }`}
                      >
                        {capability}
                      </span>
                    ))}
                    {agent.capabilities.length > 2 && (
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        isSelected 
                          ? 'bg-blue-100 text-blue-700' 
                          : 'bg-gray-200 text-gray-600'
                      }`}>
                        +{agent.capabilities.length - 2} more
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default AgentSelector;