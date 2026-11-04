"""Helpers for checking the built site (`_site/`, or $SITE_DIR) with the stdlib only."""
import os
import pathlib
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


def site_dir() -> pathlib.Path:
    return pathlib.Path(os.environ.get("SITE_DIR", ROOT / "_site"))


def fixtures_on() -> bool:
    return os.environ.get("FIXTURES") == "1"


class _Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children, self.text_parts = [], []

    def text(self):
        out = list(self.text_parts)
        for c in self.children:
            out.append(c.text())
        return " ".join(" ".join(out).split())

    def classes(self):
        return (self.attrs.get("class") or "").split()

    def element_children(self):
        return [c for c in self.children if isinstance(c, _Node)]


class _Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node("#root", [], None)
        self.cur = self.root
        self.all = []

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        self.all.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        node = _Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        self.all.append(node)

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        if self.cur is not self.root:
            self.cur.text_parts.append(data)


class Page:
    def __init__(self, raw: str):
        self.raw = raw
        b = _Builder()
        b.feed(raw)
        self._nodes = b.all
        self.root = b.root

    def nodes(self, tag=None, cls=None, within=None, **attrs):
        """Matching element nodes. `cls` matches one class; `within` restricts to descendants of a node."""
        pool = self._nodes
        if within is not None:
            pool = [n for n in pool if _is_descendant(n, within)]
        out = []
        for n in pool:
            if tag and n.tag != tag:
                continue
            if cls and cls not in n.classes():
                continue
            if any(n.attrs.get(k) != v for k, v in attrs.items()):
                continue
            out.append(n)
        return out

    def find_all(self, tag: str, **attrs) -> list:
        cls = attrs.pop("cls", None)
        return [{"attrs": n.attrs, "text": n.text()} for n in self.nodes(tag, cls=cls, **attrs)]

    def text(self) -> str:
        return self.root.text()


def _is_descendant(node, ancestor):
    p = node.parent
    while p is not None:
        if p is ancestor:
            return True
        p = p.parent
    return False


def load(relpath: str) -> Page:
    return Page((site_dir() / relpath).read_text(encoding="utf-8"))


def html_files():
    return sorted(site_dir().rglob("*.html"))
