import os
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from map_generator import generate_map

def test_map_creation():
    output = generate_map(14.5995, 120.9842, "test_map.html")
    assert output == "test_map.html"
    assert os.path.exists("test_map.html")

    # cleanup
    os.remove("test_map.html")


def test_map_error():
    # invalid input → should not crash
    output = generate_map("not-lat", "not-long")
    assert output is None
