"""Verify generated pages and their local links against the article sources."""

from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

from build import ROOT, expected_files


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.ids = set()
        self.headings = 0
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attributes):
        if tag == "h1":
            self.headings += 1
        for key, value in attributes:
            if key == "id" and value:
                self.ids.add(value)
            if key in {"href", "src"} and value:
                self.links.append(value)


def main():
    try:
        expected = expected_files()
    except ValueError as error:
        raise SystemExit(str(error))
    pages = {ROOT / name: Page(html) for name, html in expected.items()}
    errors = []
    for name, html in expected.items():
        path = ROOT / name
        if not path.is_file() or path.read_bytes() != html.encode("utf-8"):
            errors.append(f"{name}: 缺少檔案或內容已過期，請重新執行 build.py")
        if pages[path].headings != 1:
            errors.append(f"{name}: 頁面應有一個 h1")
        for link in pages[path].links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            destination = (path.parent / unquote(url.path)).resolve() if url.path else path
            if url.path.startswith("/") or not destination.is_relative_to(ROOT) or not destination.is_file():
                errors.append(f"{name}: 無效的站內連結 {link}")
            elif url.fragment and (
                destination not in pages or unquote(url.fragment) not in pages[destination].ids
            ):
                errors.append(f"{name}: 找不到錨點 {link}")
    for path in (ROOT / "pages").glob("*.html"):
        if path not in pages:
            errors.append(f"pages/{path.name}: 沒有對應的文章來源")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Checked {len(pages)} pages: article format, generated files and local links.")


if __name__ == "__main__":
    main()
