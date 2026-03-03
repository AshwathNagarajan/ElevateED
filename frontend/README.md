# ElevateED Frontend

Modern React frontend for the ElevateED student success platform, built with Vite, React, and Tailwind CSS.

## Features

- ⚡ **Vite** - Fast build tool and dev server
- ⚛️ **React 18** - Latest React with hooks
- 🎨 **Tailwind CSS** - Utility-first CSS framework
- 📊 **Chart.js** - Beautiful data visualizations
- 🧭 **React Router** - Client-side routing
- 🎯 **Lucide Icons** - Modern icon library
- 📱 **Responsive Design** - Mobile-first approach

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable React components
│   │   ├── Navbar.jsx
│   │   ├── StudentDashboard.jsx
│   │   └── AdminDashboard.jsx
│   ├── pages/             # Page components
│   │   └── Login.jsx
│   ├── App.jsx            # Main app component
│   ├── App.css            # App-specific styles
│   ├── index.css          # Global styles with Tailwind
│   └── main.jsx           # Entry point
├── index.html             # HTML template
├── package.json           # Dependencies and scripts
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind configuration
├── postcss.config.js      # PostCSS configuration
└── .eslintrc.json         # ESLint configuration
```

## Setup Instructions

### Prerequisites

- Node.js 16+ and npm/yarn installed

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env.local
   ```

3. **Update `.env.local` with your configuration:**
   ```
   VITE_API_URL=http://localhost:8000/api
   VITE_ENABLE_MOCK_DATA=true
   ```

## Development

### Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

### Linting

Check code quality:
```bash
npm run lint
```

Fix linting issues:
```bash
npm run lint:fix
```

## Key Components

### Login Page
- Email/password authentication
- Role selection (Student/Admin)
- Demo credentials support
- Beautiful gradient background

### Student Dashboard
- Skill score progression chart
- Attendance percentage display
- Personalized recommendations
- Data refresh functionality

### Admin Dashboard
- Track distribution pie chart
- Average skill scores by track
- Dropout risk student table
- Risk level color coding
- Contact student button

## API Integration

The frontend is configured to communicate with the backend API running on `http://localhost:8000`.

### Proxy Configuration

Vite is configured to proxy `/api` requests to the backend:
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

### Mock Data

For development, the components include mock data. Set `VITE_ENABLE_MOCK_DATA=false` in `.env.local` to use real API calls.

## Styling

### Tailwind CSS

Custom theme colors are defined in `tailwind.config.js`:
- Primary: Purple (`primary-600`)
- Secondary: Cyan (`secondary-600`)

### Custom Components

Global Tailwind components are defined in `src/index.css`:
- `.btn-primary`, `.btn-secondary`, `.btn-outline`
- `.card`, `.card-lg`
- `.input-field`
- `.badge-primary`, `.badge-secondary`, etc.

## Deployment

### Build for Production

```bash
npm run build
```

### Deploy to Static Host

The `dist/` folder contains the production build. Deploy it to:
- Vercel
- Netlify
- AWS S3
- GitHub Pages
- Any static hosting service

## Troubleshooting

### Port Already in Use

If port 5173 is in use, Vite will automatically use the next available port.

### API Connection Issues

1. Ensure the backend is running on `http://localhost:8000`
2. Check CORS settings in the backend
3. Verify `VITE_API_URL` in `.env.local`

### Module Not Found

```bash
rm -rf node_modules package-lock.json
npm install
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT License
