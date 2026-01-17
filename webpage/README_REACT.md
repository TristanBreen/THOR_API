# Seizure Wellness Dashboard v2.0 - React Edition

A modern, fully-responsive web application built with React, Next.js, and TypeScript for comprehensive seizure monitoring and health tracking.

## 🎨 What's New in v2.0

### Technology Stack
- **Frontend**: React 18 + Next.js 14 (modern SSR/SSG)
- **Styling**: Tailwind CSS with custom animations
- **Charts**: Recharts for beautiful, interactive data visualization
- **Icons**: Lucide React for modern icon system
- **Backend**: Flask with CORS support for seamless API integration

### Features
✨ **Modern UI/UX**
- Responsive design (mobile, tablet, desktop)
- Smooth animations and transitions
- Beautiful gradient backgrounds
- Accessible color scheme with sage and cream tones
- Dark mode ready

📊 **Advanced Data Visualization**
- Interactive Recharts with smooth animations
- Real-time data updates
- Multiple chart types (bar, line, area)
- Heatmaps for pattern analysis

🔋 **Health Insights**
- Sleep analysis and correlation with seizures
- Heart rate trends with seizure markers
- Activity level tracking
- Sleep debt calculation
- Comprehensive health analytics

📱 **Responsive Components**
- Mobile-optimized stat cards
- Collapsible data tables with sorting/filtering
- Touch-friendly interface
- Fast load times with Next.js optimizations

🚀 **Performance**
- Server-side rendering with Next.js
- Automatic image optimization
- Code splitting and lazy loading
- API response caching
- Fast refresh for development

## 📁 Project Structure

```
webpage/
├── pages/
│   ├── _app.tsx           # Next.js app wrapper
│   ├── _document.tsx      # Custom document
│   ├── index.tsx          # Home redirect
│   └── dashboard.tsx      # Main dashboard page
├── components/
│   ├── StatCards.tsx      # Statistics display cards
│   ├── Predictions.tsx    # Seizure risk predictions
│   ├── Insights.tsx       # Health insights section
│   ├── Charts.tsx         # Chart components
│   └── DataTable.tsx      # Filterable data table
├── styles/
│   └── globals.css        # Global Tailwind styles
├── public/                # Static assets
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── next.config.js        # Next.js config
├── tailwind.config.js    # Tailwind config
├── postcss.config.js     # PostCSS config
└── README.md            # This file
```

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ (18+ recommended)
- npm or yarn
- Python 3.8+ (for Flask backend)

### Installation

1. **Install Node dependencies**
```bash
cd webpage
npm install
# or
yarn install
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

### Development

1. **Start Flask backend** (from THOR_API directory)
```bash
python app.py
# Runs on http://localhost:5000
```

2. **Start Next.js development server** (from webpage directory)
```bash
npm run dev
# Runs on http://localhost:3000
```

3. **Open in browser**
```
http://localhost:3000
```

The development server will auto-refresh on file changes.

### Building for Production

1. **Build the Next.js app**
```bash
npm run build
```

2. **Start production server**
```bash
npm start
```

Or use the provided start script:
```bash
chmod +x start.sh
./start.sh
```

## 🎨 Customization

### Tailwind Colors
Edit `tailwind.config.js` to customize colors:
```javascript
colors: {
  sage: {
    50: '#f7f9f5',
    // ... customize as needed
  },
  cream: {
    50: '#fefdfb',
    // ... customize as needed
  }
}
```

### Global Styles
Edit `styles/globals.css` to add custom CSS:
```css
/* Add custom styles here */
@layer components {
  .custom-component {
    @apply your-tailwind-classes;
  }
}
```

### Component Props
All components are TypeScript-typed. Edit component files to adjust prop interfaces and functionality.

## 📊 API Integration

The app communicates with the Flask backend via these endpoints:

### `/api/data`
Returns all dashboard data including:
- Statistics (seizure counts, averages, etc.)
- Chart data (distributions, trends, heatmaps)
- Health insights (sleep, heart rate, activity)
- Predictions (seizure risk forecasts)
- Last update timestamp

**Response Format**:
```json
{
  "statistics": { /* ... */ },
  "charts": { /* ... */ },
  "health_insights": { /* ... */ },
  "predictions": { /* ... */ },
  "last_updated": "2024-01-16 12:34:56"
}
```

### `/api/export`
Downloads seizure data as CSV file.

## 🔧 Environment Configuration

Create a `.env.local` file for local environment variables:
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
NODE_ENV=development
```

## 📱 Responsive Design

The app is fully responsive with breakpoints:
- **Mobile**: < 640px (`sm`)
- **Tablet**: 640px - 1024px (`md`)
- **Desktop**: > 1024px (`lg`)

Components automatically adapt layout based on screen size.

## ⚡ Performance Optimization

- **Automatic code splitting** - Only load what's needed
- **Image optimization** - Next.js Image component
- **CSS-in-JS** - Tailwind CSS for smaller bundle
- **API caching** - 60-second server-side cache
- **Lazy loading** - Charts and data load on demand

## 🐛 Troubleshooting

### CORS Errors
Ensure Flask-CORS is installed and enabled:
```bash
pip install Flask-CORS
```

The app automatically enables CORS in Flask.

### Data Not Loading
1. Verify Flask backend is running on port 5000
2. Check browser console for API errors
3. Confirm CSV files exist in the Data directory
4. Check Flask logs for detailed error information

### Build Errors
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules
npm install

# Rebuild
npm run build
```

## 📚 Dependencies

### Frontend
- **react**: UI library
- **next**: React framework with SSR
- **tailwindcss**: Utility-first CSS
- **recharts**: Data visualization
- **lucide-react**: Icon library
- **framer-motion**: Animation library
- **date-fns**: Date utilities

### Backend
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin support
- **pandas**: Data processing
- **numpy**: Numerical computing

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
CMD ["npm", "start"]
```

### Vercel Deployment
1. Connect GitHub repository to Vercel
2. Set build command: `npm run build`
3. Set start command: `npm start`
4. Deploy automatically on push

## 📝 License

This project is part of the THOR_API seizure tracking system.

## 🤝 Contributing

To contribute improvements:
1. Create a feature branch
2. Make changes and test thoroughly
3. Submit a pull request
4. Ensure all tests pass

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review Flask logs for backend errors
- Check browser console for frontend errors
- Review component prop types for API changes

---

Built with ❤️ for comprehensive seizure wellness monitoring
