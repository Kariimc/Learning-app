"""Data-driven curriculum loader.

All teaching material lives as JSON in ``readingland/content``. New letters,
words, sentences, stories or even whole modules are added by dropping in / editing
a JSON file - **no core code changes required**. This module validates and exposes
that content through small, typed accessors.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .. import config


@dataclass
class ContentItem:
    """A single teachable thing (a letter, word, sentence, story...)."""

    id: str
    stage: int
    label: str                       # the text shown / read
    narration: str                   # what the narrator says
    data: Dict = field(default_factory=dict)  # stage-specific extras

    @property
    def emoji(self) -> str:
        return self.data.get("emoji", "")

    @property
    def color(self) -> Optional[str]:
        return self.data.get("color")


@dataclass
class ContentPack:
    """All items for one stage, plus pack metadata."""

    id: str
    stage: int
    title: str
    items: List[ContentItem]

    def __len__(self) -> int:
        return len(self.items)

    def by_id(self, item_id: str) -> Optional[ContentItem]:
        for it in self.items:
            if it.id == item_id:
                return it
        return None


class ContentLibrary:
    """Loads every content pack and the character roster once at startup."""

    def __init__(self, content_dir: str = config.CONTENT_DIR):
        self.content_dir = content_dir
        self.packs: Dict[int, ContentPack] = {}
        self.characters: Dict[str, dict] = {}
        self.load()

    # ------------------------------------------------------------------ #
    def _read_json(self, filename: str) -> dict:
        path = os.path.join(self.content_dir, filename)
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def load(self) -> None:
        # Characters
        try:
            self.characters = {c["id"]: c for c in self._read_json("characters.json")["characters"]}
        except FileNotFoundError:
            self.characters = {}

        # Stage packs - declared in config so adding a stage is one edit.
        for stage in config.STAGES:
            try:
                raw = self._read_json(stage["content"])
            except FileNotFoundError:
                continue
            self.packs[stage["id"]] = self._parse_pack(stage, raw)

    def _parse_pack(self, stage: dict, raw: dict) -> ContentPack:
        items: List[ContentItem] = []
        for entry in raw.get("items", []):
            items.append(
                ContentItem(
                    id=str(entry["id"]),
                    stage=stage["id"],
                    label=entry.get("label", entry.get("id", "")),
                    narration=entry.get("narration", entry.get("label", "")),
                    data=entry,
                )
            )
        return ContentPack(
            id=raw.get("id", stage["key"]),
            stage=stage["id"],
            title=raw.get("title", stage["title"]),
            items=items,
        )

    # ------------------------------------------------------------------ #
    # Accessors
    # ------------------------------------------------------------------ #
    def pack(self, stage: int) -> Optional[ContentPack]:
        return self.packs.get(stage)

    def items(self, stage: int) -> List[ContentItem]:
        pack = self.packs.get(stage)
        return pack.items if pack else []

    def item(self, stage: int, item_id: str) -> Optional[ContentItem]:
        pack = self.packs.get(stage)
        return pack.by_id(item_id) if pack else None

    def character(self, char_id: str) -> dict:
        return self.characters.get(char_id, {"id": char_id, "name": char_id.title()})

    def total_items(self, stage: int) -> int:
        return len(self.items(stage))

    def validate(self) -> List[str]:
        """Return a list of human-readable problems (empty == healthy)."""
        problems: List[str] = []
        for stage in config.STAGES:
            pack = self.packs.get(stage["id"])
            if pack is None:
                problems.append(f"Stage {stage['id']} ({stage['key']}): content pack missing")
                continue
            if not pack.items:
                problems.append(f"Stage {stage['id']} ({stage['key']}): no items")
            seen = set()
            for it in pack.items:
                if it.id in seen:
                    problems.append(f"Stage {stage['id']}: duplicate item id '{it.id}'")
                seen.add(it.id)
        return problems
