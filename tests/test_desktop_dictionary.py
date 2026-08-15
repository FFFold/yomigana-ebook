import os
from pathlib import Path

from yomigana_desktop.dictionary import (
    DICDIR_ENV_VAR,
    configure_unidic_dir,
    find_unidic_dir,
    is_valid_unidic_dir,
)


def test_find_unidic_dir_returns_installed_dictionary():
    dicdir = find_unidic_dir()
    assert dicdir is not None
    assert is_valid_unidic_dir(dicdir)


def test_configure_unidic_dir_sets_environment_variable():
    old_value = os.environ.get(DICDIR_ENV_VAR)
    try:
        dicdir = configure_unidic_dir()
        assert dicdir is not None
        assert os.environ[DICDIR_ENV_VAR] == str(dicdir)
        assert Path(os.environ[DICDIR_ENV_VAR]).is_dir()
    finally:
        if old_value is None:
            os.environ.pop(DICDIR_ENV_VAR, None)
        else:
            os.environ[DICDIR_ENV_VAR] = old_value


def test_is_valid_unidic_dir_rejects_missing_path():
    assert not is_valid_unidic_dir(Path("Z:/definitely/not/a/unidic/dicdir"))
