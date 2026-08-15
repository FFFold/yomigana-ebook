import os
from pathlib import Path

from yomigana_desktop.dictionary import (
    DICDIR_ENV_VAR,
    LEGACY_DICDIR_ENV_VAR,
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


def test_find_unidic_dir_honors_legacy_env_var():
    dicdir = find_unidic_dir()
    assert dicdir is not None

    old_new = os.environ.get(DICDIR_ENV_VAR)
    old_legacy = os.environ.get(LEGACY_DICDIR_ENV_VAR)
    try:
        os.environ.pop(DICDIR_ENV_VAR, None)
        os.environ[LEGACY_DICDIR_ENV_VAR] = str(dicdir)
        assert find_unidic_dir() == dicdir
    finally:
        if old_new is None:
            os.environ.pop(DICDIR_ENV_VAR, None)
        else:
            os.environ[DICDIR_ENV_VAR] = old_new
        if old_legacy is None:
            os.environ.pop(LEGACY_DICDIR_ENV_VAR, None)
        else:
            os.environ[LEGACY_DICDIR_ENV_VAR] = old_legacy
