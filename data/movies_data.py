"""Canonical and TMDB 5000 Movies Dataset in structured format.

Loads and caches the full TMDB 5000 credits dataset ('data/tmdb_5000_credits.csv')
with canonical metadata overlays, providing complete graph representations for
Movie and Person nodes with ACTED_IN, DIRECTED, PRODUCED, and WROTE relationships.
Used for offline fallback, deterministic grounding validation, and fast entity lookups.
"""

import os
import sys
import json
import pickle
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger("moviegraph.data")

# Path constants
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CREDITS_CSV_PATH = os.path.join(DATA_DIR, "tmdb_5000_credits.csv")
CACHE_FILE_PATH = os.path.join(DATA_DIR, ".tmdb_credits_cache.pkl")

# Canonical overlay metadata for historical/benchmark Neo4j movies
CANONICAL_MOVIES_META: Dict[str, Dict[str, Any]] = {
    "The Matrix": {
        "released": 1999,
        "tagline": "Welcome to the Real World",
        "directors": ["Lana Wachowski", "Lilly Wachowski"],
        "producers": ["Joel Silver"],
        "writers": ["Lana Wachowski", "Lilly Wachowski"],
    },
    "The Matrix Reloaded": {
        "released": 2003,
        "tagline": "Free your mind",
        "directors": ["Lana Wachowski", "Lilly Wachowski"],
        "producers": ["Joel Silver"],
        "writers": ["Lana Wachowski", "Lilly Wachowski"],
    },
    "The Matrix Revolutions": {
        "released": 2003,
        "tagline": "Everything that has a beginning has an end",
        "directors": ["Lana Wachowski", "Lilly Wachowski"],
        "producers": ["Joel Silver"],
        "writers": ["Lana Wachowski", "Lilly Wachowski"],
    },
    "The Devil's Advocate": {
        "released": 1997,
        "tagline": "Evil has its winning ways",
        "directors": ["Taylor Hackford"],
        "producers": [],
        "writers": [],
    },
    "A Few Good Men": {
        "released": 1992,
        "tagline": "In the heart of the nation's capital, in a courthouse of the U.S. government, one man will stop at nothing to keep his honor, and one will stop at nothing to find the truth.",
        "directors": ["Rob Reiner"],
        "producers": [],
        "writers": ["Aaron Sorkin"],
    },
    "Top Gun": {
        "released": 1986,
        "tagline": "I feel the need, the need for speed.",
        "directors": ["Tony Scott"],
        "producers": [],
        "writers": [],
    },
    "Jerry Maguire": {
        "released": 2000,
        "tagline": "The rest of his life begins now.",
        "directors": ["Cameron Crowe"],
        "producers": ["Cameron Crowe"],
        "writers": ["Cameron Crowe"],
    },
    "Stand By Me": {
        "released": 1986,
        "tagline": "For some, it's the last real adventure of a lifetime, for others, a chance to rediscover what friendship means.",
        "directors": ["Rob Reiner"],
        "producers": [],
        "writers": [],
    },
    "As Good as It Gets": {
        "released": 1997,
        "tagline": "A comedy from the heart that goes for the throat.",
        "directors": ["James L. Brooks"],
        "producers": [],
        "writers": [],
    },
    "What Dreams May Come": {
        "released": 1998,
        "tagline": "After life there is more. The end is just the beginning.",
        "directors": ["Vincent Ward"],
        "producers": [],
        "writers": [],
    },
    "You've Got Mail": {
        "released": 1998,
        "tagline": "At odds in life... in love on-line.",
        "directors": ["Nora Ephron"],
        "producers": [],
        "writers": [],
    },
    "Sleepless in Seattle": {
        "released": 1993,
        "tagline": "What if someone you never met, someone you never saw, someone you never knew was the only someone for you?",
        "directors": ["Nora Ephron"],
        "producers": [],
        "writers": [],
    },
    "Joe Versus the Volcano": {
        "released": 1990,
        "tagline": "A story of love, lava and burning desire.",
        "directors": ["John Patrick Stanley"],
        "producers": [],
        "writers": [],
    },
    "When Harry Met Sally": {
        "released": 1998,
        "tagline": "Can two friends sleep together and still remain friends?",
        "directors": ["Rob Reiner"],
        "producers": ["Rob Reiner", "Nora Ephron"],
        "writers": ["Nora Ephron"],
    },
    "That Thing You Do": {
        "released": 1996,
        "tagline": "In every life there comes a time when that thing you dream becomes that thing you do",
        "directors": ["Tom Hanks"],
        "producers": [],
        "writers": [],
    },
    "The Replacements": {
        "released": 2000,
        "tagline": "Pain heals, Chicks dig scars... Glory lasts forever",
        "directors": ["Howard Deutch"],
        "producers": [],
        "writers": [],
    },
    "Rescue Dawn": {
        "released": 2006,
        "tagline": "Based on the incredible true story of one man's fight for freedom",
        "directors": ["Werner Herzog"],
        "producers": [],
        "writers": [],
    },
    "The Birdcage": {
        "released": 1996,
        "tagline": "Come as you are",
        "directors": ["Mike Nichols"],
        "producers": [],
        "writers": [],
    },
    "Unforgiven": {
        "released": 1992,
        "tagline": "It's a hell of a thing, killing a man",
        "directors": ["Clint Eastwood"],
        "producers": [],
        "writers": [],
    },
    "Johnny Mnemonic": {
        "released": 1995,
        "tagline": "The hottest data on earth. In the coolest head in town",
        "directors": ["Robert Longo"],
        "producers": [],
        "writers": [],
    },
    "Cloud Atlas": {
        "released": 2012,
        "tagline": "Everything is Connected",
        "directors": ["Tom Tykwer", "Lana Wachowski", "Lilly Wachowski"],
        "producers": ["Stefan Arndt"],
        "writers": [],
    },
    "The Da Vinci Code": {
        "released": 2006,
        "tagline": "Seek and you will find",
        "directors": ["Ron Howard"],
        "producers": [],
        "writers": [],
    },
    "V for Vendetta": {
        "released": 2006,
        "tagline": "Freedom! Forever!",
        "directors": ["James McTeigue"],
        "producers": ["Joel Silver"],
        "writers": ["Lilly Wachowski", "Lana Wachowski"],
    },
    "Speed Racer": {
        "released": 2008,
        "tagline": "Speed has no limits",
        "directors": ["Lilly Wachowski", "Lana Wachowski"],
        "producers": ["Joel Silver"],
        "writers": ["Lilly Wachowski", "Lana Wachowski"],
    },
    "Ninja Assassin": {
        "released": 2009,
        "tagline": "Prepare to enter a secret world",
        "directors": ["James McTeigue"],
        "producers": ["Lilly Wachowski", "Lana Wachowski", "Joel Silver"],
        "writers": [],
    },
    "The Green Mile": {
        "released": 1999,
        "tagline": "Walk a mile you'll never forget.",
        "directors": ["Frank Darabont"],
        "producers": [],
        "writers": [],
    },
    "Apollo 13": {
        "released": 1995,
        "tagline": "Houston, we have a problem.",
        "directors": ["Ron Howard"],
        "producers": [],
        "writers": [],
    },
    "Cast Away": {
        "released": 2000,
        "tagline": "At the edge of the world, his journey begins.",
        "directors": ["Robert Zemeckis"],
        "producers": [],
        "writers": [],
    },
}

