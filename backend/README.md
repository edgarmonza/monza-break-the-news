# Backend - Colombia News

Motor de scraping y procesamiento para agregador de noticias colombianas (clon de btw.co).

## Estructura del Proyecto

```
backend/
├── api/              # FastAPI endpoints (Fase 3)
├── config/           # Configuración y settings
├── db/               # Database schemas (Fase 3)
├── models/           # Modelos Pydantic
├── scrapers/         # Scrapers para medios colombianos
│   ├── base.py      # Clase base abstracta
│   ├── eltiempo.py  # Scraper El Tiempo
│   ├── elespectador.py  # Scraper El Espectador
│   └── semana.py    # Scraper Semana
├── services/         # Servicios (embeddings, LLM, clustering)
│   └── embedding_service.py
└── tests/            # Tests unitarios
```

## Instalación

### 1. Crear entorno virtual

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Instalar navegadores para Playwright

```bash
playwright install
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus API keys
```

Necesitas:
- `OPENAI_API_KEY`: Para embeddings (obtener en platform.openai.com)
- `ANTHROPIC_API_KEY`: Para LLM Claude (obtener en console.anthropic.com)

## Uso

### Probar Scrapers

```bash
python test_scrapers.py
```

Este script:
1. Scrape las páginas principales de El Tiempo, El Espectador y Semana
2. Muestra los primeros 5 artículos de cada medio
3. Extrae el contenido completo del primer artículo

### Ejemplo de Salida

```
============================================================
PROBANDO: El Tiempo
============================================================

✅ Artículos encontrados: 47

📰 Primeros 5 artículos:

1. Reforma tributaria: gobierno busca acuerdo con el Congreso
   URL: https://www.eltiempo.com/politica/...
   Source: eltiempo
   Imagen: https://www.eltiempo.com/files/...

2. ...
```

## Scrapers Disponibles

### 1. ElTiempoScraper

Scrape artículos de [eltiempo.com](https://www.eltiempo.com)

**Secciones:**
- Política
- Justicia
- Economía
- Colombia
- Mundo

**Uso:**

```python
from scrapers import ElTiempoScraper

scraper = ElTiempoScraper()
articles = await scraper.scrape_frontpage()

# Extraer contenido completo
full_article = await scraper.scrape_article_content(articles[0].url)
```

### 2. ElEspectadorScraper

Scrape artículos de [elespectador.com](https://www.elespectador.com)

**Secciones:**
- Noticias/Política
- Noticias/Judicial
- Noticias/Economía
- Noticias/Nacional
- Noticias/El Mundo

### 3. SemanaScraper

Scrape artículos de [semana.com](https://www.semana.com)

**Secciones:**
- Nación
- Economía
- Mundo
- Política

## Servicio de Embeddings

Genera vectores para búsqueda semántica usando OpenAI.

```python
from services import EmbeddingService
from models import ArticleBase

service = EmbeddingService()

# Embed un artículo
article = ArticleBase(
    url="https://...",
    title="Título del artículo",
    content="Contenido completo...",
    source="eltiempo"
)

article_with_embedding = await service.embed_article(article)

# Embed múltiples artículos (batch)
articles = [...]  # Lista de ArticleBase
embedded_articles = await service.embed_articles_batch(articles)
```

## Próximos Pasos (Fases 2-4)

### Fase 2: Clustering & Threads
- Implementar clustering semántico (DBSCAN)
- Generar threads con LLM (Claude)
- Crear sugerencias de preguntas

### Fase 3: API & Database
- Configurar Supabase (PostgreSQL + pgvector)
- Crear FastAPI endpoints
- Implementar RAG para chat

### Fase 4: Frontend
- Next.js 14 con Tailwind
- Feed infinito de threads
- Modal de chat interactivo

## Troubleshooting

### Error: playwright not installed
```bash
playwright install
```

### Error: No module named 'lxml'
```bash
pip install lxml
```

### Error: newspaper3k no funciona
Newspaper3k a veces tiene problemas. Alternativas:
- Usar solo BeautifulSoup + requests
- Migrar a `newspaper4k` (fork mantenido)

### Scrapers no encuentran artículos
Los sitios de noticias cambian su HTML frecuentemente. Verifica:
1. El sitio está accesible (abre en navegador)
2. Los selectores CSS/patrones necesitan actualización
3. Revisa los logs para ver qué está capturando

## Licencia

Este es un proyecto educativo para aprender sobre RAG y scraping de noticias.
