"""Query Classifier and Entity Extraction Module for MovieGraph RAG.

Classifies natural language questions into predefined Cypher query templates
and extracts entities (movie titles, person names) using catalog lookup,
rule-based pattern matching, and fuzzy resolution.
"""

import re
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple, List
from data.movies_data import get_all_movie_titles, get_all_person_names


@dataclass
class QueryIntent:
    """Represents the parsed intent and extracted parameters of a user question."""
    query_type: str
    template_name: str
    confidence: float
    parameters: Dict[str, Any]
    detected_entity: Optional[str]
    detected_entity_type: Optional[str]  # 'movie' or 'person'
    explanation: str


class QueryClassifier:
    """Classifies user queries and extracts entities against the Neo4j Movies catalog."""

    def __init__(self):
        self.movie_titles = get_all_movie_titles()
        self.person_names = get_all_person_names()
        # High-performance hash lookups for large graph catalogs (4,800+ movies, 63,000+ persons)
        self._movie_lookup = {t.lower(): t for t in self.movie_titles}
        self._person_lookup = {p.lower(): p for p in self.person_names}
        self._movie_no_the_lookup = {t[4:].lower(): t for t in self.movie_titles if t.lower().startswith("the ")}
        self._stopwords = {
            "who", "what", "where", "when", "why", "how", "did", "do", "does", "in", "on", "at",
            "to", "for", "of", "with", "a", "an", "the", "is", "was", "are", "were", "act",
            "acted", "direct", "directed", "director", "producers", "producer", "produced",
            "writer", "writers", "wrote", "movie", "movies", "film", "films", "recommend",
            "similar", "like", "share", "shares", "shared", "actor", "actors", "cast"
        }

    def classify(self, question: str) -> QueryIntent:
        """Analyzes a natural language question and resolves its query intent and entities.

        Args:
            question: Raw user question string.

        Returns:
            QueryIntent dataclass with query_type, parameters, and confidence.
        """
        cleaned_q = question.strip()
        q_lower = cleaned_q.lower()

        # Step 1: Entity Extraction
        movie_match = self._extract_movie_title(cleaned_q)
        person_match = self._extract_person_name(cleaned_q)

        # Step 2: Intent Pattern Matching

        # Recommendations
        if any(kw in q_lower for kw in ["recommend", "suggest", "similar to", "like", "movies related to"]):
            if movie_match:
                return QueryIntent(
                    query_type="movie_recommendation",
                    template_name="Graph-based Movie Recommendation",
                    confidence=0.95,
                    parameters={"title": movie_match},
                    detected_entity=movie_match,
                    detected_entity_type="movie",
                    explanation=f"Recommendation query targeted at movie '{movie_match}'",
                )
            elif person_match:
                return QueryIntent(
                    query_type="actor_movies",
                    template_name="Find Movies Acted in by Person",
                    confidence=0.90,
                    parameters={"name": person_match},
                    detected_entity=person_match,
                    detected_entity_type="person",
                    explanation=f"Recommendation query targeted at actor '{person_match}'",
                )

        # Director queries
        if any(kw in q_lower for kw in ["who directed", "director of", "directed by", "was the director"]):
            if movie_match:
                return QueryIntent(
                    query_type="movie_director",
                    template_name="Find Movie Director",
                    confidence=0.95,
                    parameters={"title": movie_match},
                    detected_entity=movie_match,
                    detected_entity_type="movie",
                    explanation=f"Director inquiry for movie '{movie_match}'",
                )
            elif person_match:
                return QueryIntent(
                    query_type="director_movies",
                    template_name="Find Movies Directed by Person",
                    confidence=0.90,
                    parameters={"name": person_match},
                    detected_entity=person_match,
                    detected_entity_type="person",
                    explanation=f"Inquiry for movies directed by '{person_match}'",
                )
            else:
                candidate = self._extract_quotes_or_title_candidate(cleaned_q)
                candidate_title = re.sub(
                    r'^(who directed|director of|directed by|who was the director of)\s+',
                    '',
                    candidate,
                    flags=re.IGNORECASE,
                ).strip().rstrip('?.!')
                return QueryIntent(
                    query_type="movie_director",
                    template_name="Find Movie Director",
                    confidence=0.60,
                    parameters={"title": candidate_title},
                    detected_entity=candidate_title,
                    detected_entity_type="movie",
                    explanation=f"Director inquiry for candidate movie '{candidate_title}'",
                )

        # Movies directed by a person
        if "what movies did" in q_lower and "direct" in q_lower:
            target_person = person_match or self._extract_name_fallback(cleaned_q)
            return QueryIntent(
                query_type="director_movies",
                template_name="Find Movies Directed by Person",
                confidence=0.92,
                parameters={"name": target_person},
                detected_entity=target_person,
                detected_entity_type="person",
                explanation=f"Directorial catalog inquiry for '{target_person}'",
            )

        # Actor / Cast queries for a movie
        if any(kw in q_lower for kw in ["who acted in", "who was in", "cast of", "actors in", "who starred in", "starred in"]):
            if movie_match:
                return QueryIntent(
                    query_type="movie_actors",
                    template_name="Find Movie Cast / Actors",
                    confidence=0.95,
                    parameters={"title": movie_match},
                    detected_entity=movie_match,
                    detected_entity_type="movie",
                    explanation=f"Cast inquiry for movie '{movie_match}'",
                )

        # Movies starring a person
        if any(kw in q_lower for kw in ["movies did", "movies starring", "movies featuring", "acted in", "starred in"]):
            if person_match:
                return QueryIntent(
                    query_type="actor_movies",
                    template_name="Find Movies Acted in by Person",
                    confidence=0.95,
                    parameters={"name": person_match},
                    detected_entity=person_match,
                    detected_entity_type="person",
                    explanation=f"Filmography inquiry for actor '{person_match}'",
                )

        # Collaboration / Worked together
        if any(kw in q_lower for kw in ["worked together", "collaborat", "co-star", "frequent co-star"]):
            if movie_match:
                return QueryIntent(
                    query_type="movie_actors",
                    template_name="Find Movie Cast / Actors",
                    confidence=0.90,
                    parameters={"title": movie_match},
                    detected_entity=movie_match,
                    detected_entity_type="movie",
                    explanation=f"Cast collaboration inquiry for '{movie_match}'",
                )
            if person_match:
                return QueryIntent(
                    query_type="actor_collaboration",
                    template_name="Co-Star Collaboration",
                    confidence=0.90,
                    parameters={"name": person_match},
                    detected_entity=person_match,
                    detected_entity_type="person",
                    explanation=f"Collaboration network inquiry for '{person_match}'",
                )

        # Release year / Tagline
        if any(kw in q_lower for kw in ["when was", "release date", "released in", "what year", "year was", "tagline"]):
            if movie_match:
                return QueryIntent(
                    query_type="movie_release",
                    template_name="Find Movie Release & Tagline",
                    confidence=0.95,
                    parameters={"title": movie_match},
                    detected_entity=movie_match,
                    detected_entity_type="movie",
                    explanation=f"Release metadata inquiry for '{movie_match}'",
                )

        # Shared actors / Shared directors
        if "share actor" in q_lower or "shared actor" in q_lower or "actors with" in q_lower:
            if movie_match:
                return QueryIntent(
                    query_type="movies_with_shared_actor",
                    template_name="Movies Sharing Actors",
                    confidence=0.92,
                    parameters={"title": movie_match},
                    detected_entity=movie_match,
                    detected_entity_type="movie",
                    explanation=f"Shared actors discovery for '{movie_match}'",
                )

        if "share director" in q_lower or "same director as" in q_lower:
            if movie_match:
                return QueryIntent(
                    query_type="movies_with_shared_director",
                    template_name="Movies by Same Director",
                    confidence=0.92,
                    parameters={"title": movie_match},
                    detected_entity=movie_match,
                    detected_entity_type="movie",
                    explanation=f"Shared director discovery for '{movie_match}'",
                )

        # Fallback to general movie information if a movie title is detected
        if movie_match:
            return QueryIntent(
                query_type="general_movie_information",
                template_name="Full Movie Overview",
                confidence=0.80,
                parameters={"title": movie_match},
                detected_entity=movie_match,
                detected_entity_type="movie",
                explanation=f"General knowledge graph inquiry for movie '{movie_match}'",
            )

        # Fallback to actor movies if a person is detected
        if person_match:
            return QueryIntent(
                query_type="actor_movies",
                template_name="Find Movies Acted in by Person",
                confidence=0.75,
                parameters={"name": person_match},
                detected_entity=person_match,
                detected_entity_type="person",
                explanation=f"General filmography query for person '{person_match}'",
            )

        # Fallback if no specific catalog match was found
        extracted_fallback = self._extract_quotes_or_title_candidate(cleaned_q)
        return QueryIntent(
            query_type="general_movie_information",
            template_name="Full Movie Overview",
            confidence=0.40,
            parameters={"title": extracted_fallback},
            detected_entity=extracted_fallback,
            detected_entity_type="unknown",
            explanation=f"Unclassified query; attempting title match for '{extracted_fallback}'",
        )

    def _extract_movie_title(self, text: str) -> Optional[str]:
        """Extracts known movie title from text with priority for longest matches using n-gram lookup."""
        # 1. Check quoted strings first: "The Matrix"
        quoted = re.findall(r'["\']([^"\']+)["\']', text)
        for q in quoted:
            k = q.strip().lower()
            if k in self._movie_lookup:
                return self._movie_lookup[k]
            if k in self._movie_no_the_lookup:
                return self._movie_no_the_lookup[k]

        # 2. Tokenize into words and test n-grams from longest down to 1
        clean = re.sub(r'[^\w\s\-\':]', ' ', text).strip()
        words = clean.split()
        max_n = min(len(words), 8)

        # Full title match with priority for longest phrases
        for n in range(max_n, 0, -1):
            for i in range(len(words) - n + 1):
                gram = ' '.join(words[i:i+n]).lower()
                if n == 1 and gram in self._stopwords:
                    continue
                if gram in self._movie_lookup:
                    return self._movie_lookup[gram]

        # Title without leading "The "
        for n in range(max_n, 0, -1):
            for i in range(len(words) - n + 1):
                gram = ' '.join(words[i:i+n]).lower()
                if n == 1 and gram in self._stopwords:
                    continue
                if gram in self._movie_no_the_lookup:
                    return self._movie_no_the_lookup[gram]

        return None

    def _extract_person_name(self, text: str) -> Optional[str]:
        """Extracts known person name from text with priority for longest matches using n-gram lookup."""
        # 1. Check quoted strings first
        quoted = re.findall(r'["\']([^"\']+)["\']', text)
        for q in quoted:
            k = q.strip().lower()
            if k in self._person_lookup:
                return self._person_lookup[k]

        # 2. Tokenize and check n-grams
        clean = re.sub(r'[^\w\s\-\':]', ' ', text).strip()
        words = clean.split()
        max_n = min(len(words), 6)

        for n in range(max_n, 0, -1):
            for i in range(len(words) - n + 1):
                gram = ' '.join(words[i:i+n]).lower()
                if n == 1 and gram in self._stopwords:
                    continue
                if gram in self._person_lookup:
                    return self._person_lookup[gram]

        return None

    def _extract_name_fallback(self, text: str) -> str:
        """Attempts to extract a person's name using grammatical structure."""
        match = re.search(r'what movies did (.+?) direct', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return "Unknown"

    def _extract_quotes_or_title_candidate(self, text: str) -> str:
        """Extracts candidate title from quotes or common prepositions."""
        quoted = re.findall(r'["\']([^"\']+)["\']', text)
        if quoted:
            return quoted[0].strip()

        # Check for "in <title>" or "about <title>"
        match = re.search(r'\b(?:in|about|for|like|to)\s+([A-Za-z0-9\s\':]+?)(?:\?|$)', text, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            # remove common trailing punctuation
            candidate = re.sub(r'[\?\.!]$', '', candidate).strip()
            if candidate:
                return candidate

        return text.strip()
