# EnergyOS - Intelligent Energy Management Platform

A modern, AI-powered renewable energy management system with real-time monitoring, forecasting, optimization, and sustainability tracking.

## Features

- **Real-time Monitoring**: Live energy generation and consumption metrics
- **AI Forecasting**: 24-hour and 7-day energy generation predictions
- **Optimization**: Machine learning-based recommendations for peak efficiency
- **Digital Twin**: Simulate energy system scenarios before implementation
- **Carbon Analytics**: Track and reduce your carbon footprint
- **Advanced Analytics**: Detailed breakdowns of energy usage patterns
- **Report Generation**: Export data in PDF, Excel, and CSV formats
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile

## Tech Stack

- **Framework**: Next.js 16 with React 19
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui with Radix UI
- **Charts & Visualization**: Recharts
- **Icons**: Lucide React
- **Forms**: React Hook Form with Zod validation
- **Deployment**: Vercel-ready

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js**: v18.17 or later (check with `node --version`)
- **npm/pnpm**: v9 or later (check with `npm --version` or `pnpm --version`)
- **Git**: For cloning the repository (optional)

## Installation

### Step 1: Clone or Download the Project

```bash
# If using Git
git clone <repository-url>
cd v0-project

# Or extract the downloaded ZIP file
cd v0-project
```

### Step 2: Install Dependencies

Using **pnpm** (recommended):
```bash
pnpm install
```

Or using **npm**:
```bash
npm install
```

Or using **yarn**:
```bash
yarn install
```

The installation will download all required packages listed in `package.json`.

## Running the Project Locally

### Development Mode (Recommended)

Start the development server with hot-reload:

```bash
pnpm dev
```

Or with npm:
```bash
npm run dev
```

The application will be available at:
- **Local**: http://localhost:3000
- **Network**: http://192.168.x.x:3000 (see terminal output)

**Features in development mode:**
- Hot Module Replacement (HMR) - changes appear instantly
- Detailed error messages with stack traces
- Source maps for debugging
- Slower performance (expected)

### Production Build

Create an optimized production build:

```bash
pnpm build
```

Then start the production server:

```bash
pnpm start
```

The application will be available at http://localhost:3000 (production optimized).

## Project Structure

```
v0-project/
├── app/                          # Next.js app directory
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Redirect to login
│   ├── login/
│   │   └── page.tsx             # Login page
│   ├── signup/
│   │   └── page.tsx             # Signup page
│   └── dashboard/
│       ├── layout.tsx           # Dashboard layout with sidebar
│       ├── page.tsx             # Dashboard overview
│       ├── monitoring/          # Real-time monitoring
│       ├── forecasting/         # Energy forecasting
│       ├── optimization/        # AI recommendations
│       ├── digital-twin/        # Scenario simulation
│       ├── analytics/           # Energy analytics
│       ├── carbon-analytics/    # Sustainability tracking
│       ├── reports/             # Report generation
│       ├── settings/            # System settings
│       └── help/                # Help & documentation
├── components/
│   ├── ui/                      # Reusable UI components
│   ├── dashboard-sidebar.tsx    # Navigation sidebar
│   └── ...                      # Other components
├── lib/
│   ├── mock-data.ts            # Sample data for development
│   └── utils.ts                # Utility functions
├── app/globals.css             # Global styles & design tokens
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript config
└── next.config.mjs             # Next.js config
```

## Usage

### Login to the Application

1. Open http://localhost:3000
2. You'll be redirected to the login page
3. Enter credentials or click "Enter as Demo User" for instant access

**Demo credentials:**
- Email: `demo@energyos.com`
- Password: `demo123`

### Navigate the Dashboard

The sidebar provides quick access to all major sections:

- **Dashboard**: Overview of your energy system status
- **Monitoring**: Real-time energy metrics and gauges
- **Forecasting**: 24-hour and weekly generation predictions
- **Optimization**: AI-powered efficiency recommendations
- **Digital Twin**: Test scenarios before implementation
- **Analytics**: Detailed energy usage analysis
- **Carbon Analytics**: Carbon footprint and offset tracking
- **Reports**: Generate and download reports
- **Settings**: Configure alerts, thresholds, and preferences
- **Help**: Documentation, FAQs, and support resources

### Mock Data

The application uses mock data for demonstration. To view or modify it:

```bash
# Edit mock data
vi lib/mock-data.ts
```

All pages pull from this single source, so changes will reflect across the dashboard.

## Available Scripts

```bash
# Development server (with hot reload)
pnpm dev

# Production build
pnpm build

# Start production server
pnpm start

# Run linting
pnpm lint
```

## Environment Variables

This application doesn't require environment variables for local development. All data is mock-based.

For production deployment to Vercel, you may want to add:
- `NEXT_PUBLIC_API_URL`: Backend API endpoint
- `AUTH_SECRET`: Authentication secret key

## Customization

### Change the Color Scheme

Edit `app/globals.css` to modify the design tokens:

```css
:root {
  --primary: oklch(0.52 0.18 142.8);  /* Green */
  --secondary: oklch(0.48 0.15 201);  /* Blue */
  --accent: oklch(0.58 0.2 81);       /* Yellow */
  /* ... other tokens */
}
```

### Modify Navigation Items

Edit `components/dashboard-sidebar.tsx`:

```typescript
const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  // Add more items here
];
```

### Update Mock Data

Edit `lib/mock-data.ts` to change the sample data used throughout the application.

## Deployment

### Deploy to Vercel (Recommended)

1. Push your code to GitHub
2. Connect your repository to Vercel (vercel.com)
3. Vercel will automatically detect Next.js and configure deployment
4. Your app will be live in seconds

```bash
# Or deploy directly via CLI
npm i -g vercel
vercel
```

### Deploy to Other Platforms

The project can be deployed to any platform that supports Node.js:
- **AWS Amplify**: Automatic Next.js detection
- **Netlify**: With Next.js plugin
- **DigitalOcean App Platform**: Standard Node.js deployment
- **Docker**: Create a Dockerfile for containerized deployment

## Troubleshooting

### Port Already in Use

If port 3000 is already in use:

```bash
# macOS/Linux: Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Windows: Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use a different port
pnpm dev -- -p 3001
```

### Module Not Found Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Build Fails

```bash
# Clean build cache
rm -rf .next
pnpm build
```

## Performance Tips

1. **Use Responsive Images**: Optimize images before adding to the project
2. **Code Splitting**: Next.js automatically splits code per route
3. **Database Queries**: Mock data is loaded on-demand
4. **Caching**: Browser caching enabled for static assets

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari 12+, Chrome Android

## Security

- All routes use client-side routing (no sensitive data exposed)
- No external API calls in mock mode
- Input validation via Zod schemas
- XSS protection via React's default rendering

## Contributing

To contribute to EnergyOS:

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes
3. Commit: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is proprietary software. All rights reserved.

## Support

For issues and questions:
- **Email**: support@energyos.com
- **Documentation**: See the Help page in the dashboard
- **GitHub Issues**: (if applicable)

## Roadmap

- [ ] Real database integration (Supabase/PostgreSQL)
- [ ] User authentication with JWT
- [ ] API integration with hardware devices
- [ ] Real-time WebSocket updates
- [ ] Multi-user support with role-based access
- [ ] Advanced AI forecasting models
- [ ] Mobile app (React Native)
- [ ] Integration with utility billing systems

## Getting Help

1. Check the **Help** page in the dashboard for FAQs
2. Review the **Settings** page for system configuration
3. Check terminal output for error messages
4. Try the troubleshooting section above

---

**Happy energy management! ⚡**
