from unicodedata import name as get_unicode_name


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


def contains_japanese_script(text: str) -> bool:
    # Uses Unicode range checks instead of is_hira/is_kata/is_kanji for performance.
    # Those functions call unicodedata.name() per character; this fast-path avoids that
    # overhead by using direct range comparisons, accepting a slightly different
    # definition of "Japanese script" (e.g. CJK extension blocks are not covered).
    for char in text:
        if "\u3040" <= char <= "\u309f":
            return True
        if "\u30a0" <= char <= "\u30ff":
            return True
        if "\u4e00" <= char <= "\u9fff":
            return True
        if char == "\u3005":
            return True
    return False
