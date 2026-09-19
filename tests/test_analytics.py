"""Unit tests for Graph Analytics (Six Degrees BFS, Movie Compare, Network Gen)."""

import pytest
from recommendation.graph_analytics import GraphAnalytics


@pytest.fixture
def analytics():
    return GraphAnalytics()


def test_bfs_path_finding(analytics):
    """Test Six Degrees of Separation BFS pathfinder finds connection between known actors."""
    path, dur_ms = analytics.find_shortest_path("Keanu Reeves", "Leonardo DiCaprio")
    assert path is not None
    assert len(path) >= 3
    assert path[0]["name"] == "Keanu Reeves"
    assert path[-1]["name"] == "Leonardo DiCaprio"
    assert dur_ms < 500  # Should run fast


def test_bfs_same_person(analytics):
    """Test BFS when start and end person are identical."""
    path, _ = analytics.find_shortest_path("Keanu Reeves", "Keanu Reeves")
    assert path is not None
    assert len(path) == 1
    assert path[0]["name"] == "Keanu Reeves"


def test_bfs_unknown_person(analytics):
    """Test BFS returns None for non-existent person."""
    path, _ = analytics.find_shortest_path("Nonexistent Person 12345", "Keanu Reeves")
    assert path is None


def test_movie_comparison(analytics):
    """Test head-to-head comparison between two movies."""
    comp = analytics.compare_movies("The Matrix", "The Matrix Reloaded")
    assert comp is not None
    assert comp["affinity_score"] > 0
    assert len(comp["shared_actors"]) > 0
    assert "Keanu Reeves" in comp["shared_actors"]
    assert len(comp["shared_directors"]) > 0


def test_vis_network_generation(analytics):
    """Test Vis.js network data generation."""
    data = analytics.generate_vis_network_data("The Matrix")
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0
    # Center node should be the movie
    movie_nodes = [n for n in data["nodes"] if n["id"] == "movie_center"]
    assert len(movie_nodes) == 1
