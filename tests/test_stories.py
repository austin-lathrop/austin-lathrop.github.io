import re
import unittest

from sitelib import fixtures_on, load, site_dir

SLUGS = ["plowshare-tea", "beef-prices", "ffa-busy-fall", "4h-program-assistant", "athens-de-icing"]


def body_children(page):
    body = page.nodes("div", cls="body")
    assert len(body) == 1, "expected one .body"
    return body[0].element_children()


def figure_after(children, para_match):
    """The element right after the first <p> whose text starts with para_match (or is the Nth <p>)."""
    count = 0
    for i, n in enumerate(children):
        if n.tag != "p":
            continue
        count += 1
        if (isinstance(para_match, int) and count == para_match) or (
            isinstance(para_match, str) and n.text().startswith(para_match)
        ):
            return children[i + 1] if i + 1 < len(children) else None
    raise AssertionError(f"paragraph {para_match!r} not found")


def img_src(node):
    imgs = [c for c in node.element_children() if c.tag == "img"]
    return imgs[0].attrs.get("src", "") if imgs else ""


class StoryPagesTest(unittest.TestCase):
    def test_story_pages_exist(self):
        for slug in SLUGS:
            self.assertTrue((site_dir() / "stories" / slug / "index.html").is_file(), slug)

    def test_canonical_and_credit(self):
        page = load("stories/beef-prices/index.html")
        canon = page.find_all("link", rel="canonical")
        self.assertEqual(
            [c["attrs"]["href"] for c in canon],
            ["https://www.theoglethorpeecho.com/local-news/experts-ranchers-say-beef-prices-likely-remain-high-years"],
        )
        self.assertIn("Originally published by The Oglethorpe Echo on October 7, 2026.", page.text())

    def test_inline_photo_position(self):
        page = load("stories/beef-prices/index.html")
        nxt = figure_after(body_children(page), 3)
        self.assertEqual(nxt.tag, "figure")
        self.assertTrue(img_src(nxt).endswith("beef-ground-beef-prices-chart.png"))

    def test_converted_photo_lands_in_its_section(self):
        page = load("stories/athens-de-icing/index.html")
        nxt = figure_after(body_children(page), "Sand, used far more heavily")
        self.assertEqual(nxt.tag, "figure")
        self.assertTrue(img_src(nxt).endswith("de-icing-curb-gravel.jpg"))

    def test_lead_photo_not_upscaled(self):
        css = (site_dir() / "assets" / "css" / "site.css").read_text(encoding="utf-8")
        rule = re.search(r"\.lead-figure img\s*\{([^}]*)\}", css)
        self.assertIsNotNone(rule, "no .lead-figure img rule")
        self.assertIn("width: auto", rule.group(1))
        self.assertIn("max-width: 100%", rule.group(1))
        page = load("stories/4h-program-assistant/index.html")
        lead = page.nodes("figure", cls="lead-figure")
        self.assertEqual(len(lead), 1)
        img = [c for c in lead[0].element_children() if c.tag == "img"][0]
        self.assertNotIn("width", img.attrs)

    def test_photo_credits_shown(self):
        page = load("stories/athens-de-icing/index.html")
        credits = [n.text() for n in page.nodes("span", cls="credit-line")]
        self.assertEqual(credits, ["Photo: Austin Lathrop"] * 3)

    def test_plowshare_story(self):
        page = load("stories/plowshare-tea/index.html")
        self.assertEqual([h["text"] for h in page.find_all("h1")], ["Plowshare members share tea recipes, ingredients at meeting"])
        self.assertIn("The Oglethorpe Echo, November 11, 2026", page.text())
        lead = page.nodes("figure", cls="lead-figure")
        self.assertEqual(len(lead), 1)
        self.assertTrue(img_src(lead[0]).endswith("/assets/images/stories/plowshare-tea-herbs.jpg"))
        self.assertEqual([n.text() for n in page.nodes("span", cls="credit-line", within=lead[0])], ["Photo: Austin Lathrop"])
        canon = page.find_all("link", rel="canonical")
        self.assertEqual(canon[0]["attrs"]["href"],
                         "https://www.theoglethorpeecho.com/local-news/plowshare-members-share-tea-recipes-ingredients-meeting")
        self.assertEqual(len(page.nodes("p", within=page.nodes("div", cls="body")[0])), 14)
        self.assertIn("tea night in Crawford", lead[0].text())

    def test_newest_story_tops_the_list(self):
        if fixtures_on():
            self.skipTest("fixtures add a 2099 story")
        home = load("index.html")
        clips = home.nodes("ul", cls="clips")[0]
        self.assertEqual([a.attrs["href"] for a in home.nodes("a", within=clips)][0], "/stories/plowshare-tea/")

    def test_every_story_photo_on_home(self):
        home = load("index.html")
        writing = home.nodes("section", id="writing")[0]
        imgs = [i.attrs.get("src", "") for i in home.nodes("img", within=writing)]
        for slug, photo in [("plowshare-tea", "plowshare-tea-herbs.jpg"), ("beef-prices", "beef-cam-ranches-cattle.jpg"),
                            ("ffa-busy-fall", "ffa-greenhouse.jpg"), ("4h-program-assistant", "4h-first-meeting.jpg"),
                            ("athens-de-icing", "de-icing-trail-creek.jpg")]:
            self.assertTrue(any(src.endswith("/" + photo) for src in imgs), f"{slug}: photo missing from home page")

    def test_row_thumbnail_inside_its_link(self):
        home = load("index.html")
        clips = home.nodes("ul", cls="clips")[0]
        for a in home.nodes("a", within=clips):
            thumbs = home.nodes("img", cls="clip-img", within=a)
            if a.attrs["href"] == "/stories/plowshare-tea/":
                self.assertEqual(len(thumbs), 1)
                self.assertTrue(thumbs[0].attrs.get("alt"), "thumbnail needs alt text")

    def test_home_writing_order(self):
        home = load("index.html")
        leads = home.nodes("div", cls="leads")
        clips = home.nodes("ul", cls="clips")
        self.assertEqual(len(leads), 1)
        self.assertEqual(len(clips), 1)
        lead_hrefs = [a.attrs["href"] for a in home.nodes("a", within=leads[0])]
        clip_hrefs = [a.attrs["href"] for a in home.nodes("a", within=clips[0])]
        self.assertEqual(lead_hrefs[:2], ["/stories/beef-prices/", "/stories/athens-de-icing/"])
        expected_rows = ["/stories/ffa-busy-fall/", "/stories/4h-program-assistant/"]
        self.assertEqual([h for h in clip_hrefs if h in expected_rows], expected_rows)

    def test_next_story_wraps(self):
        page = load("stories/athens-de-icing/index.html")
        nxt = page.find_all("a", cls="next")
        self.assertEqual(len(nxt), 1)
        if not fixtures_on():
            # The oldest story wraps around to the newest one.
            self.assertEqual(nxt[0]["attrs"]["href"], "/stories/plowshare-tea/")

    def test_escaping(self):
        page = load("stories/athens-de-icing/index.html")
        og = page.find_all("meta", property="og:title")
        self.assertEqual([m["attrs"]["content"] for m in og], ["Athens' de-icing chemicals raise waterway concerns"])
        titles = page.find_all("title")
        self.assertTrue(titles[0]["text"].startswith("Athens' de-icing chemicals raise waterway concerns"))


