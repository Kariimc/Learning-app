"""ReadingLand - a highly visual early-literacy app for children.

The package is split into four layers:

* ``readingland.core``    - pure-Python engine (no Kivy import). Persistence,
                            curriculum content, progress, adaptive difficulty and
                            rewards live here so they can be unit-tested headless.
* ``readingland.ui``      - reusable Kivy widgets, particle effects and the
                            programmatic placeholder-asset generator.
* ``readingland.screens`` - one Kivy ``Screen`` per stage / view.
* ``readingland.content`` - data-driven JSON curriculum packs.

The golden rule that keeps the project maintainable and AI-friendly:
**core never imports Kivy, and content is data not code.**
"""

__version__ = "1.0.0"
__app_name__ = "ReadingLand"
