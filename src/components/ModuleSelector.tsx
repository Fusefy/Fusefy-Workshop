import React from 'react';
import { Module } from '../types';
import { 
  UserPlus, 
  Calendar,
  ChevronRight,
  Users,
  CheckCircle
} from 'lucide-react';

interface ModuleSelectorProps {
  modules: Module[];
  selectedModule: Module | null;
  onSelectModule: (module: Module) => void;
}

const iconMap = {
  UserPlus,
  Calendar,
  Users,
  CheckCircle
};

const ModuleSelector: React.FC<ModuleSelectorProps> = ({ 
  modules, 
  selectedModule, 
  onSelectModule 
}) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-800">AI Modules</h2>
        <div className="flex gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-500">Active</span>
        </div>
      </div>
      
      <div className="space-y-4">
        {modules.map((module) => {
          const IconComponent = iconMap[module.icon as keyof typeof iconMap];
          const isSelected = selectedModule?.id === module.id;
          
          return (
            <button
              key={module.id}
              onClick={() => onSelectModule(module)}
              className={`w-full p-6 rounded-xl text-left transition-all duration-300 hover:shadow-lg group ${
                isSelected 
                  ? 'bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 shadow-md transform scale-[1.02]' 
                  : 'bg-gray-50 hover:bg-gray-100 border border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-xl ${module.color} flex-shrink-0 shadow-sm`}>
                  <IconComponent className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className={`text-lg font-semibold ${
                      isSelected ? 'text-blue-900' : 'text-gray-900'
                    }`}>
                      {module.name}
                    </h3>
                    <ChevronRight className={`w-5 h-5 transition-all duration-200 ${
                      isSelected ? 'text-blue-500 rotate-90' : 'text-gray-400 group-hover:translate-x-1'
                    }`} />
                  </div>
                  <p className={`text-sm mb-3 ${
                    isSelected ? 'text-blue-700' : 'text-gray-600'
                  }`}>
                    {module.description}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className={`text-xs font-medium ${
                      isSelected ? 'text-blue-600' : 'text-gray-500'
                    }`}>
                      {module.agents.length} Specialized Agents
                    </span>
                    <div className="flex gap-1">
                      {[...Array(3)].map((_, i) => (
                        <div
                          key={i}
                          className={`w-2 h-2 rounded-full ${
                            isSelected ? 'bg-blue-400' : 'bg-gray-300'
                          }`}
                        />
                      ))}
                    </div>
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

export default ModuleSelector;