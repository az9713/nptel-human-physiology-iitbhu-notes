"""Bounded static integrity check; does not attest browser/science acceptance."""
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "chapter-15-muscle-neuromuscular-transmission.html"


class Page(HTMLParser):
    """Collect link and ID evidence without evaluating scripts."""

    def __init__(self, source):
        super().__init__()
        self.ids = []
        self.links = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        names = [item[0] for item in attrs]
        assert len(names) == len(set(names)), "duplicate attribute"
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for name in ("href", "src"):
            if name in attrs:
                self.links.append(attrs[name])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    raw = CHAPTER.read_bytes()
    begin = b"<!-- BEGIN CHAPTER BODY -->"
    end = b"<!-- END CHAPTER BODY -->"
    assert raw.count(begin) == raw.count(end) == 1
    body = raw.split(begin)[1].split(end)[0]
    source = raw.decode("utf-8")
    page = Page(source)
    assert len(page.ids) == len(set(page.ids)), "duplicate IDs"
    for link in page.links:
        parsed = urlsplit(unescape(link))
        if parsed.scheme or parsed.netloc:
            continue
        if parsed.path:
            assert (ROOT / unquote(parsed.path)).is_file(), link
            assert not parsed.path.startswith(("sources/", "work/")), link
        elif parsed.fragment:
            assert unquote(parsed.fragment) in page.ids, link
    assert source.count('class="problem"') == 6
    assert source.count('class="solution"') == 6
    assert source.count('class="ch15-model"') == 3
    # The shared reader uses \( \) and \[ \], not dollar delimiters.
    math_source = body.decode("utf-8")
    assert math_source.count(r"\(") == math_source.count(r"\)")
    assert math_source.count(r"\[") == math_source.count(r"\]")
    segments = re.findall(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", math_source, re.S)
    for inline, display in segments:
        math = inline or display
        count = 0
        for char in math:
            if char == "{":
                count += 1
            elif char == "}":
                count -= 1
                assert count >= 0
        assert count == 0, math
        assert "<" not in math and ">" not in math
    meta = json.loads(CHAPTER.with_suffix(".meta.json").read_text("utf-8"))
    assert meta["body_sha256"] == digest(body)
    expected = {f"L{lec}-T{i:02d}"
                for lec, count in ((33, 19), (34, 23), (35, 16))
                for i in range(1, count + 1)}
    assert {t["id"] for t in meta["coverage_topics"]} == expected
    for topic in meta["coverage_topics"]:
        assert topic["anchor"] in page.ids
        assert topic["disposition"]
    for artifact in meta["reviewed_artifacts"]:
        assert digest((ROOT / artifact["path"]).read_bytes()) == artifact["sha256"]
    print(f"PASS: {len(page.ids)} unique IDs; {len(segments)} math segments; "
          "58 topic dispositions; six worked solutions; current raw digests")
    print("Browser, accessibility interaction, visual verdict and two "
          "independent scientific reviews remain separate.")


if __name__ == "__main__":
    main()
