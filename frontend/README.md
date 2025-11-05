# Claims Management Frontend

A modern React frontend for the Claims Management System built with Vite, TypeScript, and Tailwind CSS.

## 🚀 Features

- **Modern Tech Stack**: React 18, TypeScript, Vite, Tailwind CSS
- **Data Management**: TanStack Query for server state management
- **Form Handling**: React Hook Form with Zod validation  
- **Responsive Design**: Mobile-first responsive UI
- **Real-time Updates**: Automatic data synchronization
- **OCR Integration**: Document processing with AI agents
- **Toast Notifications**: User feedback system
- **Loading States**: Comprehensive loading and error handling

## 📦 Tech Stack

### Core
- **React 18** - UI library with hooks and concurrent features
- **TypeScript** - Type safety and developer experience
- **Vite** - Fast build tool and development server

### Routing & Navigation
- **React Router 6** - Client-side routing

### State Management
- **TanStack Query (React Query)** - Server state management and caching
- **React Hook Form** - Form state management

### Validation
- **Zod** - TypeScript-first schema validation

### Styling
- **Tailwind CSS** - Utility-first CSS framework
- **Inter Font** - Modern typography

### HTTP Client
- **Axios** - HTTP client with interceptors

### Utilities
- **date-fns** - Date formatting and manipulation
- **react-hot-toast** - Toast notifications
- **clsx** - Conditional CSS classes

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Base UI components (Button, Input, etc.)
│   ├── layout/         # Layout components
│   └── forms/          # Form-specific components
├── pages/              # Page components
├── hooks/              # Custom React hooks
├── services/           # API service layers
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── main.tsx           # Application entry point
```

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+ 
- npm or yarn package manager
- FastAPI backend running on localhost:8000 (see backend setup)

### Quick Start

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment setup**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # The .env file should contain:
   VITE_API_BASE_URL=http://localhost:8000
   VITE_ENVIRONMENT=development
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:3000`

### Backend Integration

Ensure the FastAPI backend is running:
```bash
# In the backend directory
cd ../backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The frontend will proxy API requests to the backend automatically.

### Available Scripts

```bash
# Development
npm run dev              # Start dev server
npm run build           # Build for production
npm run preview         # Preview production build

# Code Quality
npm run lint            # Run ESLint
npm run lint:fix        # Fix ESLint issues
npm run type-check      # TypeScript type checking
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Environment
VITE_ENVIRONMENT=development
```

### API Integration

The frontend connects to the FastAPI backend running on `http://localhost:8000`. All API endpoints are prefixed with `/api/v1`.

Key endpoints:
- `GET /api/v1/claims` - Fetch claims with pagination and filtering
- `POST /api/v1/claims` - Create new claim
- `GET /api/v1/claims/{id}` - Get claim by ID
- `PATCH /api/v1/claims/{id}` - Update claim
- `POST /api/v1/agents/ocr/process/{id}` - Process document with OCR

## 🎨 UI Components

### Button Component
```tsx
<Button variant="primary" size="md" loading={false}>
  Create Claim
</Button>
```

Variants: `primary`, `secondary`, `danger`, `ghost`, `outline`
Sizes: `sm`, `md`, `lg`

### Status Badge
```tsx
<StatusBadge status={ClaimStatus.RECEIVED} />
```

Displays color-coded status badges for different claim states.

### Input Component
```tsx
<Input
  label="Patient Name"
  error={errors.patient_name?.message}
  {...register('patient_name')}
/>
```

Includes validation error display and proper accessibility attributes.

## 📱 Pages & Features

### Dashboard (`/dashboard`)
- Claims list with pagination
- Status filtering
- Search functionality  
- Real-time updates
- Quick stats overview

### Create Claim (`/claims/new`)
- Form validation with Zod schema
- Auto-generated claim numbers
- Success/error handling
- Redirect after creation

### Claim Detail (`/claims/:id`)
- Complete claim information
- OCR processing status
- Document management
- Action buttons for agents
- Edit/update capability

### Mobile Support
- Responsive design for all screen sizes
- Touch-friendly interface
- Mobile navigation menu
- Optimized for mobile browsers

## 🔍 Data Management

### React Query Integration

Custom hooks for data fetching:

```tsx
// Fetch claims with filters
const { data, isLoading, error } = useClaims({
  skip: 0,
  limit: 20,
  status: ClaimStatus.RECEIVED
});

// Create claim mutation
const createMutation = useCreateClaim();
```

### Cache Management
- Automatic cache invalidation on mutations
- Optimistic updates for better UX
- Background refetching
- Stale-while-revalidate strategy

## 🎯 Form Handling

### Validation Schema (Zod)

```tsx
const claimSchema = z.object({
  claim_number: z.string().min(1, 'Claim number is required'),
  patient_name: z.string().min(2, 'Patient name must be at least 2 characters'),
  claim_amount: z.number().positive('Amount must be positive'),
  // ... other fields
});
```

### Form Integration

```tsx
const form = useForm<ClaimCreate>({
  resolver: zodResolver(claimSchema),
  defaultValues: {
    claim_number: generateClaimNumber(),
    // ... other defaults
  }
});
```

## 🚦 Status Management

Claims support the following statuses with color coding:

- **RECEIVED** (Blue) - Initial submission
- **OCR_PROCESSING** (Yellow) - Document processing
- **PII_MASKED** (Purple) - Privacy protection applied
- **DQ_VALIDATED** (Cyan) - Data quality validated
- **HUMAN_REVIEW** (Orange) - Requires manual review
- **CONSENT_VERIFIED** (Indigo) - Patient consent confirmed
- **CLAIM_VALIDATED** (Green) - Fully validated
- **PAYER_SUBMITTED** (Teal) - Submitted to payer
- **SETTLED** (Dark Green) - Payment processed
- **REJECTED** (Red) - Claim rejected

## 🔒 Error Handling

### API Error Management
- Axios interceptors for global error handling
- Retry logic for network failures
- User-friendly error messages
- Toast notifications for feedback

### Loading States
- Skeleton loaders for tables
- Button loading spinners  
- Page-level loading indicators
- Error boundaries for crash recovery

## 🔮 Future Enhancements

### Planned Features
- User authentication and authorization
- Advanced filtering and sorting
- Bulk operations
- Document viewer component
- Real-time notifications
- Audit trail tracking
- Analytics dashboard
- Export functionality

### Agent Integration
The frontend is structured to easily integrate additional AI agents:
- PII masking agent
- Data quality validation agent  
- Consent verification agent
- Claim validation agent

## 🤝 Contributing

### Code Style
- ESLint + Prettier for consistent formatting
- TypeScript strict mode enabled
- Semantic commit messages
- Component documentation

### Development Workflow
1. Create feature branch
2. Implement changes with tests
3. Run linting and type checking
4. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support or questions:
1. Check the troubleshooting section
2. Review API documentation  
3. Contact the development team

---

**Built with ❤️ using React, TypeScript, and modern web technologies.**