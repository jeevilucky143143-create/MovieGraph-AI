"""Automated loader script to import the TMDB 5000 Credits dataset into Neo4j.

Usage:
    python3 data/load_data.py
"""

import os
import sys
import time

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from neo4j import GraphDatabase, exceptions
from data.movies_data import MOVIES, PERSONS, CREDITS_CSV_PATH


def batch_iterate(iterable, batch_size=1000):
    """Yield successive batches of batch_size from iterable."""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def load_movies_dataset():
    """Loads the TMDB 5000 Credits dataset into Neo4j via high-performance parameterized batch UNWIND."""
    print("=" * 60)
    print("MovieGraph RAG - TMDB 5000 Neo4j Dataset Importer")
    print("=" * 60)
    print(f"Target URI:      {Config.NEO4J_URI}")
    print(f"Target Username: {Config.NEO4J_USERNAME}")
    print(f"Target Database: {Config.NEO4J_DATABASE}")
    print(f"Dataset Source:  {CREDITS_CSV_PATH}")
    print(f"Movies in graph: {len(MOVIES)}")
    print(f"Persons in graph:{len(PERSONS)}")
    print("-" * 60)

    try:
        driver = GraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USERNAME, Config.NEO4J_PASSWORD),
        )
        with driver.session(database=Config.NEO4J_DATABASE) as session:
            print("Connecting to Neo4j...")
            driver.verify_connectivity()
            print("Connected successfully!\n")

            # 1. Create Schema Constraints / Indexes
            print("Setting up schema constraints...")
            try:
                session.run("CREATE CONSTRAINT movie_title_unique IF NOT EXISTS FOR (m:Movie) REQUIRE m.title IS UNIQUE")
                session.run("CREATE CONSTRAINT person_name_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE")
                print("  ✓ Schema uniqueness constraints active.")
            except Exception as e:
                print(f"  Note: Constraint setup ({e})")

            # 2. Batch Ingest Movies
            print("\nIngesting Movie nodes...")
            movie_records = [
                {
                    "title": m["title"],
                    "released": m.get("released", 0),
                    "tagline": m.get("tagline", ""),
                }
                for m in MOVIES.values()
            ]
            for batch in batch_iterate(movie_records, 1000):
                session.run(
                    """
                    UNWIND $batch AS m
                    MERGE (node:Movie {title: m.title})
                    SET node.released = m.released, node.tagline = m.tagline
                    """,
                    {"batch": batch},
                )
            print(f"  ✓ {len(movie_records)} Movie nodes synchronized.")

            # 3. Batch Ingest Persons
            print("\nIngesting Person nodes...")
            person_records = [
                {
                    "name": p["name"],
                    "born": p.get("born"),
                }
                for p in PERSONS.values()
            ]
            for batch in batch_iterate(person_records, 2000):
                session.run(
                    """
                    UNWIND $batch AS p
                    MERGE (node:Person {name: p.name})
                    ON CREATE SET node.born = p.born
                    """,
                    {"batch": batch},
                )
            print(f"  ✓ {len(person_records)} Person nodes synchronized.")

            # 4. Batch Ingest ACTED_IN Relationships
            print("\nIngesting ACTED_IN relationships...")
            acted_records = []
            directed_records = []
            produced_records = []
            wrote_records = []

            for m in MOVIES.values():
                title = m["title"]
                for act in m.get("actors", []):
                    acted_records.append({"movie": title, "actor": act["name"], "roles": act.get("roles", [])})
                for d in m.get("directors", []):
                    directed_records.append({"movie": title, "director": d})
                for p in m.get("producers", []):
                    produced_records.append({"movie": title, "producer": p})
                for w in m.get("writers", []):
                    wrote_records.append({"movie": title, "writer": w})

            for batch in batch_iterate(acted_records, 2000):
                session.run(
                    """
                    UNWIND $batch AS r
                    MATCH (m:Movie {title: r.movie})
                    MATCH (p:Person {name: r.actor})
                    MERGE (p)-[rel:ACTED_IN]->(m)
                    SET rel.roles = r.roles
                    """,
                    {"batch": batch},
                )
            print(f"  ✓ {len(acted_records)} ACTED_IN relationships synchronized.")

            # 5. Batch Ingest DIRECTED
            print("\nIngesting DIRECTED relationships...")
            for batch in batch_iterate(directed_records, 2000):
                session.run(
                    """
                    UNWIND $batch AS r
                    MATCH (m:Movie {title: r.movie})
                    MATCH (p:Person {name: r.director})
                    MERGE (p)-[:DIRECTED]->(m)
                    """,
                    {"batch": batch},
                )
            print(f"  ✓ {len(directed_records)} DIRECTED relationships synchronized.")

            # 6. Batch Ingest PRODUCED
            print("\nIngesting PRODUCED relationships...")
            for batch in batch_iterate(produced_records, 2000):
                session.run(
                    """
                    UNWIND $batch AS r
                    MATCH (m:Movie {title: r.movie})
                    MATCH (p:Person {name: r.producer})
                    MERGE (p)-[:PRODUCED]->(m)
                    """,
                    {"batch": batch},
                )
            print(f"  ✓ {len(produced_records)} PRODUCED relationships synchronized.")

            # 7. Batch Ingest WROTE
            print("\nIngesting WROTE relationships...")
            for batch in batch_iterate(wrote_records, 2000):
                session.run(
                    """
                    UNWIND $batch AS r
                    MATCH (m:Movie {title: r.movie})
                    MATCH (p:Person {name: r.writer})
                    MERGE (p)-[:WROTE]->(m)
                    """,
                    {"batch": batch},
                )
            print(f"  ✓ {len(wrote_records)} WROTE relationships synchronized.")

            # Verification queries
            movie_res = session.run("MATCH (m:Movie) RETURN count(m) AS count")
            movie_count = movie_res.single()["count"]

            person_res = session.run("MATCH (p:Person) RETURN count(p) AS count")
            person_count = person_res.single()["count"]

            rel_res = session.run("MATCH ()-[r]->() RETURN count(r) AS count")
            rel_count = rel_res.single()["count"]

            print("\n" + "-" * 60)
            print("Neo4j Knowledge Graph Import Summary:")
            print(f"  Movies in Neo4j:       {movie_count}")
            print(f"  Persons in Neo4j:      {person_count}")
            print(f"  Relationships:         {rel_count}")
            print("Dataset successfully imported into Neo4j!")
            print("=" * 60)

        driver.close()

    except exceptions.ServiceUnavailable:
        print("\n[Info]: Neo4j is currently offline or unreachable at " + Config.NEO4J_URI)
        print("Note: The MovieGraph application uses built-in high-performance fallback caching")
        print("and runs fully with all TMDB 5000 movies even without an external Neo4j instance active.")
    except exceptions.AuthError:
        print("\n[Error]: Neo4j Authentication Failed.")
        print("Check NEO4J_USERNAME and NEO4J_PASSWORD in your .env file.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[Unexpected Error]: {e}")
        sys.exit(1)


if __name__ == "__main__":
    load_movies_dataset()
