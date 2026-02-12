# 🏗️ Arquitectura del Sistema - Colombia News

## Diagrama General

```
┌─────────────────────────────────────────────────────────────────────┐
│                         COLOMBIA NEWS                                │
│                   Agregador de Noticias con IA                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────── FASE 1 (✅ COMPLETADA) ────────────────────────┐
│                                                                        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │  El Tiempo   │    │ El Espectador│    │    Semana    │          │
│  │  .com        │    │  .com        │    │    .com      │          │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘          │
│         │                    │                    │                   │
│         └────────────────────┼────────────────────┘                   │
│                              │                                        │
│                    ┌─────────▼─────────┐                             │
│                    │  Web Scrapers     │                             │
│                    │  ─────────────    │                             │
│                    │  • BeautifulSoup  │                             │
│                    │  • newspaper3k    │                             │
│                    │  • httpx          │                             │
│                    └─────────┬─────────┘                             │
│                              │                                        │
│                              │ ScrapedArticle[]                       │
│                              ▼                                        │
│                    ┌─────────────────┐                               │
│                    │ Content Extract │                               │
│                    │ ─────────────── │                               │
│                    │ • Title         │                               │
│                    │ • Full Content  │                               │
│                    │ • Author, Date  │                               │
│                    │ • Images        │                               │
│                    └─────────┬───────┘                               │
│                              │                                        │
│                              │ ArticleBase[]                          │
│                              ▼                                        │
│                    ┌─────────────────┐                               │
│                    │ Embedding Svc   │                               │
│                    │ ─────────────── │                               │
│                    │ OpenAI API      │                               │
│                    │ text-embed-3    │                               │
│                    │ 1536 dimensions │                               │
│                    └─────────┬───────┘                               │
│                              │                                        │
│                              ▼                                        │
│                      Article[embedding]                               │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘

┌─────────────────────── FASE 2 (⏳ PRÓXIMA) ──────────────────────────┐
│                                                                        │
│                   Article[embedding] (x120)                           │
│                              │                                        │
│                              ▼                                        │
│                    ┌─────────────────┐                               │
│                    │ Clustering Svc  │                               │
│                    │ ─────────────── │                               │
│                    │ DBSCAN          │                               │
│                    │ Cosine Distance │                               │
│                    │ eps=0.3         │                               │
│                    └─────────┬───────┘                               │
│                              │                                        │
│                              │ Grouped Articles                       │
│                              ▼                                        │
│                    ┌─────────────────┐                               │
│                    │  LLM Service    │                               │
│                    │  ────────────   │                               │
│                    │  Claude Sonnet  │                               │
│                    │  • @Handle      │                               │
│                    │  • Summary      │                               │
│                    │  • Questions    │                               │
│                    └─────────┬───────┘                               │
│                              │                                        │
│                              ▼                                        │
│                         Thread Objects                                │
│                    (@ReformaTributaria)                               │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘

┌─────────────────────── FASE 3 (⏳ FUTURA) ───────────────────────────┐
│                                                                        │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │              Supabase (PostgreSQL + pgvector)             │       │
│  │  ─────────────────────────────────────────────────────   │       │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────┐       │       │
│  │  │  articles  │  │  threads   │  │  questions   │       │       │
│  │  │  + vector  │  │  + scores  │  │  + prompts   │       │       │
│  │  └────────────┘  └────────────┘  └──────────────┘       │       │
│  └──────────────────────────┬───────────────────────────────┘       │
│                             │                                         │
│                             ▼                                         │
│                  ┌──────────────────┐                                │
│                  │   FastAPI REST   │                                │
│                  │   ────────────   │                                │
│                  │ GET  /api/feed   │                                │
│                  │ GET  /api/thread │                                │
│                  │ POST /api/chat   │                                │
│                  └─────────┬────────┘                                │
│                            │                                          │
│         ┌──────────────────┼──────────────────┐                     │
│         │                  │                  │                     │
│         ▼                  ▼                  ▼                     │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐                 │
│  │   Celery   │   │   Redis    │   │  RAG Chat  │                 │
│  │ Scraping   │   │   Cache    │   │  Claude    │                 │
│  │ Tasks      │   │            │   │  + Context │                 │
│  └────────────┘   └────────────┘   └────────────┘                 │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌─────────────────────── FASE 4 (⏳ FUTURA) ───────────────────────────┐
│                                                                        │
│                         Next.js 14 Frontend                           │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │                      Homepage / Feed                      │       │
│  │  ─────────────────────────────────────────────────────   │       │
│  │  ┌────────────────────────────────────────────────────┐  │       │
│  │  │  @ReformaTributaria                                │  │       │
│  │  │  Debate sobre nueva propuesta...                   │  │       │
│  │  │  15 artículos · 2h ago                             │  │       │
│  │  └────────────────────────────────────────────────────┘  │       │
│  │  ┌────────────────────────────────────────────────────┐  │       │
│  │  │  @EconomíaColombia                                 │  │       │
│  │  │  Dólar alcanza nuevo precio...                     │  │       │
│  │  │  8 artículos · 4h ago                              │  │       │
│  │  └────────────────────────────────────────────────────┘  │       │
│  │  [Infinite Scroll]                                        │       │
│  └──────────────────────────────────────────────────────────┘       │
│                             │                                         │
│                             │ Click Thread                            │
│                             ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │                   Thread Detail Modal                     │       │
│  │  ─────────────────────────────────────────────────────   │       │
│  │  Summary: ...                                             │       │
│  │                                                           │       │
│  │  Sources:                                                 │       │
│  │  [El Tiempo] [El Espectador] [Semana]                   │       │
│  │                                                           │       │
│  │  ┌─────────────────────────────────────────────┐        │       │
│  │  │ 💬 Chat                                      │        │       │
│  │  │ "¿Qué opinan los expertos?"                 │        │       │
│  │  │                                              │        │       │
│  │  │ [Suggested Questions...]                    │        │       │
│  │  └─────────────────────────────────────────────┘        │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

## Flujo de Datos - Fase 1 (Actual)

```
1. SCRAPING
   ┌─────────────────────────────────────────────┐
   │ Medios → Scrapers → ScrapedArticle[]       │
   │ (URLs, títulos, previews)                   │
   └─────────────────────────────────────────────┘
                      ↓
