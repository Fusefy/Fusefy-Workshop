import { Agent } from '../types';

export const agents: Agent[] = [
  {
    id: 'welcome',
    name: 'Welcome Agent',
    description: 'Provides company introductions and manager connections',
    icon: 'UserCheck',
    color: 'bg-blue-500',
    capabilities: ['Company Introduction', 'Manager Assignment', 'Team Integration']
  },
  {
    id: 'benefits',
    name: 'Benefits Explainer',
    description: 'Explains company benefits and policies',
    icon: 'Heart',
    color: 'bg-green-500',
    capabilities: ['Health Insurance', 'Retirement Plans', 'PTO Policies', 'Wellness Programs']
  },
  {
    id: 'system-access',
    name: 'System Access Agent',
    description: 'Handles system provisioning and access setup',
    icon: 'Settings',
    color: 'bg-purple-500',
    capabilities: ['Slack Setup', 'Jira Access', 'GitHub Provisioning', 'VPN Configuration']
  },
  {
    id: 'expense',
    name: 'Expense Policy Agent',
    description: 'Provides expense guidance and policy information',
    icon: 'CreditCard',
    color: 'bg-orange-500',
    capabilities: ['Expense Policies', 'Receipt Guidelines', 'Approval Workflows', 'Reimbursement']
  },
  {
    id: 'interview-scheduler',
    name: 'Interview Scheduler',
    description: 'Handles interview scheduling and calendar management',
    icon: 'Calendar',
    color: 'bg-indigo-500',
    capabilities: ['Availability Matching', 'Multi-timezone Support', 'Auto-rescheduling', 'Notifications']
  },
  {
    id: 'candidate-bot',
    name: 'Candidate Bot',
    description: 'Collects candidate availability and preferences',
    icon: 'Users',
    color: 'bg-teal-500',
    capabilities: ['Availability Collection', 'Preference Gathering', 'Interview Preparation', 'Follow-up']
  }
];