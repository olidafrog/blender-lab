"""Convert a folder of Sphinx HTML pages to plain text (main content only). Stdlib only.

    python3 tools/html_to_text.py <html_dir> <out_dir>
"""
import sys
from html.parser import HTMLParser
from pathlib import Path

BLOCK = {"p", "div", "section", "li", "dt", "dd", "tr", "br", "pre", "table", "ul", "ol", "dl"}
HEAD = {"h1": "# ", "h2": "## ", "h3": "### ", "h4": "#### "}
SKIP = {"script", "style", "nav", "footer", "header", "aside"}


class Main(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0      # >0 while inside the main content element
        self.skip = 0
        self.pre = False
        self.out = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.depth:
            self.depth += 1
        elif a.get("role") == "main" or a.get("itemprop") == "articleBody" or a.get("id") == "furo-main-content":
            self.depth = 1
            return
        if not self.depth:
            return
        if tag in SKIP:
            self.skip += 1
        if a.get("class", "") and "headerlink" in a.get("class", ""):
            self.skip += 1
            self._headerlink = True
        if tag in HEAD:
            self.out.append("\n\n" + HEAD[tag])
        elif tag == "pre":
            self.pre = True
            self.out.append("\n```\n")
        elif tag == "li":
            self.out.append("\n- ")
        elif tag in BLOCK:
            self.out.append("\n")
        elif tag == "code" and not self.pre:
            self.out.append("`")

    def handle_endtag(self, tag):
        if not self.depth:
            return
        if tag in SKIP and self.skip:
            self.skip -= 1
        if tag == "a" and getattr(self, "_headerlink", False):
            self.skip -= 1
            self._headerlink = False
        if tag == "pre":
            self.pre = False
            self.out.append("\n```\n")
        elif tag == "code" and not self.pre:
            self.out.append("`")
        elif tag in BLOCK or tag in HEAD:
            self.out.append("\n")
        self.depth -= 1

    def handle_data(self, data):
        if self.depth and not self.skip:
            self.out.append(data if self.pre else " ".join(data.split()) + (" " if data.endswith((" ", "\n")) else ""))

    def text(self):
        t = "".join(self.out)
        lines = [l.rstrip() for l in t.splitlines()]
        res, blank = [], 0
        for l in lines:
            blank = blank + 1 if not l.strip() else 0
            if blank < 2:
                res.append(l)
        return "\n".join(res).strip() + "\n"


src, dst = Path(sys.argv[1]), Path(sys.argv[2])
n = 0
for f in src.rglob("*.html"):
    if any(part.startswith(("_", ".")) for part in f.relative_to(src).parts) or f.name in ("genindex.html", "search.html", "py-modindex.html"):
        continue
    p = Main()
    p.feed(f.read_text(errors="ignore"))
    t = p.text()
    if len(t) < 40:
        continue
    out = dst / f.relative_to(src).with_suffix(".txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(t)
    n += 1
print(f"converted {n} pages -> {dst}")
