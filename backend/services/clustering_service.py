"""
Servicio de clustering semántico para agrupar artículos relacionados
"""
from typing import List, Dict, Tuple
import logging
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_distances
import numpy as np
from models.article import Article
from config.settings import settings

logger = logging.getLogger(__name__)


class ClusteringService:
    """Agrupa artículos similares en threads usando DBSCAN"""

    def __init__(self):
        self.eps = settings.clustering_eps  # 0.3 por defecto
        self.min_samples = settings.clustering_min_samples  # 2 por defecto

    def cluster_articles(
        self,
        articles: List[Article]
    ) -> Dict[int, List[Article]]:
        """
        Agrupa artículos similares usando DBSCAN sobre embeddings

        Args:
            articles: Lista de artículos con embeddings

        Returns:
            Dict donde key=cluster_id, value=lista de artículos
            cluster_id=-1 son outliers (artículos únicos sin match)
        """
        if not articles:
            logger.warning("No articles to cluster")
            return {}

        # Validar que todos los artículos tengan embeddings
        articles_with_embeddings = [
            a for a in articles if a.embedding is not None
        ]

        if len(articles_with_embeddings) < self.min_samples:
            logger.warning(
                f"Not enough articles with embeddings: {len(articles_with_embeddings)}"
            )
            return {}

        logger.info(f"Clustering {len(articles_with_embeddings)} articles")

        # Extraer embeddings como matriz numpy
        embeddings_matrix = np.array([
            article.embedding for article in articles_with_embeddings
        ])

        # Calcular distancias coseno
        # DBSCAN necesita una matriz de distancias, no similitudes
        distances = cosine_distances(embeddings_matrix)

        # Aplicar DBSCAN
        clustering = DBSCAN(
            eps=self.eps,
            min_samples=self.min_samples,
            metric='precomputed'  # Usamos distancias pre-calculadas
        )

        labels = clustering.fit_predict(distances)

        # Agrupar artículos por cluster
        clusters: Dict[int, List[Article]] = {}
        for article, label in zip(articles_with_embeddings, labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(article)

        # Log estadísticas
        n_clusters = len([k for k in clusters.keys() if k != -1])
        n_outliers = len(clusters.get(-1, []))

        logger.info(f"Clustering results:")
        logger.info(f"  • Clusters found: {n_clusters}")
        logger.info(f"  • Outliers: {n_outliers}")

        for cluster_id, cluster_articles in clusters.items():
            if cluster_id != -1:  # Skip outliers en el log
                logger.info(
                    f"  • Cluster {cluster_id}: {len(cluster_articles)} articles"
                )

        return clusters

    def get_cluster_statistics(
        self,
        clusters: Dict[int, List[Article]]
    ) -> Dict[int, Dict]:
        """
        Calcula estadísticas útiles de cada cluster

        Returns:
            Dict con stats: sources, time_range, avg_similarity, etc.
        """
        stats = {}

        for cluster_id, articles in clusters.items():
            if cluster_id == -1:  # Skip outliers
                continue

            # Sources únicas
            sources = list(set(a.source for a in articles))

            # Rango de tiempo - normalize to naive datetimes for comparison
            dates = []
            for a in articles:
                if a.published_at:
                    d = a.published_at
                    if d.tzinfo is not None:
                        d = d.replace(tzinfo=None)
                    dates.append(d)
            time_range = None
            if dates:
                time_range = {
                    'earliest': min(dates),
                    'latest': max(dates),
                    'span_hours': (max(dates) - min(dates)).total_seconds() / 3600
                }

            # Calcular similitud promedio intra-cluster
            avg_similarity = self._calculate_avg_similarity(articles)

            stats[cluster_id] = {
                'size': len(articles),
                'sources': sources,
                'n_sources': len(sources),
                'time_range': time_range,
                'avg_similarity': avg_similarity,
                'article_ids': [str(a.id) for a in articles]
            }

        return stats

    def _calculate_avg_similarity(self, articles: List[Article]) -> float:
        """Calcula similitud coseno promedio entre artículos del cluster"""
        if len(articles) < 2:
            return 1.0

        embeddings = [a.embedding for a in articles if a.embedding]
        if len(embeddings) < 2:
            return 0.0

        # Calcular todas las similitudes pairwise
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                vec1 = np.array(embeddings[i])
                vec2 = np.array(embeddings[j])

                # Similitud coseno = 1 - distancia coseno
                dot_product = np.dot(vec1, vec2)
                norm = np.linalg.norm(vec1) * np.linalg.norm(vec2)
                similarity = dot_product / norm if norm > 0 else 0
                similarities.append(similarity)

        return float(np.mean(similarities)) if similarities else 0.0

    def filter_valid_clusters(
        self,
        clusters: Dict[int, List[Article]],
        min_articles: int = 2,
        min_sources: int = 1
    ) -> Dict[int, List[Article]]:
        """
        Filtra clusters que no cumplen criterios mínimos

        Args:
            min_articles: Mínimo de artículos por cluster
            min_sources: Mínimo de fuentes diferentes
        """
        filtered = {}

        for cluster_id, articles in clusters.items():
            if cluster_id == -1:  # Skip outliers
                continue

            sources = set(a.source for a in articles)

            if len(articles) >= min_articles and len(sources) >= min_sources:
                filtered[cluster_id] = articles
            else:
                logger.debug(
                    f"Cluster {cluster_id} filtered out: "
                    f"{len(articles)} articles, {len(sources)} sources"
                )

        logger.info(
            f"Filtered {len(filtered)}/{len(clusters)-1} clusters "
            f"(min_articles={min_articles}, min_sources={min_sources})"
        )

        return filtered

    def get_representative_article(
        self,
        articles: List[Article]
    ) -> Article:
        """
        Encuentra el artículo más "central" del cluster
        (el que tiene mayor similitud promedio con los demás)
        """
        if len(articles) == 1:
            return articles[0]

        embeddings = [a.embedding for a in articles if a.embedding]
        if not embeddings:
            return articles[0]

        # Calcular similitud promedio de cada artículo con los demás
        avg_similarities = []
        for i, emb_i in enumerate(embeddings):
            similarities = []
            for j, emb_j in enumerate(embeddings):
                if i != j:
                    vec1 = np.array(emb_i)
                    vec2 = np.array(emb_j)
                    sim = np.dot(vec1, vec2) / (
                        np.linalg.norm(vec1) * np.linalg.norm(vec2)
                    )
                    similarities.append(sim)
            avg_similarities.append(np.mean(similarities))

        # Retornar el artículo con mayor similitud promedio
        most_central_idx = np.argmax(avg_similarities)
        return articles[most_central_idx]
