"""Unit tests for Query Classification and Entity Extraction."""

import pytest
from rag.query_classifier import QueryClassifier


@pytest.fixture
def classifier():
    return QueryClassifier()


def test_classify_director_query(classifier):
    intent = classifier.classify("Who directed The Matrix?")
    assert intent.query_type == "movie_director"
    assert intent.parameters.get("title") == "The Matrix"


def test_classify_actor_query(classifier):
    intent = classifier.classify("Who acted in The Matrix?")
    assert intent.query_type == "movie_actors"
    assert intent.parameters.get("title") == "The Matrix"


def test_classify_filmography_query(classifier):
    intent = classifier.classify("What movies did Tom Hanks act in?")
    assert intent.query_type == "actor_movies"
    assert intent.parameters.get("name") == "Tom Hanks"


def test_classify_recommendation_query(classifier):
    intent = classifier.classify("Recommend movies similar to The Matrix")
    assert intent.query_type == "movie_recommendation"
    assert intent.parameters.get("title") == "The Matrix"


def test_classify_release_query(classifier):
    intent = classifier.classify("When was The Matrix released?")
    assert intent.query_type == "movie_release"
    assert intent.parameters.get("title") == "The Matrix"


def test_classify_shared_actor_query(classifier):
    intent = classifier.classify("Which movies share actors with The Matrix?")
    assert intent.query_type == "movies_with_shared_actor"
    assert intent.parameters.get("title") == "The Matrix"


def test_classify_case_insensitivity(classifier):
    intent = classifier.classify("who directed the matrix?")
    assert intent.query_type == "movie_director"
    assert intent.parameters.get("title") == "The Matrix"
