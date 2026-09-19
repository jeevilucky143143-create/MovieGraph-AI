"""Graph Analytics Module for MovieGraph AI.

Provides high-performance graph algorithms including:
- Six Degrees of Separation (Breadth-First Search shortest pathfinder)
- Movie Head-to-Head Comparative Graph Analytics
- Network Graph Topology Extraction for interactive Canvas visualization
"""

import math
import time
from collections import deque
from typing import Dict, List, Any, Optional, Tuple, Set
from data.movies_data import MOVIES, PERSONS


class GraphAnalytics:
    """Provides high-performance graph traversal and comparative analytics."""

    _instance = None
    _person_to_movies: Dict[str, List[Tuple[str, str]]] = {}
    _movie_to_persons: Dict[str, List[Tuple[str, str]]] = {}
    _initialized = False

    def __init__(self):
        if not GraphAnalytics._initialized:
            self._build_index()
            GraphAnalytics._initialized = True

    @classmethod
    def _build_index(cls) -> None:
        """Constructs bidirectional adjacency graph for fast O(V+E) traversals."""
        p_to_m: Dict[str, List[Tuple[str, str]]] = {}
        m_to_p: Dict[str, List[Tuple[str, str]]] = {}

        for m_title, m_data in MOVIES.items():
            movie_people: List[Tuple[str, str]] = []

            # Directors
            for d in m_data.get("directors", []):
                movie_people.append((d, "DIRECTED"))
                if d not in p_to_m:
                    p_to_m[d] = []
                p_to_m[d].append((m_title, "DIRECTED"))

            # Actors
            for a in m_data.get("actors", []):
                act_name = a["name"]
                movie_people.append((act_name, "ACTED_IN"))
                if act_name not in p_to_m:
                    p_to_m[act_name] = []
                p_to_m[act_name].append((m_title, "ACTED_IN"))

            # Producers
            for p in m_data.get("producers", []):
                movie_people.append((p, "PRODUCED"))
                if p not in p_to_m:
                    p_to_m[p] = []
                p_to_m[p].append((m_title, "PRODUCED"))

            # Writers
            for w in m_data.get("writers", []):
                movie_people.append((w, "WROTE"))
                if w not in p_to_m:
                    p_to_m[w] = []
                p_to_m[w].append((m_title, "WROTE"))

            m_to_p[m_title] = movie_people

        cls._person_to_movies = p_to_m
        cls._movie_to_persons = m_to_p

    def find_shortest_path(
        self,
        person_a: str,
        person_b: str,
        max_depth: int = 6,
    ) -> Tuple[Optional[List[Dict[str, str]]], float]:
        """Finds the shortest relational path between two people using Breadth-First Search (BFS).

        Returns:
            Tuple of (path_steps, execution_time_ms)
        """
        t0 = time.time()
        p1 = person_a.strip()
        p2 = person_b.strip()

        if p1 not in self._person_to_movies or p2 not in self._person_to_movies:
            return None, (time.time() - t0) * 1000

        if p1 == p2:
            return [{"type": "person", "name": p1}], (time.time() - t0) * 1000

        # Queue contains (current_person, path_history, depth)
        queue = deque([(p1, [{"type": "person", "name": p1}], 0)])
        visited_persons: Set[str] = {p1}
        visited_movies: Set[str] = set()

        while queue:
            current_person, path, depth = queue.popleft()
            if depth >= max_depth:
                break

            for movie_title, p_rel in self._person_to_movies.get(current_person, []):
                if movie_title in visited_movies:
                    continue
                visited_movies.add(movie_title)

                for next_person, m_rel in self._movie_to_persons.get(movie_title, []):
                    if next_person == p2:
                        # Found target!
                        complete_path = path + [
                            {"type": "movie", "name": movie_title, "rel_from": p_rel, "rel_to": m_rel},
                            {"type": "person", "name": p2},
                        ]
                        return complete_path, (time.time() - t0) * 1000

                    if next_person not in visited_persons:
                        visited_persons.add(next_person)
                        new_path = path + [
                            {"type": "movie", "name": movie_title, "rel_from": p_rel, "rel_to": m_rel},
                            {"type": "person", "name": next_person},
                        ]
                        queue.append((next_person, new_path, depth + 1))

        return None, (time.time() - t0) * 1000

    def compare_movies(self, title_a: str, title_b: str) -> Optional[Dict[str, Any]]:
        """Compares two movies head-to-head across their graph neighborhoods."""
        if title_a not in MOVIES or title_b not in MOVIES:
            return None

        m1 = MOVIES[title_a]
        m2 = MOVIES[title_b]

        m1_actors = {a["name"] for a in m1.get("actors", [])}
        m2_actors = {a["name"] for a in m2.get("actors", [])}
        shared_actors = sorted(list(m1_actors.intersection(m2_actors)))

        m1_dirs = set(m1.get("directors", []))
        m2_dirs = set(m2.get("directors", []))
        shared_directors = sorted(list(m1_dirs.intersection(m2_dirs)))

        m1_prods = set(m1.get("producers", []))
        m2_prods = set(m2.get("producers", []))
        shared_producers = sorted(list(m1_prods.intersection(m2_prods)))

        m1_writers = set(m1.get("writers", []))
        m2_writers = set(m2.get("writers", []))
        shared_writers = sorted(list(m1_writers.intersection(m2_writers)))

        affinity_score = (
            len(shared_actors) * 2
            + len(shared_directors) * 4
            + len(shared_producers) * 2
            + len(shared_writers) * 2
        )

        total_unique_people = len(m1_actors.union(m2_actors).union(m1_dirs).union(m2_dirs))
        overlap_count = len(shared_actors) + len(shared_directors) + len(shared_producers) + len(shared_writers)
        similarity_pct = round((overlap_count / max(total_unique_people, 1)) * 100, 1)

        return {
            "movie_a": m1,
            "movie_b": m2,
            "shared_actors": shared_actors,
            "shared_directors": shared_directors,
            "shared_producers": shared_producers,
            "shared_writers": shared_writers,
            "affinity_score": affinity_score,
            "similarity_pct": similarity_pct,
            "has_connection": affinity_score > 0,
        }

    def get_top_prolific_entities(self, limit: int = 8) -> Dict[str, List[Tuple[str, int]]]:
        """Identifies top connected actors and directors in the knowledge graph."""
        actor_counts: Dict[str, int] = {}
        director_counts: Dict[str, int] = {}

        for m_data in MOVIES.values():
            for a in m_data.get("actors", []):
                name = a["name"]
                actor_counts[name] = actor_counts.get(name, 0) + 1
            for d in m_data.get("directors", []):
                director_counts[d] = director_counts.get(d, 0) + 1

        top_actors = sorted(actor_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        top_directors = sorted(director_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

        return {
            "top_actors": top_actors,
            "top_directors": top_directors,
        }

    def generate_vis_network_data(self, movie_title: str, max_actors: int = 15) -> Dict[str, Any]:
        """Generates node and edge definitions formatted for Vis.js force-directed physics graph."""
        if movie_title not in MOVIES:
            return {"nodes": [], "edges": []}

        m = MOVIES[movie_title]
        nodes = []
        edges = []

        directors = m.get("directors", [])
        actors = m.get("actors", [])[:max_actors]
        total_connected = len(directors) + len(actors)

        # Central Movie Node (Anchored at center coordinate 0,0)
        rel_str = f" ({m['released']})" if m.get("released") else ""
        nodes.append({
            "id": "movie_center",
            "label": f"{movie_title}{rel_str}",
            "title": f"Movie: {movie_title}\nTagline: {m.get('tagline', 'N/A')}",
            "x": 0,
            "y": 0,
            "fixed": {"x": True, "y": True},
            "color": {
                "background": "#FFFFFF",
                "border": "#53457A",
                "highlight": {"background": "#EFEAF7", "border": "#53457A"},
            },
            "font": {"color": "#2D3142", "size": 16, "face": "Manrope, sans-serif", "bold": True},
            "shape": "box",
            "margin": 12,
            "borderWidth": 3,
            "shadow": {"enabled": True, "color": "rgba(83, 69, 122, 0.25)", "size": 10},
        })

        radius = 240
        node_idx = 0

        # Director Nodes
        for d in directors:
            d_id = f"dir_{d}"
            angle = (2 * math.pi * node_idx / max(total_connected, 1)) - (math.pi / 2)
            nx = int(radius * math.cos(angle))
            ny = int(radius * math.sin(angle))
            node_idx += 1

            nodes.append({
                "id": d_id,
                "label": f"🎬 {d}",
                "title": f"Director: {d}",
                "x": nx,
                "y": ny,
                "color": {
                    "background": "#F5F2FA",
                    "border": "#B4A7D6",
                    "highlight": {"background": "#EFEAF7", "border": "#53457A"},
                },
                "font": {"color": "#53457A", "size": 13, "face": "Manrope, sans-serif", "bold": True},
                "shape": "box",
                "margin": 8,
                "borderWidth": 2,
            })
            edges.append({
                "from": d_id,
                "to": "movie_center",
                "label": "DIRECTED",
                "color": {"color": "#B4A7D6", "highlight": "#53457A"},
                "arrows": "to",
                "font": {"size": 10, "color": "#53457A", "align": "middle"},
                "width": 2,
            })

        # Actor Nodes
        for idx, a in enumerate(actors):
            act_name = a["name"]
            roles = a.get("roles", [])
            role_hint = f"\nas {roles[0]}" if roles else ""
            a_id = f"act_{act_name}_{idx}"

            angle = (2 * math.pi * node_idx / max(total_connected, 1)) - (math.pi / 2)
            nx = int(radius * math.cos(angle))
            ny = int(radius * math.sin(angle))
            node_idx += 1

            nodes.append({
                "id": a_id,
                "label": f"👤 {act_name}",
                "title": f"Actor: {act_name}{role_hint}",
                "x": nx,
                "y": ny,
                "color": {
                    "background": "#F2F6F0",
                    "border": "#A3B899",
                    "highlight": {"background": "#EBF2E8", "border": "#38522E"},
                },
                "font": {"color": "#38522E", "size": 12, "face": "Manrope, sans-serif"},
                "shape": "box",
                "margin": 6,
                "borderWidth": 1.5,
            })
            edges.append({
                "from": a_id,
                "to": "movie_center",
                "label": "ACTED_IN",
                "color": {"color": "#A3B899", "highlight": "#38522E"},
                "arrows": "to",
                "font": {"size": 9, "color": "#38522E", "align": "middle"},
                "width": 1.5,
            })

        return {"nodes": nodes, "edges": edges}
