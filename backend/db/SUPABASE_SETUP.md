# 🗄️ Setup de Supabase

Guía para configurar la base de datos vectorial con Supabase.

## 1. Crear Proyecto en Supabase

1. Ve a [supabase.com](https://supabase.com)
2. Sign up / Login
3. Click "New Project"
4. Configuración:
   - **Name**: colombia-news
   - **Database Password**: (guárdala de forma segura)
   - **Region**: South America (São Paulo) - más cercano a Colombia
   - **Plan**: Free (suficiente para desarrollo)

5. Espera ~2 minutos mientras se crea el proyecto

## 2. Obtener Credenciales

Una vez creado el proyecto:

1. Ve a **Settings** → **API**
2. Copia:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

3. Agrega a tu `.env`:
```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 3. Ejecutar Migraciones SQL

### Opción A: SQL Editor (Recomendado)

1. En Supabase, ve a **SQL Editor**
2. Click "New query"
3. Copia y pega el contenido de `db/migrations/001_initial_schema.sql`
4. Click "Run"
5. Repite con `002_vector_search_function.sql`

### Opción B: psql (Avanzado)

```bash
# Obtener connection string
# Settings → Database → Connection string → URI

psql "postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres"

# Ejecutar migraciones
\i db/migrations/001_initial_schema.sql
\i db/migrations/002_vector_search_function.sql
```

## 4. Verificar Instalación

### Check pgvector

En SQL Editor:

```sql
-- Verificar extensión pgvector
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Debe retornar una fila
```

### Check tablas

```sql
-- Listar tablas
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

-- Debe mostrar: articles, threads, thread_articles, thread_questions
```

### Check índices vectoriales

```sql
-- Verificar índice HNSW
SELECT indexname FROM pg_indexes
WHERE indexname = 'idx_articles_embedding';

-- Debe retornar 1 fila
```

## 5. Configurar Row Level Security (Opcional)

Para desarrollo, puedes desactivar RLS temporalmente:

```sql
-- Desactivar RLS en todas las tablas (solo dev)
ALTER TABLE articles DISABLE ROW LEVEL SECURITY;
ALTER TABLE threads DISABLE ROW LEVEL SECURITY;
ALTER TABLE thread_articles DISABLE ROW LEVEL SECURITY;
ALTER TABLE thread_questions DISABLE ROW LEVEL SECURITY;
```

⚠️ **Producción**: Configura políticas RLS apropiadas.

## 6. Probar Conexión

```bash
cd backend
python -c "from db import db; import asyncio; print('✅ OK' if asyncio.run(db.health_check()) else '❌ Error')"
```

## Troubleshooting

### Error: "extension 'vector' not available"

Solución:
1. Ve a **Database** → **Extensions**
2. Busca "vector"
3. Click "Enable"

### Error: "function match_articles does not exist"

Solución:
- Ejecuta la migración `002_vector_search_function.sql`

### Error de conexión

Verifica:
- SUPABASE_URL es correcta (incluye https://)
- SUPABASE_KEY es la **anon key**, no la service_role key
- Tu IP está permitida (Supabase free plan permite todas las IPs)

### Límites del Plan Free

- **Storage**: 500 MB
- **Bandwidth**: 1 GB/mes (luego pausa)
- **Database size**: 500 MB
- **API requests**: Ilimitadas

Para producción, considera Pro plan ($25/mes).

## Estructura de Datos Final

```
articles (tabla principal)
├── id (uuid)
├── url (text, unique)
├── title (text)
├── content (text)
├── embedding (vector 1536D) ← pgvector
├── source, author, published_at
└── timestamps

threads (historias agregadas)
├── id (uuid)
├── title_id (text, '@Handle')
├── display_title, summary
├── trending_score (float)
└── timestamps

thread_articles (relación N:M)
├── thread_id → threads
├── article_id → articles
└── position (orden)

thread_questions (preguntas sugeridas)
├── thread_id → threads
├── question (text)
└── position
```

## Queries Útiles

### Ver threads con más artículos

```sql
SELECT
    t.title_id,
    t.trending_score,
    COUNT(ta.article_id) as article_count
FROM threads t
JOIN thread_articles ta ON t.id = ta.thread_id
GROUP BY t.id, t.title_id, t.trending_score
ORDER BY article_count DESC;
```

### Buscar artículos por similaridad

```sql
SELECT * FROM match_articles(
    query_embedding := (SELECT embedding FROM articles LIMIT 1),
    match_threshold := 0.7,
    match_count := 10
);
```

### Estadísticas generales

```sql
SELECT
    (SELECT COUNT(*) FROM articles) as total_articles,
    (SELECT COUNT(*) FROM threads) as total_threads,
    (SELECT AVG(trending_score) FROM threads) as avg_score;
```

---

**Próximo paso:** Ejecutar `python backend/run_pipeline_to_db.py` para poblar la BD.