CANONICAL_PERSONS_META: Dict[str, int] = {
    "Keanu Reeves": 1964, "Carrie-Anne Moss": 1967, "Laurence Fishburne": 1961, "Hugo Weaving": 1960,
    "Lilly Wachowski": 1967, "Lana Wachowski": 1965, "Joel Silver": 1952, "Charlize Theron": 1975,
    "Al Pacino": 1940, "Taylor Hackford": 1944, "Tom Cruise": 1962, "Jack Nicholson": 1937,
    "Demi Moore": 1962, "Kevin Bacon": 1958, "Kiefer Sutherland": 1966, "Noah Wyle": 1971,
    "Cuba Gooding Jr.": 1968, "Kevin Pollak": 1957, "J.T. Walsh": 1943, "James Marshall": 1967,
    "Christopher Guest": 1948, "Rob Reiner": 1947, "Aaron Sorkin": 1961, "Kelly McGillis": 1957,
    "Val Kilmer": 1959, "Anthony Edwards": 1962, "Tom Skerritt": 1933, "Meg Ryan": 1961,
    "Tony Scott": 1944, "Renee Zellweger": 1969, "Kelly Preston": 1962, "Jerry O'Connell": 1974,
    "Jay Mohr": 1970, "Bonnie Hunt": 1961, "Regina King": 1971, "Jonathan Lipnicki": 1996,
    "Cameron Crowe": 1957, "Wil Wheaton": 1972, "River Phoenix": 1970, "Corey Feldman": 1971,
    "John Cusack": 1966, "Marshall Bell": 1942, "Helen Hunt": 1963, "Greg Kinnear": 1963,
    "James L. Brooks": 1940, "Robin Williams": 1951, "Annabella Sciorra": 1960, "Max von Sydow": 1929,
    "Werner Herzog": 1942, "Vincent Ward": 1956, "Ethan Hawke": 1970, "Rick Yune": 1971,
    "James Cromwell": 1940, "Scott Hicks": 1953, "Tom Hanks": 1956, "Parker Posey": 1968,
    "Dave Chappelle": 1973, "Steve Zahn": 1967, "Nora Ephron": 1941, "Rita Wilson": 1956,
    "Bill Pullman": 1953, "Victor Garber": 1949, "Rosie O'Donnell": 1962, "John Patrick Stanley": 1950,
    "Nathan Lane": 1956, "Billy Crystal": 1948, "Carrie Fisher": 1956, "Bruno Kirby": 1949,
    "Liv Tyler": 1977, "Brooke Langton": 1970, "Gene Hackman": 1930, "Orlando Jones": 1968,
    "Howard Deutch": 1950, "Christian Bale": 1974, "Zach Grenier": 1954, "Mike Nichols": 1931,
    "Richard Harris": 1930, "Clint Eastwood": 1930, "Takeshi Kitano": 1947, "Dina Meyer": 1968,
    "Ice-T": 1958, "Robert Longo": 1953, "Halle Berry": 1966, "Jim Broadbent": 1949,
    "Tom Tykwer": 1965, "David Mitchell": 1969, "Stefan Arndt": 1961, "Ian McKellen": 1939,
    "Audrey Tautou": 1976, "Paul Bettany": 1971, "Ron Howard": 1954, "Natalie Portman": 1981,
    "Stephen Rea": 1946, "John Hurt": 1940, "Ben Miles": 1972, "James McTeigue": 1967,
    "Emile Hirsch": 1985, "John Goodman": 1952, "Susan Sarandon": 1946, "Matthew Fox": 1966,
    "Christina Ricci": 1980, "Rain": 1982, "Naomie Harris": 1976, "Michael Clarke Duncan": 1957,
    "David Morse": 1953, "Michael Jeter": 1952, "Graham Greene": 1952, "Sam Rockwell": 1968,
    "Barry Pepper": 1970, "Patricia Clarkson": 1959, "Harry Dean Stanton": 1926,
    "Frank Darabont": 1959, "Ed Harris": 1950, "Bill Paxton": 1955, "Gary Sinise": 1955,
    "Robert Zemeckis": 1952
}


