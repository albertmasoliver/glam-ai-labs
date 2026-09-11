"""Streak rules -- added in the change under review.

Tracks how many lines in a row you have advanced through without jumping back.
"""

import time

STREAK_KEY = "streak"
LAST_SEEN_KEY = "last_seen_at"
RESET_AFTER_SECONDS = 60 * 60 * 12


def advance(state, now=None):
    """Return new state after moving forward one line."""
    now = time.time() if now is None else now
    last = state.get(LAST_SEEN_KEY)
    streak = state.get(STREAK_KEY, 0)
    if last is not None and now - last > RESET_AFTER_SECONDS:
        streak = 0
    return {**state, STREAK_KEY: streak + 1, LAST_SEEN_KEY: now}


def reset(state):
    """Jumping back to an earlier line breaks the streak."""
    return {**state, STREAK_KEY: 0}


def describe(streak):
    if streak == 0:
        return "no streak"
    if streak == 1:
        return "1 line"
    return f"{streak} lines"
