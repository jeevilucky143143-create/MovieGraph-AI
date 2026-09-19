"""Context Builder Module for MovieGraph RAG.

Converts retrieved graph records from Neo4j into structured, factual text
blocks and UI entity badges designed for strict LLM grounding.
"""

from typing import Dict, List, Any, Tuple
from rag.retriever import RetrievalResult


class ContextBuilder:
    """Builds structured factual context from retrieved Neo4j graph records."""

    @staticmethod
    def build_context(retrieval: RetrievalResult) -> Tuple[str, List[Dict[str, str]]]:
        """Formats graph retrieval results into an LLM context prompt and UI badges.

        Args:
            retrieval: RetrievalResult from GraphRetriever.

        Returns:
            Tuple of:
              - formatted_context_str: Text string passed into the LLM system prompt.
              - entity_badges: List of dicts for UI display (e.g. [{'type': 'movie', 'label': 'The Matrix'}]).
        """
        if not retrieval.records:
            return (
                "NO_DATA_FOUND: The Neo4j Knowledge Graph returned 0 records for this query.",
                [],
            )

        lines: List[str] = []
        badges: List[Dict[str, str]] = []
        q_type = retrieval.query_type
        records = retrieval.records

        # Format based on query type
        if q_type == "movie_director":
            movie_title = records[0].get("movie", "Unknown")
            directors = [r.get("director", "") for r in records if r.get("director")]
            released = records[0].get("released")
            rel_str = f" (Released: {released})" if released else ""
            badge_label = f"{movie_title} ({released})" if released else movie_title

            lines.append(f"Movie: {movie_title}{rel_str}")
            lines.append(f"Director(s): {', '.join(directors)}")

            badges.append({"type": "movie", "label": badge_label})
            for d in directors:
                badges.append({"type": "person", "label": f"Director: {d}"})

        elif q_type == "movie_actors":
            movie_title = records[0].get("movie", "Unknown")
            released = records[0].get("released")
            rel_str = f" (Released: {released})" if released else ""
            badge_label = f"{movie_title} ({released})" if released else movie_title

            lines.append(f"Movie: {movie_title}{rel_str}")
            lines.append("Cast & Roles:")

            badges.append({"type": "movie", "label": badge_label})
            for r in records:
                actor = r.get("actor", "")
                roles = r.get("roles", [])
                role_str = f" as {', '.join(roles)}" if roles else ""
                lines.append(f"  - {actor}{role_str}")
                badges.append({"type": "actor", "label": actor})

        elif q_type == "actor_movies":
            actor_name = records[0].get("actor", "Unknown")
            lines.append(f"Actor: {actor_name}")
            lines.append("Filmography in Knowledge Graph:")

            badges.append({"type": "person", "label": f"Actor: {actor_name}"})
            for r in records:
                m_title = r.get("movie", "")
                rel = r.get("released", "")
                rel_suffix = f" ({rel})" if rel else ""
                roles = r.get("roles", [])
                role_str = f" (Roles: {', '.join(roles)})" if roles else ""
                lines.append(f"  - {m_title}{rel_suffix}{role_str}")
                badges.append({"type": "movie", "label": f"{m_title}{rel_suffix}"})

        elif q_type == "director_movies":
            director_name = records[0].get("director", "Unknown")
            lines.append(f"Director: {director_name}")
            lines.append("Directed Films in Knowledge Graph:")

            badges.append({"type": "person", "label": f"Director: {director_name}"})
            for r in records:
                m_title = r.get("movie", "")
                rel = r.get("released", "")
                rel_suffix = f" ({rel})" if rel else ""
                tag = f" - '{r.get('tagline')}'" if r.get("tagline") else ""
                lines.append(f"  - {m_title}{rel_suffix}{tag}")
                badges.append({"type": "movie", "label": f"{m_title}{rel_suffix}"})

        elif q_type in ["movie_recommendation", "movies_with_shared_actor", "movies_with_shared_director"]:
            lines.append("Graph-Based Recommendations & Connection Reasons:")
            for r in records:
                rec_movie = r.get("recommended_movie", "")
                rel = r.get("released", "")
                rel_suffix = f" ({rel})" if rel else ""
                shared_actors = r.get("shared_actors", [])
                same_directors = r.get("same_directors", [])

                reasons = []
                if shared_actors:
                    reasons.append(f"Shares {len(shared_actors)} actor(s): {', '.join(shared_actors)}")
                if same_directors:
                    reasons.append(f"Same director: {', '.join(same_directors)}")

                reason_text = "; ".join(reasons) if reasons else "Connected in knowledge graph"
                lines.append(f"  * Recommended: {rec_movie}{rel_suffix} - Reason: {reason_text}")

                badges.append({"type": "movie", "label": f"Rec: {rec_movie}{rel_suffix}"})

        elif q_type == "movie_release":
            r = records[0]
            title = r.get("title", "")
            rel = r.get("released", "")
            tagline = r.get("tagline", "")
            directors = r.get("directors", [])
            lines.append(f"Movie: {title}")
            lines.append(f"Release Year: {rel}")
            if tagline:
                lines.append(f"Tagline: '{tagline}'")
            if directors:
                lines.append(f"Director(s): {', '.join(directors)}")

            badges.append({"type": "movie", "label": f"{title} ({rel})"})

        else:
            # Generic structured representation
            for idx, r in enumerate(records, 1):
                clean_items = [f"{k}: {v}" for k, v in r.items() if v]
                lines.append(f"Record {idx}: {', '.join(clean_items)}")

        formatted_context = "\n".join(lines)
        return formatted_context, badges