@unittest.skipUnless(fixtures_on(), "needs tests/build_with_fixtures.sh")
class StoryEdgeCasesTest(unittest.TestCase):
    def setUp(self):
        self.page = load("stories/edge-case/index.html")

    def test_photo_beyond_last_paragraph_appended(self):
        children = body_children(self.page)
        paras = [i for i, n in enumerate(children) if n.tag == "p"]
        figs = [i for i, n in enumerate(children) if n.tag == "figure"]
        self.assertEqual(len(figs), 1, "photo dropped or duplicated")
        self.assertGreater(figs[0], paras[-1])

    def test_lead_without_image_renders_as_row(self):
        home = load("index.html")
        leads = home.nodes("div", cls="leads")[0]
        clips = home.nodes("ul", cls="clips")[0]
        self.assertNotIn("/stories/edge-case/", [a.attrs["href"] for a in home.nodes("a", within=leads)])
        self.assertIn("/stories/edge-case/", [a.attrs["href"] for a in home.nodes("a", within=clips)])

    def test_every_photo_with_an_image_appears_once(self):
        page = load("stories/hostile-cms/index.html")
        body = page.nodes("div", cls="body")[0]
        captions = sorted(f.text() for f in page.nodes("figcaption", within=body))
        self.assertEqual(captions, sorted(["blank number", "no number key", "zero", "text two", "one and a half"]))

    def test_text_paragraph_number_is_honoured(self):
        page = load("stories/hostile-cms/index.html")
        nxt = figure_after(body_children(page), 2)
        self.assertEqual(nxt.tag, "figure")
        self.assertIn("text two", nxt.text())

    def test_link_without_scheme_gets_https(self):
        page = load("stories/hostile-cms/index.html")
        self.assertEqual(page.find_all("link", rel="canonical")[0]["attrs"]["href"], "https://www.example.com/no-scheme")
        hrefs = [a["attrs"].get("href") for a in page.find_all("a") if "original" in a["text"] or "Read it at" in a["text"]]
        self.assertTrue(hrefs)
        self.assertTrue(all(h == "https://www.example.com/no-scheme" for h in hrefs), hrefs)

    def test_uploaded_filename_with_spaces_loads(self):
        from urllib.parse import unquote
        page = load("stories/hostile-cms/index.html")
        lead = page.nodes("figure", cls="lead-figure")[0]
        src = img_src(lead)
        self.assertNotIn(" ", src)
        self.assertTrue((site_dir() / unquote(src).lstrip("/")).is_file(), src)

    def test_story_without_text_points_to_original(self):
        page = load("stories/no-text-yet/index.html")
        body = page.nodes("div", cls="body")[0]
        links = [a for a in page.nodes("a", within=body) if a.attrs.get("href") == "https://example.com/no-text-yet"]
        self.assertEqual([a.text() for a in links], ["Read the full story at Test Outlet"])

    def test_headline_with_quotes_and_ampersand(self):
        og = self.page.find_all("meta", property="og:title")
        self.assertEqual(og[0]["attrs"]["content"], "Q&A: \"Quotes\" & 'apostrophes'")
        h1 = self.page.find_all("h1")
        self.assertEqual(h1[0]["text"], "Q&A: \"Quotes\" & 'apostrophes'")


if __name__ == "__main__":
    unittest.main()
