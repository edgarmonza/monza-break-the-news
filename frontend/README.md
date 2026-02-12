# Frontend - Colombia News

Next.js 14 frontend para el agregador de noticias colombianas con IA.

## Stack Tecnológico

- **Next.js 14**: Framework React con App Router
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first CSS
- **TanStack Query**: Data fetching y cache
- **Framer Motion**: Animaciones
- **date-fns**: Formateo de fechas

## Setup

### 1. Instalar Dependencias

```bash
cd frontend
npm install
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env.local
```

Edita `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Iniciar Desarrollo

```bash
npm run dev
```

Abre http://localhost:3000

## Estructura

```
frontend/
├── app/
│   ├── layout.tsx          # Layout principal
│   ├── page.tsx            # Homepage con feed
│   ├── providers.tsx       # React Query provider
│   └── globals.css         # Estilos globales
│
├── components/
│   ├── Navbar.tsx          # Barra de navegación
│   ├── ThreadCard.tsx      # Card de thread
│   └── ThreadModal.tsx     # Modal con detalle + chat
│
└── lib/
    ├── types.ts            # TypeScript types
    └── api.ts              # API client
```

## Componentes

### ThreadCard

Card que muestra un thread en el feed.

**Props:**
- `thread`: Thread object
- `onClick`: Handler al hacer click

**Características:**
- Emoji según trending score (🔥 📈 📊 📰)
- Resumen truncado
- Contador de artículos
- Timestamp relativo

### ThreadModal

Modal full-screen con detalle del thread y chat RAG.

**Props:**
- `threadId`: ID del thread
- `onClose`: Handler para cerrar

**Características:**
- Detalle completo del thread
- Lista de artículos fuente
- Preguntas sugeridas clickeables
- Chat RAG integrado
- Historial de conversación
- Auto-scroll al enviar mensaje

### Navbar

Barra de navegación fija en el top.

## API Client

El API client (`lib/api.ts`) expone estas funciones:

```typescript
api.getFeed(params)      // Get paginated feed
api.getThread(id)        // Get thread detail
api.chat(request)        // Chat RAG
api.search(query)        // Search articles
api.health()             // Health check
```

Todas retornan Promises tipadas con TypeScript.

## Infinite Scroll

Implementado con:
- TanStack Query `useInfiniteQuery`
- Intersection Observer API
- Carga automática al llegar al final
- Loading states

## Chat RAG

Características:
- Preguntas sugeridas (generadas por IA)
- Chat interactivo sobre el thread
- Cita fuentes automáticamente
- Loading states durante generación
- Historial de conversación
- Auto-scroll

## Estilos

### Tailwind CSS

Configurado con:
- Custom animations (fade-in, slide-up)
- Custom scrollbar
- Dark mode ready (prefers-color-scheme)

### Animaciones

Framer Motion para:
- Fade-in de modals
- Transitions suaves
- Exit animations

## Deploy en Vercel

### 1. Push a GitHub

```bash
git add .
git commit -m "Frontend completo"
git push
```

### 2. Importar en Vercel

1. Ve a [vercel.com](https://vercel.com)
2. Click "Import Project"
3. Selecciona tu repo
4. Framework: Next.js (detectado automáticamente)
5. Root Directory: `frontend`

### 3. Environment Variables

En Vercel, agrega:
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

### 4. Deploy

Click "Deploy" - toma ~2 minutos

Tu app estará en: `https://tu-app.vercel.app`

## Troubleshooting

### Error: Cannot connect to API

Verifica:
- Backend corriendo en `http://localhost:8000`
- `NEXT_PUBLIC_API_URL` correcta en `.env.local`
- CORS configurado en backend

### Feed vacío

Causa: No hay threads en la BD

Solución:
```bash
cd backend
python run_pipeline_to_db.py
```

### TypeScript errors

```bash
npm run lint
```

### Build errors

```bash
rm -rf .next
npm run build
```

## Scripts

```bash
npm run dev      # Development server
npm run build    # Production build
npm run start    # Production server
npm run lint     # ESLint
```

## Performance

- Server Components por defecto
- Client Components solo donde necesario
- TanStack Query cache automático
- Infinite scroll sin re-renders innecesarios
- Images optimizadas (Next.js Image)

## Próximas Mejoras

- [ ] Search bar en navbar
- [ ] Filtros por fuente
- [ ] Share threads (copiar link)
- [ ] Dark mode toggle
- [ ] PWA (offline support)
- [ ] Notifications (new threads)

---

**Documentación completa:** Ver [FASE4_COMPLETADA.md](../FASE4_COMPLETADA.md)
