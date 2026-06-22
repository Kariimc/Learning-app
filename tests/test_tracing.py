"""Letter-tracing stroke geometry: every letter is well-formed and in-bounds."""
import string

from readingland.core import tracing


def test_all_26_letters_have_strokes():
    for letter in string.ascii_uppercase:
        strokes = tracing.get_strokes(letter)
        assert strokes, f"no strokes for {letter}"
        assert len(strokes) >= 1


def test_points_are_normalized_in_bounds():
    for letter in string.ascii_uppercase:
        for stroke in tracing.get_strokes(letter):
            assert len(stroke) >= 2, f"{letter} has a degenerate stroke"
            for (x, y) in stroke:
                assert 0.0 <= x <= 1.0, f"{letter} x out of range: {x}"
                assert 0.0 <= y <= 1.0, f"{letter} y out of range: {y}"


def test_lookup_is_case_insensitive():
    assert tracing.get_strokes("a") == tracing.get_strokes("A")
    assert tracing.stroke_count("A") == 3   # two diagonals + crossbar


def test_unknown_letter_returns_none():
    assert tracing.get_strokes("3") is None
    assert tracing.get_strokes("") is None
