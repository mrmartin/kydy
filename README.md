# Political Posters Platform 🗳️

A modern web application for uploading, sharing, and rating political posters and campaign materials. Built with Next.js, Supabase, and Vercel Blob storage.

**🇨🇿 Fully localized in Czech** - All user interface text, forms, and messages are in Czech language, designed for Czech users and political content.

## 🎯 What is this?

This platform allows users to:
- **Upload political posters** with metadata (title, description, location, date, political party)
- **Browse galleries** of uploaded posters
- **Rate and comment** on political materials
- **Organize by political parties** with color-coded categories
- **User authentication** and personalized dashboards

## 🏗️ Architecture

- **Frontend**: Next.js 15 with React, TypeScript, TailwindCSS
- **Backend**: Next.js API routes
- **Database**: Supabase (PostgreSQL with Row Level Security)
- **Authentication**: Supabase Auth
- **File Storage**: Vercel Blob
- **UI Components**: Radix UI primitives
- **Localization**: Full Czech language support (UI, forms, messages)

## 📋 Prerequisites

Before running this project, you need:

1. **Node.js** (v18 or higher)
2. **npm** package manager
3. **Supabase account** and project
4. **Vercel account** (for Blob storage)

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd kydy
npm install --legacy-peer-deps
```

### 2. Environment Setup

Create a `.env.local` file in the project root with the following variables:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your-supabase-project-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key

# Optional: For development redirects
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXT_PUBLIC_DEV_SUPABASE_REDIRECT_URL=http://localhost:3000/auth/callback

# Vercel Blob Storage Token (for file uploads)
BLOB_READ_WRITE_TOKEN=your-vercel-blob-token
```

### 3. Database Setup

Run the following SQL scripts in your Supabase SQL Editor:

1. **Create Tables** (`scripts/01-create-tables.sql`)
2. **Seed Political Parties** (`scripts/02-seed-parties.sql`)
3. **Create Functions & Triggers** (`scripts/03-create-functions.sql`)

See `SETUP-INSTRUCTIONS.md` for detailed database setup instructions.

### 4. Start Development Server

```bash
npm run dev
```

Visit http://localhost:3000 to see the application.

## 📁 Project Structure

```
kydy/
├── app/                    # Next.js app directory
│   ├── api/               # API routes
│   │   ├── upload/        # File upload endpoint
│   │   ├── posters/       # Poster CRUD operations
│   │   ├── comments/      # Comments API
│   │   └── ratings/       # Ratings API
│   ├── auth/              # Authentication pages
│   ├── dashboard/         # User dashboard
│   ├── gallery/           # Poster gallery
│   ├── poster/[id]/       # Individual poster pages
│   └── upload/            # Upload form page
├── components/            # Reusable React components
├── lib/                   # Utility libraries
│   ├── supabase/         # Supabase client configuration
│   └── actions.ts        # Server actions
├── scripts/              # Database setup scripts
└── .env.local           # Environment variables (create this)
```

## 🔐 Environment Variables Explained

### Required Variables

| Variable | Description | How to Get |
|----------|-------------|------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase project URL | Supabase Dashboard → Settings → API |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous/public key | Supabase Dashboard → Settings → API |
| `BLOB_READ_WRITE_TOKEN` | Vercel Blob storage token | Vercel Dashboard → Storage → Create Token |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_SITE_URL` | Your site URL | `http://localhost:3000` |
| `NEXT_PUBLIC_DEV_SUPABASE_REDIRECT_URL` | Auth redirect URL | `http://localhost:3000/auth/callback` |

## 🗄️ Database Schema

The application uses the following main tables:

- **`profiles`** - User profiles (auto-created on signup)
- **`political_parties`** - Political party data with colors
- **`posters`** - Uploaded poster metadata and files
- **`comments`** - User comments on posters
- **`ratings`** - User ratings (1-5 stars) for posters

All tables include Row Level Security (RLS) policies for data protection.

## 🎮 How to Use

### For Users

1. **Sign Up/Login** - Create an account or login (all in Czech)
2. **Upload Posters** - Go to `/upload` to add new political posters
3. **Browse Gallery** - View all posters at `/gallery`
4. **Rate & Comment** - Interact with posters on individual poster pages
5. **Dashboard** - View your uploaded posters at `/dashboard`

**Note**: All user interface elements, forms, buttons, and messages are displayed in Czech language for a native user experience.

### For Developers

#### Adding New Political Parties

Add entries to the `political_parties` table:

```sql
INSERT INTO political_parties (name, color_hex) 
VALUES ('New Party', '#FF5733');
```

#### Customizing Upload Logic

Edit `app/api/upload/route.ts` to modify file upload behavior.

#### Modifying UI Components

Components are in the `components/` directory using Radix UI primitives.

## 🛠️ Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint
```

## 🔧 Troubleshooting

### Common Issues

1. **"Vercel Blob: No token found"**
   - Ensure `BLOB_READ_WRITE_TOKEN` is set in `.env.local`
   - Restart the dev server after adding the token

2. **"Could not find table 'posters'"**
   - Run the database setup scripts in Supabase SQL Editor
   - Check Supabase connection and permissions

3. **"Cannot read properties of undefined"**
   - Verify all Supabase environment variables are correct
   - Check network connectivity to Supabase

4. **Auth redirect issues**
   - Verify `NEXT_PUBLIC_DEV_SUPABASE_REDIRECT_URL` matches your Supabase Auth settings
   - Check Supabase Auth → URL Configuration

### Environment Variable Validation

The app includes built-in validation for required environment variables. Check the browser console and server logs for configuration issues.

## 📦 Dependencies

### Main Dependencies
- **Next.js 15** - React framework
- **React 19** - UI library
- **TypeScript** - Type safety
- **Supabase** - Backend-as-a-Service
- **Vercel Blob** - File storage
- **TailwindCSS** - Styling
- **Radix UI** - UI primitives

### Development Dependencies
- **ESLint** - Code linting
- **PostCSS** - CSS processing

## 🚀 Deployment

### Vercel Deployment

1. Push your code to GitHub
2. Connect to Vercel
3. Add environment variables in Vercel dashboard
4. Deploy

### Environment Variables for Production

For production deployment, set the same environment variables with production values:
- Use your production Supabase project
- Use your production domain for site URLs
- Keep the same Vercel Blob token (or create a production one)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review `SETUP-INSTRUCTIONS.md` for detailed setup help
3. Check Supabase and Vercel documentation
4. Create an issue in the repository

---

**Built with ❤️ for democratic participation and political transparency in the Czech Republic.**

---

## 🇨🇿 Czech Language Features

This platform is fully localized for Czech users:

- **Native Czech Interface**: All menus, buttons, forms, and navigation in Czech
- **Czech Content Context**: Designed for sharing Czech political posters and campaigns  
- **Proper Czech Grammar**: Correct pluralization, formal/informal tone, and natural phrasing
- **Local Date Formats**: Czech date and time formatting throughout the application
- **Czech Political Parties**: Pre-configured for Czech political landscape
- **Responsive Czech Text**: All UI components properly handle Czech language characters and text length
