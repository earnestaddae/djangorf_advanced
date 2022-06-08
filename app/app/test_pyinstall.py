import pytest


def add(a,b):
    return a + b

def subtract(a,b):
    return a - b

def test_add():
    assert add(3, 2) == 5

def test_subtractions():
    assert subtract(8,7) == 1