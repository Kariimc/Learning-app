"""Adaptive difficulty and scaffolding behaviour."""
from readingland import config


def test_difficulty_rises_after_streak(session):
    pid = session.pid
    start = session.adaptive.state(pid, 2).difficulty
    for _ in range(config.ADAPTIVE_STREAK_UP):
        session.adaptive.register_result(pid, 2, correct=True)
    assert session.adaptive.state(pid, 2).difficulty > start


def test_difficulty_drops_after_miss(session):
    pid = session.pid
    # Raise it first.
    for _ in range(config.ADAPTIVE_STREAK_UP * 2):
        session.adaptive.register_result(pid, 2, correct=True)
    high = session.adaptive.state(pid, 2).difficulty
    session.adaptive.register_result(pid, 2, correct=False)
    assert session.adaptive.state(pid, 2).difficulty < high


def test_num_choices_scales_with_difficulty(session):
    pid = session.pid
    assert session.adaptive.num_choices(pid, 2) == 2  # starts easy
    for _ in range(config.ADAPTIVE_STREAK_UP * 4):
        session.adaptive.register_result(pid, 2, correct=True)
    assert session.adaptive.num_choices(pid, 2) >= 3


def test_next_item_prefers_unmastered(session):
    pid = session.pid
    # Master one letter fully.
    mastered = session.content.item(2, "A")
    for _ in range(config.MASTERY_THRESHOLD):
        session.answer(2, mastered, correct=True)
    # Over many draws the mastered item should appear less than its fair share.
    counts = {}
    for _ in range(400):
        it = session.adaptive.next_item(pid, 2)
        counts[it.id] = counts.get(it.id, 0) + 1
    total = sum(counts.values())
    fair_share = total / session.content.total_items(2)
    assert counts.get("A", 0) < fair_share


def test_build_choices_includes_target(session):
    target = session.content.item(2, "M")
    choices = session.build_choices(2, target)
    assert target in choices
    assert len(choices) >= 2
