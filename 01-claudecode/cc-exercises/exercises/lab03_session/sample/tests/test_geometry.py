import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from geometry import area, intersect, union_area

A = {"left": 0, "top": 0, "right": 10, "bottom": 10}
B = {"left": 5, "top": 5, "right": 15, "bottom": 15}
FAR = {"left": 100, "top": 100, "right": 110, "bottom": 110}


def test_area_of_a_normal_box():
    assert area(A) == 100


def test_boxes_that_miss_have_no_intersection():
    assert intersect(A, FAR) is None


def test_union_does_not_count_the_overlap_twice():
    assert union_area(A, B) == 175
