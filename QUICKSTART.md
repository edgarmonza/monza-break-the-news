# 🚀 Inicio Rápido - Colombia News

Guía de 5 minutos para empezar a usar el sistema de scraping.

## 📋 Pre-requisitos

- Python 3.11+ instalado
- Cuenta de OpenAI (para embeddings) - [platform.openai.com](https://platform.openai.com)
- Cuenta de Anthropic (para thread generation) - [console.anthropic.com](https://console.anthropic.com)

## ⚡ Setup en 3 Pasos

### 1. Instalar dependencias

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` y agrega tu API key de OpenAI:

```bash
# Fase 1 - Scraping (requerido)
OPENAI_API_KEY=sk-proj-xxxxx...

# Fase 2 - Thread Generation (requerido)
ANTHROPIC_API_KEY=sk-ant-xxxxx...

# Fase 3 - API & Database (opcional por ahora)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbG...
REDIS_URL=redis://localhost:6379/0
```

> **¿Dónde conseguir API keys?**
> - OpenAI: https://platform.openai.com/api-keys (~$0.02 por 100 artículos)
> - Anthropic: https://console.anthropic.com/settings/keys (~$0.10 por 10 threads)

### 3. Probar scrapers

```bash
python test_scrapers.py
```

## ✅ ¿Funcionó?

Deberías ver algo como:

```
============================================================
PROBANDO: El Tiempo
============================================================

✅ Artículos encontrados: 47

📰 Primeros 5 artículos:

1. Reforma tributaria: gobierno busca acuerdo con el Congreso
   URL: https://www.eltiempo.com/politica/...
   Source: eltiempo

🔍 Extrayendo contenido completo del primer artículo...
✅ Contenido extraído exitosamente
```

## 🎮 Explorar Ejemplos

```bash
python example_usage.py
```

Este script interactivo te permite:
1. Ver el pipeline completo (scraping + embeddings + similitud)
2. Scraping multi-fuente en paralelo
3. Búsqueda semántica con queries

## 🧪 Uso Programático

### Ejemplo básico:

```python
import asyncio
from scrapers import ElTiempoScraper
from services import EmbeddingService

async def main():
    # 1. Scrape noticias
    scraper = ElTiempoScraper()
    articles = await scraper.scrape_frontpage()
    print(f"Encontrados: {len(articles)} artículos")

    # 2. Extraer contenido completo
    full_article = await scraper.scrape_article_content(articles[0].url)
    print(f"Título: {full_article.title}")

    # 3. Generar embedding
    embedding_service = EmbeddingService()
    embedded = await embedding_service.embed_article(full_article)
    print(f"Embedding: {len(embedded.embedding)} dimensiones")

asyncio.run(main())
```

## 🔧 Troubleshooting

### Error: "playwright not installed"

```bash
playwright install
```

### Error: "OPENAI_API_KEY not found"

Asegúrate de que el archivo `.env` existe en `backend/` y contiene tu API key.

### No encuentra artículos

Los sitios web cambian frecuentemente. Si un scraper no encuentra artículos:
1. Verifica que el sitio está accesible
2. Revisa los logs para ver qué está pasando
3. Puede que necesites actualizar los selectores HTML

### ImportError o ModuleNotFoundError

Asegúrate de estar en el entorno virtual y haber instalado todas las dependencias:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 🚀 Fase 2: Thread Generation (NUEVO)

### Probar pipeline completo

```bash
python test_phase2.py
# Selecciona opción 1: Pipeline completo
```

Esto ejecutará:
1. Scraping de 3 fuentes (~60 artículos)
2. Clustering automático (agrupa similares)
3. Generación de threads con Claude
4. Cálculo de trending scores

**Output esperado:**

```
✅ THREADS GENERADOS: 8

1. 🔥 @ReformaTributaria
   📊 Score: 0.847
   📰 Título: Gobierno presenta nueva reforma tributaria
   📄 Artículos: 7
   📡 Fuentes: eltiempo, elespectador, semana

   💬 Resumen:
   El gobierno colombiano anunció una reforma...

   ❓ Preguntas sugeridas:
      • ¿Por qué es importante esto?
      • ¿Cuál es el contexto histórico?
      ...
```

**Tiempo de ejecución:** ~2 minutos

### Opciones de prueba

```bash
python test_phase2.py

1. Pipeline completo (scraping → threads)
2. Solo clustering (sin LLM, más rápido)
3. Solo LLM (con artículos de ejemplo)
4. Todas las pruebas
```

## 📚 Próximos Pasos

1. **Explora el código**: Revisa [backend/README.md](backend/README.md)
2. **Lee la doc de Fase 2**: [FASE2_COMPLETADA.md](FASE2_COMPLETADA.md)
3. **Fase 3**: API REST con FastAPI (próxima)
4. **Fase 4**: Frontend con Next.js

## 💡 Tips

- Los scrapers están diseñados para ser resilientes y manejar cambios en HTML
- Newspaper3k extrae el contenido principal automáticamente
- Los embeddings permiten búsqueda semántica (no solo por keywords)
- Cada scraper puede personalizarse modificando las secciones

## 🆘 Ayuda

Si tienes problemas:
1. Revisa los logs: el código usa `logging` extensivamente
2. Lee [backend/README.md](backend/README.md) para más detalles
3. Verifica que todas las dependencias estén instaladas

## 🎉 ¡Listo!

Ya tienes un sistema funcional de scraping de noticias colombianas con embeddings.

En la Fase 2 implementaremos:
- Clustering automático para agrupar noticias relacionadas
- Generación de threads con @handles como @ReformaTributaria
- Sugerencias de preguntas con IA

---

**¿Todo funcionando?** Continúa con la Fase 2 o explora el código en `backend/`.
