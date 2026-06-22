"""Progress, mastery, stars and stage unlocking."""
from readingland import config


def test_mastery_advances_and_awards_stars(session):
    item = session.content.item(2, "A")
    # First correct answer = perfect, awards STARS_PER_PERFECT.
    out = session.answer(2, item, correct=True)
    assert out.result.mastery == 1
    assert out.result.first_try is True
    assert out.result.stars_awarded == config.STARS_PER_PERFECT

    # Reach mastery threshold.
    for _ in range(config.MASTERY_THRESHOLD - 1):
        out = session.answer(2, item, correct=True)
    assert out.result.mastery == config.MASTERY_THRESHOLD
    assert out.result.mastered_now is True


def test_wrong_answer_never_punishes(session):
    item = session.content.item(2, "B")
    before = session.stars()
    out = session.answer(2, item, correct=False)
    assert out.result.mastery == 0
    assert out.result.stars_awarded == 0
    assert session.stars() == before  # never subtracts


def test_stage_unlocks_after_threshold(session):
    pid = session.pid
    assert session.progress.is_unlocked(pid, 1) is True
    assert session.progress.is_unlocked(pid, 2) is False

    pack = session.content.pack(1)
    needed = int(len(pack) * config.STAGE_UNLOCK_RATIO) + 1
    for item in pack.items[:needed]:
        for _ in range(config.MASTERY_THRESHOLD):
            session.answer(1, item, correct=True)

    assert session.progress.is_unlocked(pid, 2) is True


def test_overall_percent_monotonic(session):
    start = session.progress.overall_percent(session.pid)
    item = session.content.item(2, "C")
    for _ in range(config.MASTERY_THRESHOLD):
        session.answer(2, item, correct=True)
    assert session.progress.overall_percent(session.pid) >= start


def test_multiple_profiles_isolated(session):
    other = session.profiles.create("Sibling")
    item = session.content.item(2, "A")
    for _ in range(config.MASTERY_THRESHOLD):
        session.answer(2, item, correct=True)
    # Switch to the sibling - they should have zero progress.
    session.set_profile(other.id)
    assert session.progress.stage_summary(other.id, 2).mastered == 0
    assert session.stars() == 0
