"""Content packs must be present, well-formed and unique."""
from readingland import config
from readingland.core.content import ContentLibrary


def test_all_stage_packs_load():
    lib = ContentLibrary()
    for stage in config.STAGES:
        pack = lib.pack(stage["id"])
        assert pack is not None, f"missing pack for stage {stage['id']}"
        assert len(pack) > 0, f"empty pack for stage {stage['id']}"


def test_content_validates_clean():
    lib = ContentLibrary()
    problems = lib.validate()
    assert problems == [], f"content problems: {problems}"


def test_characters_loaded():
    lib = ContentLibrary()
    for cid in ["reading_rabbit", "benny_bear", "penny_penguin", "ollie_owl", "milo_monkey"]:
        char = lib.character(cid)
        assert char["name"], cid
        assert "voice_lines" in char


def test_alphabet_has_26_letters():
    lib = ContentLibrary()
    assert lib.total_items(2) == 26


def test_item_lookup():
    lib = ContentLibrary()
    apple = lib.item(2, "A")
    assert apple is not None
    assert apple.data["word"] == "Apple"
    assert apple.emoji == "🍎"
