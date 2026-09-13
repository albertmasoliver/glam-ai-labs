"""Small helpers for axis-aligned rectangles."""


def area(rect):
    return max(0, rect["right"] - rect["left"]) * max(0, rect["bottom"] - rect["top"])


def intersect(a, b):
    box = {
        "left": max(a["left"], b["left"]),
        "right": min(a["right"], b["right"]),
        "top": max(a["top"], b["top"]),
        "bottom": min(a["bottom"], b["bottom"]),
    }
    return box if area(box) else None


def union_area(a, b):
    overlap = intersect(a, b)
    return area(a) + area(b) - (area(overlap) if overlap else 0)