2. CONTENT EXTRACTION
   ┌─────────────────────────────────────────────┐
   │ newspaper3k → ArticleBase[]                │
   │ (contenido completo, metadata)              │
   └─────────────────────────────────────────────┘
                      ↓
3. EMBEDDING
   ┌─────────────────────────────────────────────┐
   │ OpenAI API → Article[embedding]            │
   │ (vectores 1536D para búsqueda semántica)   │
   └─────────────────────────────────────────────┘
```

## Flujo de Datos - Fase 2 (Próxima)

```
Article[embedding] (x120)
         ↓
1. CLUSTERING SEMÁNTICO
   ┌─────────────────────────────────────────────┐
   │ DBSCAN agrupa artículos similares          │
   │ → 10-15 clusters (threads)                  │
   └─────────────────────────────────────────────┘
         ↓
2. THREAD GENERATION
   ┌─────────────────────────────────────────────┐
   │ Claude Sonnet:                              │
   │ • Analiza artículos del cluster             │
   │ • Genera @Handle creativo                   │
   │ • Resume el tema común                      │
   │ • Crea 3-5 preguntas sugeridas              │
   └─────────────────────────────────────────────┘
         ↓
3. TRENDING SCORE
   ┌─────────────────────────────────────────────┐
   │ Calcula relevancia:                         │
   │ • Cantidad de artículos                     │
   │ • Recencia                                  │
   │ • Diversidad de fuentes                     │
   └─────────────────────────────────────────────┘
         ↓
   Thread Objects → Listos para API
```

## Tecnologías por Capa

### Scraping & Processing

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| HTTP Client | httpx | Requests asíncronos |
| HTML Parsing | BeautifulSoup | Extracción de elementos |
| Article Extract | newspaper3k | Contenido + metadata |
| Embeddings | OpenAI API | Vectorización semántica |
| Clustering | scikit-learn | Agrupación automática |
| LLM | Anthropic Claude | Generación de texto |

### API & Database (Fase 3)

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| API Framework | FastAPI | REST endpoints |
| Database | PostgreSQL | Datos estructurados |
| Vector Store | pgvector | Búsqueda semántica |
| Cache | Redis | Performance |
| Task Queue | Celery | Jobs asíncronos |
| Hosting | Railway/Render | Backend deployment |

### Frontend (Fase 4)

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| Framework | Next.js 14 | SSR + RSC |
| Styling | Tailwind CSS | Utility-first CSS |
| Components | shadcn/ui | UI primitives |
| State | Zustand | Client state |
| Queries | TanStack Query | Server state |
| Animations | Framer Motion | Transiciones |
| Hosting | Vercel | Frontend deployment |

## Patrones de Diseño

### 1. Strategy Pattern (Scrapers)

```python
# Cada scraper implementa la misma interfaz
class BaseScraper(ABC):
    @abstractmethod
    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        pass

# Intercambiables
scrapers = [ElTiempoScraper(), ElEspectadorScraper()]
```

### 2. Service Layer Pattern

```python
# Servicios encapsulan lógica de negocio
embedding_service = EmbeddingService()
clustering_service = ClusteringService()  # Fase 2
llm_service = LLMService()  # Fase 2
```

### 3. Repository Pattern (Fase 3)

```python
# Abstracción de acceso a datos
article_repo = ArticleRepository(db)
thread_repo = ThreadRepository(db)
```

## Escalabilidad

### Actual (Fase 1)
- ✅ Scrapers asíncronos (httpx + asyncio)
- ✅ Batch processing de embeddings
- ✅ Rate limiting implícito

### Futura (Fase 3-4)
- Redis cache para threads frecuentes
- Celery para scraping distribuido
- CDN para assets estáticos (Vercel)
- Database read replicas (Supabase)

## Seguridad

### Implementado
- ✅ Validación con Pydantic
- ✅ Configuración con variables de entorno
- ✅ No hardcoded secrets

### Por implementar (Fase 3)
- Rate limiting en API
- Authentication con Supabase Auth
- CORS configurado correctamente
- Input sanitization en chat

## Monitoreo (Fase 3+)

```python
# Métricas clave a trackear
- Artículos scrapeados/hora
- Tiempo de scraping por fuente
- Errores de scraping
- Uso de API (OpenAI, Claude)
- Latencia de endpoints
- Cache hit rate
```

## Costos Estimados (Producción)

| Servicio | Plan | Costo/mes |
|----------|------|-----------|
| OpenAI (embeddings) | Pay-as-go | ~$5-10 |
| Anthropic (LLM) | Pay-as-go | ~$10-20 |
| Supabase | Pro | $25 |
| Redis Cloud | Free | $0 |
| Vercel | Hobby | $0 |
| Backend Hosting | Basic | $5-10 |
| **TOTAL** | | **~$45-65** |

### Optimizaciones de costo:
- Cachear threads populares
- Batch embeddings
- Rate limit scraping
- CDN para reducir bandwidth

---

**Arquitectura diseñada para:**
- ✅ Escalabilidad horizontal
- ✅ Bajo acoplamiento
- ✅ Alta cohesión
- ✅ Testabilidad
- ✅ Mantenibilidad
