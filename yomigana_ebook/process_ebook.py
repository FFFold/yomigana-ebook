from warnings import filterwarnings
from typing import IO
from zipfile import ZipFile, ZIP_DEFLATED
from concurrent.futures import Future, ProcessPoolExecutor, as_completed

from bs4 import BeautifulSoup, Tag, XMLParsedAsHTMLWarning
from bs4.element import NavigableString
from yomigana_ebook.yomituki import yomituki
from yomigana_ebook.checking import contains_japanese


filterwarnings("ignore", category=XMLParsedAsHTMLWarning, module="bs4")


def process_ebook(reader: IO[bytes], writer: IO[bytes], filter_non_japanese: bool = False):
    with (
        ZipFile(reader, "r") as zip_reader,
        ZipFile(writer, "w", ZIP_DEFLATED) as zip_writer,
        ProcessPoolExecutor() as executor,
    ):
        tasks: list[Future[tuple[str, bytes]]] = []

        for file in zip_reader.namelist():
            with zip_reader.open(file) as file_reader:
                content = file_reader.read()

            if file.endswith(("xhtml", "html")):
                task = executor.submit(process_html, file, content, filter_non_japanese)
            else:
                task = executor.submit(process_resources, file, content)

            tasks.append(task)

        for task in as_completed(tasks):
            file, processed_content = task.result()
            zip_writer.writestr(file, processed_content)


def process_html(file: str, content: bytes, filter_non_japanese: bool = False):
    soup = BeautifulSoup(content, "lxml")

    for child in soup.children:
        process_tag(child, filter_non_japanese)  # type: ignore

    return file, soup.encode(formatter=None)  # type: ignore


def process_tag(tag: Tag, filter_non_japanese: bool = False):
    if tag.name == "ruby":
        return

    if isinstance(tag, NavigableString):
        text = str(tag)
        if not filter_non_japanese or contains_japanese(text):
            tag.replace_with("".join(yomituki(text)))
        return

    if hasattr(tag, "children"):
        for child in tag.children:
            process_tag(child, filter_non_japanese)  # type: ignore


def process_resources(file: str, content: bytes):
    return file, content
