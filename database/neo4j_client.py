"""Neo4j Client module for MovieGraph RAG Assistant.

Manages connection pooling, read-only Cypher query execution with safe parameterized
variables, schema inspection, and graceful fallback to the canonical in-memory Movies
graph when an external Neo4j instance is offline or unreachable.
"""

import logging
import re
from typing import Dict, List, Any, Optional
from neo4j import GraphDatabase, Driver, exceptions
from config import Config
from data.movies_data import MOVIES, PERSONS, get_graph_stats

# Configure logger
logger = logging.getLogger("moviegraph.database")

# Unsafe Cypher keywords prohibited for read-only RAG operations
FORBIDDEN_KEYWORDS = [
    r"\bCREATE\b",
    r"\bDELETE\b",
    r"\bDETACH\s+DELETE\b",
    r"\bSET\b",
    r"\bMERGE\b",
    r"\bREMOVE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bLOAD\s+CSV\b",
]


class Neo4jSecurityError(Exception):
    """Raised when an unsafe Cypher mutation query is attempted."""
    pass


class Neo4jClient:
    """Manages Neo4j driver connection and provides secure, read-only graph retrieval."""

    def __init__(
        self,
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        self.uri = uri or Config.NEO4J_URI
        self.username = username or Config.NEO4J_USERNAME
        self.password = password or Config.NEO4J_PASSWORD
        self.database = database or Config.NEO4J_DATABASE
        self._driver: Optional[Driver] = None
        self._is_live: bool = False
        self._connection_message: str = "Uninitialized"

        # Attempt connection
        self._connect()

    def _connect(self) -> bool:
        """Attempts to establish connection to the Neo4j instance."""
        try:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                max_connection_lifetime=3600,
            )
            # Verify connectivity
            self._driver.verify_connectivity()
            self._is_live = True
            self._connection_message = "Connected to Live Neo4j Instance"
            logger.info(f"Connected to Neo4j at {self.uri}")
            return True
        except exceptions.AuthError:
            self._is_live = False
            self._connection_message = "Authentication Failed: Incorrect Neo4j username/password"
            logger.warning(self._connection_message)
            return False
        except exceptions.ServiceUnavailable:
            self._is_live = False
            self._connection_message = f"Neo4j Service Unavailable at {self.uri} (Running on Canonical Graph Dataset)"
            logger.info(self._connection_message)
            return False
        except Exception as e:
            self._is_live = False
            self._connection_message = f"Connection Failed: {str(e)} (Running on Canonical Graph Dataset)"
            logger.warning(self._connection_message)
            return False

    @property
    def is_live(self) -> bool:
        """Returns True if connected to an active Neo4j database instance."""
        return self._is_live

    @property
    def connection_status(self) -> str:
        """Returns a user-friendly description of the database connection."""
        return self._connection_message

    def verify_connectivity(self) -> Dict[str, Any]:
        """Runs health check and returns connection metrics."""
        stats = self.get_database_stats()
        return {
            "is_connected": self._is_live,
            "status_message": self._connection_message,
            "database": self.database if self._is_live else "Canonical In-Memory Graph",
            "uri": self.uri if self._is_live else "Local Offline Engine",
            "movies_count": stats.get("movie_count", 0),
            "persons_count": stats.get("person_count", 0),
            "total_nodes": stats.get("total_nodes", 0),
            "is_fallback": not self._is_live,
        }

    def validate_query_safety(self, query: str) -> None:
        """Ensures that the Cypher query contains only read operations.

        Raises:
            Neo4jSecurityError if destructive modification keywords are detected.
        """
        for pattern in FORBIDDEN_KEYWORDS:
            if re.search(pattern, query, re.IGNORECASE):
                raise Neo4jSecurityError(
                    f"Security violation: Mutation query prohibited. Found pattern matching '{pattern}'."
                )

    def execute_read_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Executes a read-only Cypher query with parameters.

        Args:
            query: Cypher statement.
            parameters: Dictionary of query parameters (e.g., {'title': 'The Matrix'}).

        Returns:
            List of dictionaries representing retrieved graph records.
        """
        self.validate_query_safety(query)
        parameters = parameters or {}

        if self._is_live and self._driver:
            try:
                with self._driver.session(database=self.database) as session:
                    result = session.run(query, parameters)
                    records = [record.data() for record in result]
                    return records
            except Exception as e:
                logger.error(f"Live Neo4j query error: {e}. Falling back to canonical graph.")

        # Fallback to local canonical graph resolver
        return self._resolve_fallback_query(query, parameters)

    def get_database_stats(self) -> Dict[str, Any]:
        """Returns node and relationship statistics from Neo4j or canonical fallback."""
        if self._is_live and self._driver:
            try:
                with self._driver.session(database=self.database) as session:
                    m_count = session.run("MATCH (m:Movie) RETURN count(m) AS count").single()["count"]
                    p_count = session.run("MATCH (p:Person) RETURN count(p) AS count").single()["count"]
                    r_count = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()["count"]
                    return {
                        "movie_count": m_count,
                        "person_count": p_count,
                        "total_nodes": m_count + p_count,
                        "total_relationships": r_count,
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch live stats: {e}")

        return get_graph_stats()

    def _resolve_fallback_query(
        self,
        query: str,
        parameters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Resolves queries against the in-memory canonical Movies dataset."""
        title = parameters.get("title", "")
        name = parameters.get("name", "")
        query_lower = query.lower()

        # 1. Recommendation / Shared Actors Query
        if ("recommended_movie" in query_lower or "recommendation" in query_lower or "shared" in query_lower) and "title" in parameters:
            matched_title = self._find_matching_movie(title)
            if not matched_title:
                return []
            target_movie = MOVIES[matched_title]
            target_actors = {a["name"] for a in target_movie["actors"]}

            recommendations = []
            for other_title, other_data in MOVIES.items():
                if other_title == matched_title:
                    continue
                other_actors = {a["name"] for a in other_data["actors"]}
                shared_actors = list(target_actors.intersection(other_actors))
                same_dirs = list(set(target_movie["directors"]).intersection(set(other_data["directors"])))
                same_director = bool(same_dirs)

                if shared_actors or same_director:
                    recommendations.append({
                        "source_movie": matched_title,
                        "recommended_movie": other_title,
                        "released": other_data["released"],
                        "tagline": other_data.get("tagline", ""),
                        "shared_actors": shared_actors,
                        "shared_actor_count": len(shared_actors),
                        "same_directors": same_dirs,
                        "same_director": same_director,
                        "directors": other_data["directors"],
                    })

            # Sort by total graph connection score
            return sorted(
                recommendations,
                key=lambda x: (x["shared_actor_count"] * 2 + (3 if x["same_director"] else 0)),
                reverse=True,
            )

        # 2. Movie Director Query
        if "director" in query_lower and "title" in parameters:
            matched_title = self._find_matching_movie(title)
            if matched_title and matched_title in MOVIES:
                movie = MOVIES[matched_title]
                return [
                    {
                        "movie": movie["title"],
                        "director": d,
                        "released": movie["released"],
                    }
                    for d in movie["directors"]
                ]
            return []

        # 2. Movie Actors Query
        if "acted_in" in query_lower and "title" in parameters and not ("p:person {name:" in query_lower):
            matched_title = self._find_matching_movie(title)
            if matched_title and matched_title in MOVIES:
                movie = MOVIES[matched_title]
                return [
                    {
                        "movie": movie["title"],
                        "actor": actor["name"],
                        "roles": actor["roles"],
                        "released": movie["released"],
                    }
                    for actor in movie["actors"]
                ]
            return []

        # 3. Actor Movies Query
        if ("p:person {name:" in query_lower or "actor" in query_lower) and "acted_in" in query_lower and name:
            matched_name = self._find_matching_person(name)
            results = []
            for m_title, m_data in MOVIES.items():
                for actor in m_data["actors"]:
                    if actor["name"].lower() == matched_name.lower():
                        results.append({
                            "actor": actor["name"],
                            "movie": m_data["title"],
                            "released": m_data["released"],
                            "roles": actor["roles"],
                        })
            return sorted(results, key=lambda x: x["released"], reverse=True)

        # 4. Director Movies Query
        if ("director" in query_lower or "directed" in query_lower) and name:
            matched_name = self._find_matching_person(name)
            results = []
            for m_title, m_data in MOVIES.items():
                if matched_name in m_data["directors"]:
                    results.append({
                        "director": matched_name,
                        "movie": m_data["title"],
                        "released": m_data["released"],
                        "tagline": m_data.get("tagline", ""),
                    })
            return sorted(results, key=lambda x: x["released"], reverse=True)

        # 5. Movie Release & General Info
        if "title" in parameters and ("tagline" in query_lower or "released" in query_lower):
            matched_title = self._find_matching_movie(title)
            if matched_title and matched_title in MOVIES:
                m = MOVIES[matched_title]
                return [{
                    "title": m["title"],
                    "released": m["released"],
                    "tagline": m.get("tagline", ""),
                    "directors": m["directors"],
                    "cast_count": len(m["actors"]),
                }]
            return []


        # Default fallback: check if title or name exists in parameters
        if title:
            matched_title = self._find_matching_movie(title)
            if matched_title:
                m = MOVIES[matched_title]
                return [{
                    "movie": m["title"],
                    "released": m["released"],
                    "tagline": m["tagline"],
                    "directors": m["directors"],
                    "actors": [a["name"] for a in m["actors"]],
                }]

        return []

    def _find_matching_movie(self, query_title: str) -> Optional[str]:
        """Case-insensitive fuzzy match for movie titles."""
        if not query_title:
            return None
        q = query_title.strip().lower()
        # 1. Direct case-insensitive match
        for title in MOVIES.keys():
            if title.lower() == q:
                return title
        # 2. Title with or without leading 'the '
        if q.startswith("the "):
            no_the = q[4:]
            for title in MOVIES.keys():
                if title.lower() == no_the:
                    return title
        else:
            with_the = f"the {q}"
            for title in MOVIES.keys():
                if title.lower() == with_the:
                    return title
        # 3. Distinct word boundary match for title, prioritizing closer length
        sorted_by_len = sorted(MOVIES.keys(), key=len)
        for title in sorted_by_len:
            if re.search(r'\b' + re.escape(q) + r'\b', title.lower()):
                return title
        return None

    def _find_matching_person(self, query_name: str) -> str:
        """Case-insensitive match for person names."""
        if not query_name:
            return ""
        q = query_name.strip().lower()
        for name in PERSONS.keys():
            if name.lower() == q or q in name.lower() or name.lower() in q:
                return name
        return query_name

    def close(self) -> None:
        """Closes the Neo4j driver connection cleanly."""
        if self._driver:
            self._driver.close()
            self._is_live = False
            logger.info("Neo4j driver connection closed.")
