import os
import random
import sys
import tempfile

import pytest

# Make the project root importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from readingland.core.content import ContentLibrary  # noqa: E402
from readingland.core.database import Database  # noqa: E402
from readingland.core.session import LearningSession  # noqa: E402


@pytest.fixture()
def db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    database = Database(path)
    yield database
    database.close()
    os.remove(path)


@pytest.fixture()
def content():
    return ContentLibrary()


@pytest.fixture()
def session(db, content):
    s = LearningSession(db, content, rng=random.Random(42))
    prof = s.profiles.create("Tester", birth_year=2021)
    s.set_profile(prof.id)
    return s
