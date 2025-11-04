import { Message, MessageAction } from '../types';

export const generateMockResponse = (agentId: string, userMessage: string): Message => {
  const responses: Record<string, (msg: string) => { content: string; actions?: MessageAction[] }> = {
    'welcome-agent': (msg: string) => {
      if (msg.toLowerCase().includes('hello') || msg.toLowerCase().includes('hi') || msg.toLowerCase().includes('start')) {
        return {
          content: `Welcome to TechCorp! 🎉 I'm your Welcome Agent, and I'm thrilled to help you start your journey with us.

**About TechCorp:**
- Founded in 2015, we're a leading tech company focused on innovation
- 2,500+ employees across 15 countries
- We value collaboration, growth, and work-life balance

**Your Details:**
- **Manager:** Sarah Johnson (sarah.johnson@techcorp.com)
- **Team:** Frontend Engineering - Platform Team
- **Start Date:** Next Monday
- **Office Location:** San Francisco HQ (Hybrid - 3 days/week)

**Next Steps:**
I'll schedule a welcome call with Sarah for tomorrow at 2 PM. She's excited to meet you!`,
          actions: [
            { id: '1', label: 'Schedule Welcome Call', type: 'button', action: 'schedule_call' },
            { id: '2', label: 'Meet Your Team', type: 'button', action: 'team_intro' },
            { id: '3', label: 'Company Culture Guide', type: 'link', action: 'culture_guide' },
            { id: '4', label: 'Office Tour Booking', type: 'button', action: 'book_tour' }
          ]
        };
      }
      return {
        content: `I'm here to help you settle in! I can introduce you to our company culture, connect you with your manager, or answer questions about your first day.`,
        actions: [
          { id: '1', label: 'Company Overview', type: 'button', action: 'company_overview' },
          { id: '2', label: 'Meet Manager', type: 'button', action: 'meet_manager' },
          { id: '3', label: 'Team Introduction', type: 'button', action: 'team_intro' }
        ]
      };
    },
    
    'benefits-explainer': (msg: string) => {
      if (msg.toLowerCase().includes('health') || msg.toLowerCase().includes('insurance') || msg.toLowerCase().includes('benefits')) {
        return {
          content: `Great question about our comprehensive benefits package! Here's what we offer:

**Health Insurance Options:**
- **Premium Plan:** $0 monthly premium, $500 deductible
- **Standard Plan:** $150 monthly premium, $1,000 deductible  
- **Basic Plan:** $300 monthly premium, $2,500 deductible

**Additional Benefits:**
- Dental & Vision included in all plans
- $2,000 annual wellness allowance
- Mental health support through BetterHelp
- Telemedicine consultations

**Retirement & Financial:**
- 401(k) with 6% company match
- Stock options program
- Financial planning assistance

**Time Off:**
- 25 days PTO + 10 holidays
- Flexible work arrangements
- Sabbatical program (after 5 years)

**Enrollment Deadline:** Within 30 days of start date`,
          actions: [
            { id: '1', label: 'Start Benefits Enrollment', type: 'button', action: 'start_enrollment' },
            { id: '2', label: 'Schedule Benefits Consultation', type: 'button', action: 'schedule_consultation' },
            { id: '3', label: 'Compare Plans', type: 'button', action: 'compare_plans' },
            { id: '4', label: 'Download Benefits Guide', type: 'link', action: 'download_guide' }
          ]
        };
      }
      return {
        content: `I'm your Benefits Explainer! I can help you understand our comprehensive benefits package and guide you through enrollment.`,
        actions: [
          { id: '1', label: 'Health Insurance', type: 'button', action: 'health_insurance' },
          { id: '2', label: 'Retirement Plans', type: 'button', action: 'retirement_plans' },
          { id: '3', label: 'Time Off Policies', type: 'button', action: 'time_off' }
        ]
      };
    },
    
    'system-access': (msg: string) => {
      if (msg.toLowerCase().includes('slack') || msg.toLowerCase().includes('access') || msg.toLowerCase().includes('setup')) {
        return {
          content: `I'll help you get set up with all the systems you need! Here's your access checklist:

**✅ Completed:**
- Email account created (credentials sent)
- Slack workspace invitation sent
- VPN credentials generated

**⏳ In Progress:**
- Jira account setup (ready by tomorrow)
- GitHub organization invite (pending manager approval)
- AWS Console access (requires security training)

**📋 Next Steps:**
1. Join Slack workspace: techcorp-team.slack.com
2. Complete security training (mandatory)
3. Set up 2FA on all accounts
4. Install required development tools

**Security Requirements:**
- 2FA enabled on all accounts
- VPN required for remote access
- Security training completion certificate`,
          actions: [
            { id: '1', label: 'Join Slack Workspace', type: 'link', action: 'join_slack' },
            { id: '2', label: 'Start Security Training', type: 'button', action: 'security_training' },
            { id: '3', label: 'Setup 2FA Guide', type: 'link', action: 'setup_2fa' },
            { id: '4', label: 'Download VPN Client', type: 'link', action: 'download_vpn' },
            { id: '5', label: 'Request GitHub Access', type: 'button', action: 'request_github' }
          ]
        };
      }
      return {
        content: `I'll help you get access to all the systems you need! This includes Slack, Jira, GitHub, VPN, and other development tools.`,
        actions: [
          { id: '1', label: 'View Access Checklist', type: 'button', action: 'access_checklist' },
          { id: '2', label: 'Setup Slack', type: 'button', action: 'setup_slack' },
          { id: '3', label: 'Development Tools', type: 'button', action: 'dev_tools' }
        ]
      };
    },
    
    'task-management': (msg: string) => {
      return {
        content: `Here's your personalized onboarding checklist with progress tracking:

**Week 1 - Getting Started (75% Complete)**
✅ Complete welcome orientation
✅ Set up workspace and equipment
✅ Meet your direct manager
⏳ Complete security training (Due: Tomorrow)
⏳ Join team standup meetings

**Week 2 - System Integration (25% Complete)**
📋 Complete benefits enrollment
📋 Finish system access setup
📋 Shadow team members
📋 Review codebase and documentation
📋 Set up development environment

**Week 3 - Project Assignment (0% Complete)**
📋 Meet with project stakeholders
📋 Review project requirements
📋 Set up project tracking tools
📋 Begin first assignment

**Upcoming Deadlines:**
- Security Training: Tomorrow 5 PM
- Benefits Enrollment: 5 days remaining
- First Code Review: Next Friday`,
        actions: [
          { id: '1', label: 'Mark Task Complete', type: 'button', action: 'mark_complete' },
          { id: '2', label: 'Request Extension', type: 'button', action: 'request_extension' },
          { id: '3', label: 'Schedule Check-in', type: 'button', action: 'schedule_checkin' },
          { id: '4', label: 'View Full Checklist', type: 'link', action: 'full_checklist' },
          { id: '5', label: 'Get Help with Task', type: 'button', action: 'get_help' }
        ]
      };
    },
    
    'expense-policy': (msg: string) => {
      if (msg.toLowerCase().includes('laptop') || msg.toLowerCase().includes('equipment')) {
        return {
          content: `I can help you with equipment expenses! Here's our comprehensive policy:

**Equipment Allowance (Annual):**
- **Laptop:** Up to $2,500 (Mac or PC)
- **Monitor:** Up to $800 (external display)
- **Accessories:** Up to $500 (keyboard, mouse, webcam)
- **Home Office:** Up to $1,000 (desk, chair, lighting)
- **Software:** Up to $300 (licenses, subscriptions)

**Your Current Budget:**
- Equipment: $3,800 remaining
- Home Office: $1,000 remaining
- Software: $300 remaining

**Approval Process:**
1. Get pre-approval for purchases >$500
2. Submit receipts within 30 days
3. Use Expensify app for submissions
4. Manager approval required

**Popular Equipment Choices:**
- MacBook Pro 16" M3 ($2,399)
- Dell XPS 15 ($1,899)
- LG 27" 4K Monitor ($399)
- Herman Miller Chair ($695)`,
          actions: [
            { id: '1', label: 'Create Equipment Request', type: 'button', action: 'create_request' },
            { id: '2', label: 'View Approved Vendors', type: 'link', action: 'approved_vendors' },
            { id: '3', label: 'Submit Receipt', type: 'button', action: 'submit_receipt' },
            { id: '4', label: 'Check Budget Status', type: 'button', action: 'check_budget' },
            { id: '5', label: 'Download Expensify App', type: 'link', action: 'download_expensify' }
          ]
        };
      }
      return {
        content: `I'm here to help with expense policies and approvals! I can guide you through equipment purchases, travel expenses, and reimbursements.`,
        actions: [
          { id: '1', label: 'Equipment Policy', type: 'button', action: 'equipment_policy' },
          { id: '2', label: 'Travel Expenses', type: 'button', action: 'travel_expenses' },
          { id: '3', label: 'Meal Allowances', type: 'button', action: 'meal_allowances' }
        ]
      };
    },
    
    'approval-agent': (msg: string) => {
      return {
        content: `I manage all approval workflows and can help route your requests efficiently:

**Current Pending Approvals:**
1. **Equipment Request** - MacBook Pro 16" ($2,399)
   - Status: Pending Manager Approval
   - Submitted: 2 hours ago
   - Expected: Within 24 hours

2. **Home Office Setup** - Standing Desk & Chair ($895)
   - Status: Under Review
   - Submitted: Yesterday
   - Expected: Tomorrow

**Approval Workflow:**
- **<$500:** Auto-approved
- **$500-$2000:** Manager approval required
- **>$2000:** Manager + Finance approval
- **>$5000:** Executive approval required

**Recent Approvals:**
✅ Software License - IntelliJ IDEA ($149) - Approved
✅ Monitor - LG 27" 4K ($399) - Approved
✅ Webcam - Logitech C920 ($79) - Auto-approved`,
        actions: [
          { id: '1', label: 'Track Approval Status', type: 'button', action: 'track_status' },
          { id: '2', label: 'Expedite Request', type: 'button', action: 'expedite_request' },
          { id: '3', label: 'Contact Approver', type: 'button', action: 'contact_approver' },
          { id: '4', label: 'Modify Request', type: 'button', action: 'modify_request' },
          { id: '5', label: 'View Approval History', type: 'link', action: 'approval_history' }
        ]
      };
    },
    
    'candidate-bot': (msg: string) => {
      if (msg.toLowerCase().includes('available') || msg.toLowerCase().includes('schedule')) {
        return {
          content: `Thanks for reaching out! I'm here to collect your availability for the interview process.

**Interview Process Overview:**
- **Round 1:** Technical Screen (45 minutes)
- **Round 2:** System Design (60 minutes)
- **Round 3:** Culture Fit (30 minutes)
- **Round 4:** Final Interview with VP (45 minutes)

**Your Preferences:**
Please share your availability for the next two weeks:

**Time Zones Supported:**
- PST (Pacific Standard Time)
- EST (Eastern Standard Time)
- GMT (Greenwich Mean Time)
- CET (Central European Time)

**Available Hours:** 9 AM - 6 PM in your local timezone
**Days:** Monday - Friday

**Current Openings This Week:**
- Tuesday 2:00 PM - 3:00 PM (PST)
- Wednesday 10:00 AM - 11:00 AM (EST)
- Thursday 3:00 PM - 4:00 PM (GMT)`,
          actions: [
            { id: '1', label: 'Submit Availability', type: 'form', action: 'submit_availability' },
            { id: '2', label: 'View Available Slots', type: 'button', action: 'view_slots' },
            { id: '3', label: 'Set Timezone', type: 'button', action: 'set_timezone' },
            { id: '4', label: 'Interview Preparation Guide', type: 'link', action: 'prep_guide' }
          ]
        };
      }
      return {
        content: `Hi! I'm here to help coordinate your interview process. I'll collect your availability and preferences to ensure smooth scheduling.`,
        actions: [
          { id: '1', label: 'Share Availability', type: 'button', action: 'share_availability' },
          { id: '2', label: 'Interview Process Info', type: 'button', action: 'process_info' },
          { id: '3', label: 'Reschedule Request', type: 'button', action: 'reschedule_request' }
        ]
      };
    },
    
    'calendar-integration': (msg: string) => {
      return {
        content: `I handle calendar integration and coordination across multiple managers and timezones:

**Current Calendar Status:**
- **Synced Calendars:** 5 managers, 3 timezones
- **Available Slots:** 12 this week, 18 next week
- **Conflicts Detected:** 2 (auto-resolved)

**This Week's Interview Slots:**
**Tuesday, Jan 16**
- 10:00 AM PST - Sarah Chen (Technical Lead)
- 2:00 PM PST - Mike Rodriguez (Senior Dev)

**Wednesday, Jan 17**
- 9:00 AM EST - Lisa Wang (VP Engineering)
- 3:00 PM EST - David Kim (Product Manager)

**Thursday, Jan 18**
- 11:00 AM GMT - Emma Thompson (Team Lead)
- 4:00 PM GMT - Alex Johnson (Architect)

**Real-time Updates:**
- All calendars sync every 15 minutes
- Automatic conflict detection
- Instant notifications for changes`,
        actions: [
          { id: '1', label: 'View Full Calendar', type: 'link', action: 'view_calendar' },
          { id: '2', label: 'Check Availability', type: 'button', action: 'check_availability' },
          { id: '3', label: 'Sync Calendars Now', type: 'button', action: 'sync_calendars' },
          { id: '4', label: 'Add New Interviewer', type: 'button', action: 'add_interviewer' }
        ]
      };
    },
    
    'auto-rescheduler': (msg: string) => {
      return {
        content: `I automatically handle rescheduling and conflict resolution with intelligent algorithms:

**Recent Auto-Reschedules:**
1. **Sarah Chen** - Technical Interview
   - Original: Today 2:00 PM PST
   - Rescheduled: Tomorrow 10:00 AM PST
   - Reason: Emergency meeting conflict

2. **Mike Rodriguez** - Code Review
   - Original: Wednesday 3:00 PM PST
   - Rescheduled: Thursday 2:00 PM PST
   - Reason: Candidate timezone preference

**Rescheduling Rules:**
- **Priority:** Candidate convenience first
- **Buffer Time:** 30 minutes between interviews
- **Timezone Optimization:** Minimize early/late hours
- **Manager Preferences:** Respect blocked times

**Success Metrics:**
- **Reschedule Accuracy:** 98.5%
- **Average Resolution Time:** 12 minutes
- **Candidate Satisfaction:** 4.8/5
- **Zero Conflicts:** Last 30 days`,
        actions: [
          { id: '1', label: 'Request Manual Reschedule', type: 'button', action: 'manual_reschedule' },
          { id: '2', label: 'Set Rescheduling Rules', type: 'button', action: 'set_rules' },
          { id: '3', label: 'View Reschedule History', type: 'link', action: 'reschedule_history' },
          { id: '4', label: 'Emergency Reschedule', type: 'button', action: 'emergency_reschedule' }
        ]
      };
    },
    
    'notification-agent': (msg: string) => {
      return {
        content: `I manage all interview notifications and communications across multiple channels:

**Active Notifications:**
📧 **Email Reminders**
- Interview tomorrow at 2:00 PM PST
- Preparation materials sent
- Calendar invite confirmed

📱 **SMS Notifications**
- 24-hour reminder sent
- 1-hour reminder scheduled
- Emergency contact available

🔔 **In-App Notifications**
- Interview link ready
- Documents uploaded
- Feedback form prepared

**Communication Preferences:**
- **Email:** Primary channel
- **SMS:** Urgent updates only
- **Slack:** Team coordination
- **Calendar:** Meeting invites

**Upcoming Notifications:**
- Tomorrow 1:00 PM: Interview reminder
- Tomorrow 1:45 PM: Join link notification
- Post-interview: Feedback request
- Next week: Follow-up scheduling`,
        actions: [
          { id: '1', label: 'Update Notification Preferences', type: 'button', action: 'update_preferences' },
          { id: '2', label: 'Send Test Notification', type: 'button', action: 'test_notification' },
          { id: '3', label: 'View Notification History', type: 'link', action: 'notification_history' },
          { id: '4', label: 'Emergency Contact Setup', type: 'button', action: 'emergency_contact' }
        ]
      };
    }
  };

  const response = responses[agentId]?.(userMessage) || {
    content: `I'm here to help! As your ${agentId} agent, I can assist you with various tasks. What would you like to know?`,
    actions: [
      { id: '1', label: 'Get Help', type: 'button', action: 'get_help' },
      { id: '2', label: 'View Capabilities', type: 'button', action: 'view_capabilities' }
    ]
  };

  return {
    id: Date.now().toString(),
    content: response.content,
    sender: 'agent',
    timestamp: new Date(),
    agentId,
    type: 'text',
    actions: response.actions
  };
};