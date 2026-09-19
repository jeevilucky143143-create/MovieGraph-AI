"""Explainable Graph-based Recommendation Engine for MovieGraph AI.

Calculates graph relationship paths (shared actors, same director, multi-hop connections)
and produces explainable recommendation cards with exact, factual reasons.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from database.neo4j_client import Neo4jClient
from data.movies_data import MOVIES, get_all_movie_titles


@dataclass
class MovieRecommendation:
    """Represents a single explainable movie recommendation."""
    title: str
    released: int
    tagline: str
    score: int
    reasons: List[str]
    primary_reason: str
    shared_actors: List[str]
    directors: List[str]
    palette_tone: str  # 'lavender', 'sage', 'peach', 'powder_blue'


PASTEL_PALETTES = ["lavender", "sage", "peach", "powder_blue"]


class MovieRecommender:
    """Generates explainable movie recommendations based on graph connectivity."""

    def __init__(self, neo4j_client: Optional[Neo4jClient] = None):
        self.client = neo4j_client or Neo4jClient()

    def recommend(
        self,
        movie_title: str,
        mode: str = "Graph-based Discovery",
        limit: int = 6,
    ) -> List[MovieRecommendation]:
        """Generates recommendations for a target movie based on selected graph mode.

        Modes:
          - 'Shared Actors': Focuses on overlapping cast members.
          - 'Same Director': Focuses on filmography of the same filmmaker.
          - 'Connected Movies': Discovers movies sharing actors or directors.
          - 'Graph-based Discovery': Hybrid weighted graph scoring.

        Args:
            movie_title: Target movie title.
            mode: Filtering/exploration mode.
            limit: Maximum recommendations to return.

        Returns:
            List of MovieRecommendation objects with verified explanation reasons.
        """
        # Resolve target movie title
        target_title = self.client._find_matching_movie(movie_title)
        if not target_title or target_title not in MOVIES:
            return []

        target_data = MOVIES[target_title]
        target_actors = {a["name"] for a in target_data["actors"]}
        target_directors = set(target_data["directors"])

        candidates: List[MovieRecommendation] = []

        for other_title, other_data in MOVIES.items():
            if other_title == target_title:
                continue

            other_actors = {a["name"] for a in other_data["actors"]}
            other_directors = set(other_data["directors"])

            shared_actors = sorted(list(target_actors.intersection(other_actors)))
            same_directors = sorted(list(target_directors.intersection(other_directors)))

            # Check mode filters
            if mode == "Shared Actors" and not shared_actors:
                continue
            if mode == "Same Director" and not same_directors:
                continue
            if mode in ["Connected Movies", "Graph-based Discovery"] and not (shared_actors or same_directors):
                continue

            # Calculate graph score
            # Shared Actor = 2 points each, Same Director = 3 points each
            actor_score = len(shared_actors) * 2
            director_score = len(same_directors) * 3
            total_score = actor_score + director_score

            reasons: List[str] = []
            if same_directors:
                reasons.append(f"Directed by the same filmmaker ({', '.join(same_directors)})")
            if shared_actors:
                if len(shared_actors) == 1:
                    reasons.append(f"Shares actor {shared_actors[0]}")
                else:
                    reasons.append(f"Shares {len(shared_actors)} actors: {', '.join(shared_actors)}")

            primary_reason = reasons[0] if reasons else "Connected through graph relationships"

            candidates.append(
                MovieRecommendation(
                    title=other_title,
                    released=other_data.get("released", 0),
                    tagline=other_data.get("tagline", ""),
                    score=total_score,
                    reasons=reasons,
                    primary_reason=primary_reason,
                    shared_actors=shared_actors,
                    directors=other_data.get("directors", []),
                    palette_tone="lavender",  # dynamically assigned below
                )
            )

        # Sort by total graph connection score, then by release year descending
        candidates.sort(key=lambda r: (r.score, r.released), reverse=True)

        results = candidates[:limit]
        # Assign alternating pastel tones for visual harmony
        for i, rec in enumerate(results):
            rec.palette_tone = PASTEL_PALETTES[i % len(PASTEL_PALETTES)]

        return results
