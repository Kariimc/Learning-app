"""Gamification: rewards are earned, idempotent and never lost."""
from readingland import config


def test_first_steps_badge_on_first_activity(session):
    item = session.content.item(2, "A")
    out = session.answer(2, item, correct=True)
    ids = [g.reward_id for g in out.new_rewards]
    assert "first_steps" in ids


def test_mastering_item_grants_sticker(session):
    item = session.content.item(2, "A")
    grants = []
    for _ in range(config.MASTERY_THRESHOLD):
        out = session.answer(2, item, correct=True)
        grants.extend(out.new_rewards)
    kinds = {g.kind for g in grants}
    assert "sticker" in kinds


def test_rewards_are_idempotent(session):
    item = session.content.item(2, "A")
    session.answer(2, item, correct=True)
    before = len(session.rewards.owned(session.pid, "badge"))
    # Earning the same milestone again should not duplicate.
    session.rewards.grant_badge(session.pid, "first_steps")
    after = len(session.rewards.owned(session.pid, "badge"))
    assert before == after


def test_sticker_book_marks_owned(session):
    item = session.content.item(2, "A")
    for _ in range(config.MASTERY_THRESHOLD):
        session.answer(2, item, correct=True)
    book = session.rewards.sticker_book(session.pid)
    assert any(s["owned"] for s in book)
    assert all("emoji" in s for s in book)


def test_daily_goal_progress(session):
    item = session.content.item(2, "A")
    session.answer(2, item, correct=True)
    prog = session.daily_goal()
    assert prog["done"] >= 1
    assert prog["goal"] == config.DAILY_GOAL_ACTIVITIES
