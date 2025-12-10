from unicodedata import name as get_unicode_name
import subprocess
import sys


def check_unidic_dictionary() -> bool:
    """检查unidic词典是否已安装"""
    try:
        import unidic
        from pathlib import Path
        
        dic_dir = Path(unidic.DICDIR)
        return dic_dir.exists() and len(list(dic_dir.glob("*"))) > 0
    except Exception:
        return False


def download_unidic_dictionary() -> None:
    """下载unidic词典"""
    try:
        subprocess.check_call([sys.executable, "-m", "unidic", "download"])
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"词典下载失败: {e}")


def is_unknown(surface: str, reading: str) -> bool:
    return reading in (None, "*") or "、" in surface


def is_kana_only(text: str) -> bool:
    return all((is_hira(char) or is_kata(char)) for char in text)


def is_kanji_only(text: str) -> bool:
    return all(is_kanji(char) for char in text)


def is_latin_only(text: str) -> bool:
    return all(is_latin(char) for char in text)


def is_hira(char: str) -> bool:
    try:
        return "HIRAGANA" in get_unicode_name(char)
    except ValueError:
        return False


def is_kata(char: str) -> bool:
    try:
        return "KATAKANA" in get_unicode_name(char)
    except ValueError:
        return False


def is_kanji(char: str) -> bool:
    unicode_name = get_unicode_name(char)

    if "CJK UNIFIED IDEOGRAPH" in unicode_name:
        return True

    if "IDEOGRAPHIC ITERATION MARK" in unicode_name:
        return True

    return False


def is_latin(char: str) -> bool:
    return "LATIN" in get_unicode_name(char)


def contains_japanese(text: str) -> bool:
    return any((is_hira(char) or is_kata(char)) for char in text)
