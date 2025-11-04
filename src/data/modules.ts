import { Module } from '../types';

export const modules: Module[] = [
  {
    id: 'onboarding',
    name: 'Onboarding Process',
    description: 'Complete employee onboarding workflow with specialized agents',
    icon: 'UserPlus',
    color: 'bg-gradient-to-br from-blue-500 to-indigo-600',
    agents: [
      {
        id: 'welcome-agent',
        name: 'Welcome Agent',
        description: 'Company introductions and manager connections',
        icon: 'UserCheck',
        color: 'bg-blue-500',
        capabilities: ['Company Introduction', 'Manager Assignment', 'Team Integration', 'Culture Overview'],
        module: 'onboarding',
        subModule: 'welcome'
      },
      {
        id: 'benefits-explainer',
        name: 'Benefits Explainer',
        description: 'Contextual benefits information and enrollment',
        icon: 'Heart',
        color: 'bg-green-500',
        capabilities: ['Health Insurance', 'Retirement Plans', 'PTO Policies', 'Wellness Programs', 'Benefits Enrollment'],
        module: 'onboarding',
        subModule: 'benefits'
      },
      {
        id: 'system-access',
        name: 'System Access Agent',
        description: 'Slack, Jira, GitHub provisioning and setup',
        icon: 'Settings',
        color: 'bg-purple-500',
        capabilities: ['Slack Setup', 'Jira Access', 'GitHub Provisioning', 'VPN Configuration', 'Security Training'],
        module: 'onboarding',
        subModule: 'system-access'
      },
      {
        id: 'task-management',
        name: 'Task Management',
        description: 'Onboarding checklists and progress tracking',
        icon: 'CheckSquare',
        color: 'bg-amber-500',
        capabilities: ['Checklist Creation', 'Progress Tracking', 'Deadline Management', 'Task Assignment'],
        module: 'onboarding',
        subModule: 'tasks'
      },
      {
        id: 'expense-policy',
        name: 'Expense Policy Agent',
        description: 'Expense guidance with RAG on HR documents',
        icon: 'CreditCard',
        color: 'bg-orange-500',
        capabilities: ['Expense Policies', 'Receipt Guidelines', 'Equipment Requests', 'Travel Expenses'],
        module: 'onboarding',
        subModule: 'expenses'
      },
      {
        id: 'approval-agent',
        name: 'Approval Agent',
        description: 'Generates and routes expense approvals',
        icon: 'FileCheck',
        color: 'bg-red-500',
        capabilities: ['Approval Workflows', 'Manager Routing', 'Status Tracking', 'Notification System'],
        module: 'onboarding',
        subModule: 'approvals'
      }
    ]
  },
  {
    id: 'interview-scheduler',
    name: 'Interview Scheduler',
    description: 'AI-powered interview scheduling with multi-timezone support',
    icon: 'Calendar',
    color: 'bg-gradient-to-br from-indigo-500 to-purple-600',
    agents: [
      {
        id: 'candidate-bot',
        name: 'Candidate Bot',
        description: 'Collects candidate availability and preferences',
        icon: 'Users',
        color: 'bg-teal-500',
        capabilities: ['Availability Collection', 'Preference Gathering', 'Interview Preparation', 'Follow-up'],
        module: 'interview-scheduler',
        subModule: 'candidate-management'
      },
      {
        id: 'calendar-integration',
        name: 'Calendar Integration',
        description: 'Multi-manager calendar sync and coordination',
        icon: 'CalendarDays',
        color: 'bg-indigo-500',
        capabilities: ['Calendar Sync', 'Multi-timezone Support', 'Conflict Detection', 'Real-time Updates'],
        module: 'interview-scheduler',
        subModule: 'calendar'
      },
      {
        id: 'auto-rescheduler',
        name: 'Auto-Rescheduler',
        description: 'Handles changes and time zone conflicts',
        icon: 'RotateCcw',
        color: 'bg-violet-500',
        capabilities: ['Auto-rescheduling', 'Conflict Resolution', 'Timezone Management', 'Emergency Handling'],
        module: 'interview-scheduler',
        subModule: 'rescheduling'
      },
      {
        id: 'notification-agent',
        name: 'Notification Agent',
        description: 'Reminders, invites, and communication',
        icon: 'Bell',
        color: 'bg-pink-500',
        capabilities: ['Email Reminders', 'Calendar Invites', 'SMS Notifications', 'Follow-up Messages'],
        module: 'interview-scheduler',
        subModule: 'notifications'
      }
    ]
  }
];