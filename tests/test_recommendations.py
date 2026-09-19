"""Unit tests for Explainable Recommendation Engine."""

import pytest
from recommendation.recommender import MovieRecommender


@pytest.fixture
def recommender():
    return MovieRecommender()


def test_recommendations_for_the_matrix(recommender):
    recs = recommender.recommend("The Matrix", mode="Graph-based Discovery", limit=5)
    assert len(recs) > 0
    rec_titles = [r.title for r in recs]
    # Matrix Reloaded, Matrix Revolutions, or Devil's Advocate should be in recommendations
    assert any(t in rec_titles for t in ["The Matrix Reloaded", "The Matrix Revolutions", "The Devil's Advocate"])

    for r in recs:
        assert r.score > 0
        assert len(r.reasons) > 0
        # Check that reasons are factual
        assert any("Shares" in reason or "Directed" in reason for reason in r.reasons)


def test_recommendations_same_director(recommender):
    recs = recommender.recommend("The Matrix", mode="Same Director", limit=5)
    for r in recs:
        assert "Lana Wachowski" in r.directors or "Lilly Wachowski" in r.directors
