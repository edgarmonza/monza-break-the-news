"""
Servicio LLM para generación de threads usando Claude
"""
from typing import List, Optional
import logging
import json
from anthropic import AsyncAnthropic
from config.settings import settings
from models.article import Article, ThreadMetadata

logger = logging.getLogger(__name__)


class LLMThreadService:
    """Genera metadata de threads usando Claude"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-3-haiku-20240307"

    async def generate_thread_metadata(
        self,
        articles: List[Article],
        max_articles_for_context: int = 10
    ) -> Optional[ThreadMetadata]:
        """
        Genera metadata completa de un thread: @handle, título, resumen y preguntas

        Args:
            articles: Lista de artículos del cluster
            max_articles_for_context: Máximo de artículos a incluir en el prompt

        Returns:
            ThreadMetadata o None si falla
        """
        if not articles:
            return None

        try:
            # Limitar artículos para no exceder token limit
            context_articles = articles[:max_articles_for_context]

            # Preparar contexto
            articles_text = self._format_articles_for_prompt(context_articles)

            # Prompt para Claude
            prompt = self._build_thread_generation_prompt(
                articles_text,
                len(articles)
            )

            logger.info(f"Generating thread metadata for {len(articles)} articles")

            # Llamada a Claude
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parsear respuesta JSON
            response_text = response.content[0].text
            metadata_dict = json.loads(response_text)

            # Validar y crear ThreadMetadata
            metadata = ThreadMetadata(
                title_id=metadata_dict['title_id'],
                display_title=metadata_dict['display_title'],
                summary=metadata_dict['summary'],
                suggested_questions=metadata_dict['suggested_questions']
            )

            logger.info(f"Generated thread: {metadata.title_id}")
            return metadata

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.debug(f"Response was: {response_text[:200]}")
            return None
        except Exception as e:
            logger.error(f"Error generating thread metadata: {str(e)}")
            return None

    def _format_articles_for_prompt(self, articles: List[Article]) -> str:
        """Formatea artículos para incluir en el prompt"""
        formatted = []

        for i, article in enumerate(articles, 1):
            # Incluir título, fuente y preview del contenido
            content_preview = article.content[:300] if article.content else ""

            formatted.append(
                f"{i}. [{article.source.upper()}] {article.title}\n"
                f"   {content_preview}..."
            )

        return "\n\n".join(formatted)

    def _build_thread_generation_prompt(
        self,
        articles_text: str,
        total_articles: int
    ) -> str:
        """Construye el prompt para generación de thread"""
        return f"""Eres un editor de noticias colombiano experto. Analiza estos {total_articles} artículos relacionados y crea un "Thread" (historia agregada).

ARTÍCULOS:
{articles_text}

INSTRUCCIONES:
1. **title_id**: Crea un @handle estilo Twitter (ej: @ReformaTributaria, @CrisisCafé).
   - Máximo 20 caracteres
   - Sin espacios, usa PascalCase
   - Descriptivo y memorable
   - Refleja el tema común de los artículos

2. **display_title**: Título claro y conciso (40-60 caracteres)
   - Estilo periodístico
   - Captura la esencia del tema

3. **summary**: Resumen en 2-3 oraciones (120-180 palabras)
   - Explica qué está pasando
   - Por qué es relevante
   - Contexto colombiano

4. **suggested_questions**: Array de exactamente 4 preguntas que un lector querría hacer
   - Pregunta 1: "¿Por qué es importante esto?"
   - Pregunta 2: Sobre contexto o antecedentes
   - Pregunta 3: Sobre opiniones o reacciones
   - Pregunta 4: Sobre implicaciones futuras
   - Cada pregunta: 8-15 palabras

RESPONDE SOLO CON JSON VÁLIDO (sin markdown):
{{
  "title_id": "@EjemploHandle",
  "display_title": "Título descriptivo del thread",
  "summary": "Resumen de 2-3 oraciones explicando qué está pasando y por qué importa...",
  "suggested_questions": [
    "¿Por qué es importante esto?",
    "¿Cuál es el contexto histórico?",
    "¿Qué opinan los expertos?",
    "¿Qué implicaciones tiene para Colombia?"
  ]
}}"""

    async def generate_answer_for_question(
        self,
        question: str,
        articles: List[Article],
        max_context_chars: int = 4000
    ) -> Optional[str]:
        """
        Genera respuesta a una pregunta usando artículos como contexto (RAG)

        Args:
            question: Pregunta del usuario
            articles: Artículos relevantes (ya filtrados por similitud)
            max_context_chars: Máximo de caracteres de contexto

        Returns:
            Respuesta generada o None
        """
        try:
            # Preparar contexto
            context = self._format_context_for_rag(articles, max_context_chars)

            prompt = f"""Eres un asistente experto en noticias de Colombia. Responde la pregunta usando SOLO la información de los artículos proporcionados.

ARTÍCULOS DE CONTEXTO:
{context}

PREGUNTA: {question}

INSTRUCCIONES:
- Responde en español de forma clara y concisa
- Usa solo información de los artículos
- Si la información no está en los artículos, di "No tengo información suficiente sobre eso en los artículos disponibles"
- Cita las fuentes cuando sea relevante (ej: "según El Tiempo...")
- Máximo 3 párrafos

RESPUESTA:"""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=800,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )

            answer = response.content[0].text
            logger.info(f"Generated answer for question: {question[:50]}...")

            return answer

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return None

    def _format_context_for_rag(
        self,
        articles: List[Article],
        max_chars: int
    ) -> str:
        """Formatea artículos para RAG, respetando límite de caracteres"""
        context_parts = []
        current_length = 0

        for article in articles:
            # Formato: [Fuente] Título\nContenido...
            article_text = (
                f"[{article.source.upper()}] {article.title}\n"
                f"{article.content}\n"
            )

            if current_length + len(article_text) > max_chars:
                # Truncar último artículo si es necesario
                remaining = max_chars - current_length
                if remaining > 200:  # Solo agregar si queda espacio razonable
                    article_text = article_text[:remaining] + "..."
                    context_parts.append(article_text)
                break

            context_parts.append(article_text)
            current_length += len(article_text)

        return "\n---\n".join(context_parts)

    async def generate_handle_only(
        self,
        articles: List[Article]
    ) -> Optional[str]:
        """
        Genera solo el @handle para un thread (más rápido)
        Útil para preview rápido
        """
        if not articles:
            return None

        try:
            titles = "\n".join([
                f"- {a.title}" for a in articles[:5]
            ])

            prompt = f"""Crea un @handle estilo Twitter para estos titulares de noticias colombianas:

{titles}

Reglas:
- Máximo 20 caracteres
- Sin espacios, usa PascalCase
- Descriptivo del tema común
- Ejemplos: @ReformaTributaria, @CrisisCafé, @DebatyPetro

Responde SOLO con el @handle (sin explicaciones):"""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=50,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            handle = response.content[0].text.strip()

            # Limpiar respuesta (quitar comillas, espacios, etc.)
            handle = handle.strip('"\'` \n')

            # Asegurar que empieza con @
            if not handle.startswith('@'):
                handle = '@' + handle

            return handle

        except Exception as e:
            logger.error(f"Error generating handle: {str(e)}")
            return None
