# 🎨 Company Research Agent - UI

**Modern React UI built with shadcn/ui**

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd agents/company_research/ui
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The UI will be available at `http://localhost:3000`

### 3. Build for Production

```bash
npm run build
```

---

## 📦 Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Lucide React** - Icons
- **Axios** - HTTP client

---

## 🎨 Features

### ✅ File Upload
- Drag & drop Excel files
- Support for .xlsx, .xls, .csv
- File validation

### ✅ Field Configuration
- Configure which fields to extract
- Visual field selection
- Real-time preview

### ✅ Gap Analysis
- Visual data completeness overview
- Missing fields breakdown
- Completion rate tracking

### ✅ Research Progress
- Real-time progress tracking
- Activity log
- Statistics dashboard

### ✅ Results Table
- Enriched company data display
- Export to Excel
- Detailed field view

---

## 🏗️ Project Structure

```
ui/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── progress.tsx
│   │   │   └── checkbox.tsx
│   │   │
│   │   ├── FileUpload.tsx        # File upload component
│   │   ├── FieldConfiguration.tsx # Field config component
│   │   ├── GapAnalysis.tsx       # Gap analysis display
│   │   ├── ResearchProgress.tsx  # Progress tracking
│   │   └── ResultsTable.tsx      # Results display
│   │
│   ├── lib/
│   │   └── utils.ts         # Utility functions
│   │
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
│
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

---

## 🔌 API Integration

The UI connects to the backend API at `http://localhost:8000` via proxy.

### Endpoints Used:

- `POST /company/upload_excel` - Upload Excel file
- `POST /company/configure_fields` - Configure extraction fields
- `POST /company/research` - Start research process
- `POST /company/export` - Export enriched data

---

## 🎨 Customization

### Colors

Edit `tailwind.config.js` to customize the color scheme:

```js
theme: {
  extend: {
    colors: {
      primary: "hsl(var(--primary))",
      // ... more colors
    }
  }
}
```

### Components

All shadcn/ui components are in `src/components/ui/` and can be customized.

---

## 📝 Development

### Add New shadcn/ui Components

```bash
npx shadcn@latest add [component-name]
```

### Lint Code

```bash
npm run lint
```

---

## 🚀 Deployment

### Deploy to Vercel

```bash
npm run build
vercel --prod
```

### Deploy to Netlify

```bash
npm run build
netlify deploy --prod --dir=dist
```

---

## 🔗 Links

- **shadcn/ui**: https://ui.shadcn.com
- **Tailwind CSS**: https://tailwindcss.com
- **Lucide Icons**: https://lucide.dev
- **Vite**: https://vite.dev

---

**Created:** 2026-01-27  
**Version:** 1.0.0

