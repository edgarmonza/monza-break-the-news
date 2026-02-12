"""
Servicio para calcular trending scores de threads
"""
from typing import List
from datetime import datetime, timedelta
import logging
import math
from models.article import Article, Thread

logger = logging.getLogger(__name__)


class TrendingService:
    """Calcula scores de relevancia/trending para threads"""

    def __init__(self):
        # Pesos para el cálculo del score
        self.weight_recency = 0.4  # Qué tan reciente es
        self.weight_volume = 0.3   # Cantidad de artículos
        self.weight_diversity = 0.2  # Diversidad de fuentes
        self.weight_velocity = 0.1  # Velocidad de publicación

    def calculate_trending_score(
        self,
        articles: List[Article],
        reference_time: datetime = None
    ) -> float:
        """
        Calcula un score de trending (0.0 a 1.0)

        Factores considerados:
        1. Recencia: artículos más nuevos = mayor score
        2. Volumen: más artículos = mayor score
        3. Diversidad: más fuentes diferentes = mayor score
        4. Velocidad: artículos publicados en corto tiempo = mayor score

        Returns:
            Float entre 0.0 y 1.0
        """
        if not articles:
            return 0.0

        reference_time = reference_time or datetime.utcnow()

        # Calcular componentes del score
        recency_score = self._calculate_recency_score(articles, reference_time)
        volume_score = self._calculate_volume_score(articles)
        diversity_score = self._calculate_diversity_score(articles)
        velocity_score = self._calculate_velocity_score(articles)

        # Score ponderado
        total_score = (
            recency_score * self.weight_recency +
            volume_score * self.weight_volume +
            diversity_score * self.weight_diversity +
            velocity_score * self.weight_velocity
        )

        logger.debug(
            f"Trending score: {total_score:.3f} "
            f"(recency={recency_score:.2f}, volume={volume_score:.2f}, "
            f"diversity={diversity_score:.2f}, velocity={velocity_score:.2f})"
        )

        return round(total_score, 3)

    def _calculate_recency_score(
        self,
        articles: List[Article],
        reference_time: datetime
    ) -> float:
        """
        Score basado en qué tan recientes son los artículos

        Decay exponencial: artículos de hace 24h tienen score alto,
        después de 7 días el score es muy bajo
        """
        dates = [a.published_at or a.scraped_at for a in articles]
        dates = [d for d in dates if d]  # Filtrar None

        if not dates:
            return 0.5

        # Normalize all dates to naive UTC for safe comparison
        normalized = []
        for d in dates:
            if d.tzinfo is not None:
                d = d.replace(tzinfo=None)
            normalized.append(d)

        most_recent = max(normalized)

        ref = reference_time
        if ref.tzinfo is not None:
            ref = ref.replace(tzinfo=None)

        hours_ago = (ref - most_recent).total_seconds() / 3600

        # Decay exponencial (half-life de 24 horas)
        half_life_hours = 24
        decay_factor = 0.5 ** (hours_ago / half_life_hours)

        # Normalizar a 0-1
        return min(1.0, decay_factor)

    def _calculate_volume_score(self, articles: List[Article]) -> float:
        """
        Score basado en cantidad de artículos

        2 artículos = mínimo aceptable (0.3)
        5 artículos = score medio (0.5)
        10+ artículos = score alto (0.8+)
        """
        n_articles = len(articles)

        # Función logarítmica para suavizar
        # log_10(n) normalizado
        if n_articles <= 1:
            return 0.0
        elif n_articles >= 20:
            return 1.0
        else:
            # Escala logarítmica
            score = math.log10(n_articles) / math.log10(20)
            return min(1.0, score)

    def _calculate_diversity_score(self, articles: List[Article]) -> float:
        """
        Score basado en diversidad de fuentes

        1 fuente = 0.3 (poca confianza)
        2 fuentes = 0.6
        3+ fuentes = 1.0 (alta confianza)
        """
        unique_sources = set(a.source for a in articles)
        n_sources = len(unique_sources)

        if n_sources == 1:
            return 0.3
        elif n_sources == 2:
            return 0.6
        else:
            return 1.0

    def _calculate_velocity_score(self, articles: List[Article]) -> float:
        """
        Score basado en velocidad de publicación

        Muchos artículos en poco tiempo = "breaking news" = score alto
        Artículos distribuidos en días = score bajo
        """
        dates = [a.published_at or a.scraped_at for a in articles]
        dates = [d.replace(tzinfo=None) if d and d.tzinfo else d for d in dates]
        dates = [d for d in dates if d]

        if len(dates) < 2:
            return 0.5

        # Calcular span de tiempo
        earliest = min(dates)
        latest = max(dates)
        time_span_hours = (latest - earliest).total_seconds() / 3600

        # Artículos por hora
        if time_span_hours < 0.1:  # Menos de 6 minutos
            return 1.0

        articles_per_hour = len(articles) / time_span_hours

        # Normalizar
        # 5+ artículos/hora = muy rápido (1.0)
        # 1 artículo/hora = normal (0.5)
        # <0.2 artículos/hora = lento (0.2)
        if articles_per_hour >= 5:
            return 1.0
        elif articles_per_hour >= 1:
            return 0.7
        elif articles_per_hour >= 0.5:
            return 0.5
        else:
            return 0.3

    def rank_threads(self, threads: List[Thread]) -> List[Thread]:
        """
        Ordena threads por trending score (descendente)

        Returns:
            Lista de threads ordenada
        """
        return sorted(
            threads,
            key=lambda t: t.trending_score,
            reverse=True
        )

    def get_trending_category(self, score: float) -> str:
        """
        Categoriza un thread basado en su score

        Returns:
            'hot', 'trending', 'active', o 'normal'
        """
        if score >= 0.8:
            return 'hot'  # 🔥 Breaking news
        elif score >= 0.6:
            return 'trending'  # 📈 En auge
        elif score >= 0.4:
            return 'active'  # 📊 Activo
        else:
            return 'normal'  # 📰 Normal

    def calculate_decay_adjusted_score(
        self,
        current_score: float,
        created_at: datetime,
        reference_time: datetime = None
    ) -> float:
        """
        Ajusta un score existente aplicando decay temporal

        Útil para actualizar scores de threads antiguos sin recalcular todo
        """
        reference_time = reference_time or datetime.utcnow()
        # Normalize timezones
        ref = reference_time.replace(tzinfo=None) if reference_time.tzinfo else reference_time
        created = created_at.replace(tzinfo=None) if created_at.tzinfo else created_at
        hours_since_creation = (ref - created).total_seconds() / 3600

        # Decay exponencial (half-life de 48 horas)
        half_life_hours = 48
        decay_factor = 0.5 ** (hours_since_creation / half_life_hours)

        return current_score * decay_factor

    def should_boost_score(self, articles: List[Article]) -> tuple[bool, float]:
        """
        Determina si un thread merece un boost especial

        Casos especiales:
        - Todos los artículos de las últimas 2 horas (breaking news)
        - 5+ fuentes diferentes (alta cobertura)
        - Keywords importantes (gobierno, presidente, crisis)

        Returns:
            (should_boost: bool, boost_multiplier: float)
        """
        # Check 1: Breaking news (últimas 2 horas)
        now = datetime.utcnow()
        dates = [a.published_at or a.scraped_at for a in articles]
        dates = [d.replace(tzinfo=None) if d and d.tzinfo else d for d in dates]
        dates = [d for d in dates if d]

        if dates:
            most_recent = max(dates)
            hours_ago = (now - most_recent).total_seconds() / 3600

            if hours_ago < 2 and len(articles) >= 5:
                return True, 1.3  # 30% boost

        # Check 2: Alta diversidad de fuentes
        unique_sources = set(a.source for a in articles)
        if len(unique_sources) >= 4:
            return True, 1.2  # 20% boost

        # Check 3: Keywords importantes
        important_keywords = [
            'presidente', 'gobierno', 'crisis', 'reforma',
            'emergencia', 'congreso', 'petro', 'urgent'
        ]

        titles_combined = ' '.join([a.title.lower() for a in articles])
        keyword_matches = sum(
            1 for kw in important_keywords if kw in titles_combined
        )

        if keyword_matches >= 3:
            return True, 1.15  # 15% boost

        return False, 1.0
