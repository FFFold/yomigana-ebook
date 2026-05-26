from warnings import filterwarnings
from typing import IO
from zipfile import ZipFile, ZIP_DEFLATED
from concurrent.futures import ProcessPoolExecutor, as_completed

from bs4 import BeautifulSoup, Tag, XMLParsedAsHTMLWarning
from bs4.element import NavigableString
from yomigana_ebook.yomituki import yomituki
from yomigana_ebook.checking import contains_japanese


filterwarnings("ignore", category=XMLParsedAsHTMLWarning, module="bs4")

SKIP_TAGS = {"ruby", "rt", "rp", "script", "style"}


def process_ebook(reader: IO[bytes], writer: IO[bytes], filter_non_japanese: bool = False):
    with ZipFile(reader, "r") as zip_reader, ZipFile(writer, "w", ZIP_DEFLATED) as zip_writer:
        html_files: list[tuple[str, bytes]] = []

        for file in zip_reader.namelist():
            content = zip_reader.read(file)

            if file.endswith(("xhtml", "html")):
                html_files.append((file, content))
            else:
                zip_writer.writestr(file, content)

        if not html_files:
            return

        if len(html_files) == 1:
            file, content = html_files[0]
            processed_file, processed_content = process_html(file, content, filter_non_japanese)
            zip_writer.writestr(processed_file, processed_content)
            return

        with ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(process_html, file, content, filter_non_japanese)
                for file, content in html_files
            ]

            for future in as_completed(futures):
                file, processed_content = future.result()
                zip_writer.writestr(file, processed_content)


def process_html(file: str, content: bytes, filter_non_japanese: bool = False):
    soup = BeautifulSoup(content, "lxml")

    for child in soup.children:
        process_tag(child, filter_non_japanese)  # type: ignore

    return file, soup.encode(formatter=None)  # type: ignore


def process_tag(tag: Tag, filter_non_japanese: bool = False):
    if tag.name in SKIP_TAGS:
        return

    if isinstance(tag, NavigableString):
        text = str(tag)
        if not text.strip():
            return
        if not filter_non_japanese or contains_japanese(text):
            tag.replace_with("".join(yomituki(text)))
        return

    if hasattr(tag, "children"):
        for child in tag.children:
            process_tag(child, filter_non_japanese)  # type: ignore