def _build_dataset_from_credits_csv(csv_path: str) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Parses tmdb_5000_credits.csv and constructs MOVIES and PERSONS graph models."""
    import pandas as pd

    df = pd.read_csv(csv_path)

    movies: Dict[str, Dict[str, Any]] = {}
    persons: Dict[str, Dict[str, Any]] = {}

    for _, row in df.iterrows():
        title = str(row["title"]).strip()
        cast_raw = row["cast"]
        crew_raw = row["crew"]

        # Parse cast
        actors = []
        if pd.notna(cast_raw):
            try:
                cast_list = json.loads(cast_raw)
                for c in cast_list:
                    act_name = c.get("name")
                    char = c.get("character", "")
                    if act_name:
                        actors.append({"name": act_name, "roles": [char] if char else []})
                        if act_name not in persons:
                            persons[act_name] = {"name": act_name}
            except Exception:
                pass

        # Parse crew
        directors = []
        producers = []
        writers = []
        if pd.notna(crew_raw):
            try:
                crew_list = json.loads(crew_raw)
                for cr in crew_list:
                    job = cr.get("job")
                    pname = cr.get("name")
                    if not pname:
                        continue
                    if job == "Director" and pname not in directors:
                        directors.append(pname)
                        if pname not in persons:
                            persons[pname] = {"name": pname}
                    elif job in ["Producer", "Executive Producer"] and pname not in producers:
                        producers.append(pname)
                        if pname not in persons:
                            persons[pname] = {"name": pname}
                    elif job in ["Writer", "Screenplay"] and pname not in writers:
                        writers.append(pname)
                        if pname not in persons:
                            persons[pname] = {"name": pname}
            except Exception:
                pass

        if title in movies:
            # Handle rare duplicate titles in TMDB dataset
            movies[title]["actors"].extend(actors)
            for d in directors:
                if d not in movies[title]["directors"]:
                    movies[title]["directors"].append(d)
            for p in producers:
                if p not in movies[title]["producers"]:
                    movies[title]["producers"].append(p)
            for w in writers:
                if w not in movies[title]["writers"]:
                    movies[title]["writers"].append(w)
        else:
            movies[title] = {
                "title": title,
                "released": 0,
                "tagline": "",
                "directors": directors,
                "producers": producers,
                "writers": writers,
                "actors": actors,
            }

    # Overlay canonical metadata for benchmark films
    for c_title, c_meta in CANONICAL_MOVIES_META.items():
        if c_title in movies:
            movies[c_title]["released"] = c_meta["released"]
            movies[c_title]["tagline"] = c_meta["tagline"]
            for d in c_meta.get("directors", []):
                if d not in movies[c_title]["directors"]:
                    movies[c_title]["directors"].append(d)
            for p in c_meta.get("producers", []):
                if p not in movies[c_title]["producers"]:
                    movies[c_title]["producers"].append(p)
            for w in c_meta.get("writers", []):
                if w not in movies[c_title]["writers"]:
                    movies[c_title]["writers"].append(w)
        else:
            # Movie not present in TMDB CSV directly (e.g., Stand By Me casing variant)
            movies[c_title] = {
                "title": c_title,
                "released": c_meta["released"],
                "tagline": c_meta["tagline"],
                "directors": c_meta.get("directors", []),
                "producers": c_meta.get("producers", []),
                "writers": c_meta.get("writers", []),
                "actors": [],
            }

    # Overlay birth years for canonical persons
    for p_name, born_year in CANONICAL_PERSONS_META.items():
        if p_name in persons:
            persons[p_name]["born"] = born_year
        else:
            persons[p_name] = {"name": p_name, "born": born_year}

    return movies, persons


def load_movies_dataset() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Loads MOVIES and PERSONS with automatic caching for high-speed startup."""
    if os.path.exists(CREDITS_CSV_PATH):
        # Check cache validity
        if os.path.exists(CACHE_FILE_PATH):
            try:
                csv_mtime = os.path.getmtime(CREDITS_CSV_PATH)
                cache_mtime = os.path.getmtime(CACHE_FILE_PATH)
                if cache_mtime >= csv_mtime:
                    with open(CACHE_FILE_PATH, "rb") as f:
                        movies, persons = pickle.load(f)
                        return movies, persons
            except Exception as e:
                logger.warning(f"Failed to read TMDB cache: {e}. Rebuilding...")

        # Rebuild from CSV
        try:
            movies, persons = _build_dataset_from_credits_csv(CREDITS_CSV_PATH)
            try:
                with open(CACHE_FILE_PATH, "wb") as f:
                    pickle.dump((movies, persons), f, protocol=pickle.HIGHEST_PROTOCOL)
            except Exception as e:
                logger.warning(f"Failed to write TMDB cache: {e}")
            return movies, persons
        except Exception as e:
            logger.error(f"Error reading {CREDITS_CSV_PATH}: {e}")

    # Fallback to canonical metadata if CSV is not available
    fallback_movies: Dict[str, Dict[str, Any]] = {}
    for title, meta in CANONICAL_MOVIES_META.items():
        fallback_movies[title] = {
            "title": title,
            "released": meta["released"],
            "tagline": meta["tagline"],
            "directors": meta.get("directors", []),
            "producers": meta.get("producers", []),
            "writers": meta.get("writers", []),
            "actors": [],
        }
    fallback_persons = {name: {"name": name, "born": born} for name, born in CANONICAL_PERSONS_META.items()}
    return fallback_movies, fallback_persons


# Initialize dataset
MOVIES, PERSONS = load_movies_dataset()


def get_all_movie_titles() -> List[str]:
    """Return all movie titles in the knowledge graph."""
    return sorted(list(MOVIES.keys()))


def get_all_person_names() -> List[str]:
    """Return all person names in the knowledge graph."""
    return sorted(list(PERSONS.keys()))


def get_graph_stats() -> Dict[str, int]:
    """Return counts of movies, people, and relationships."""
    total_acted = sum(len(m.get("actors", [])) for m in MOVIES.values())
    total_directed = sum(len(m.get("directors", [])) for m in MOVIES.values())
    total_produced = sum(len(m.get("producers", [])) for m in MOVIES.values())
    total_wrote = sum(len(m.get("writers", [])) for m in MOVIES.values())
    total_relationships = total_acted + total_directed + total_produced + total_wrote
    return {
        "movie_count": len(MOVIES),
        "person_count": len(PERSONS),
        "total_nodes": len(MOVIES) + len(PERSONS),
        "total_relationships": total_relationships,
    }
