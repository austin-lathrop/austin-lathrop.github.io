import unittest

from sitelib import fixtures_on, load, site_dir


def nav_labels(page):
    nav = page.nodes("nav", cls="jump")
    return [a.text() for a in page.nodes("a", within=nav[0])]


@unittest.skipIf(fixtures_on(), "launch state only")
class LaunchStateTest(unittest.TestCase):
    def test_sections_hidden_at_launch(self):
        home = load("index.html")
        self.assertEqual(home.nodes(id="photo"), [])
        self.assertEqual(home.nodes(id="video"), [])
        self.assertEqual(nav_labels(home), ["Writing", "About"])
        self.assertFalse((site_dir() / "photo").exists())


@unittest.skipUnless(fixtures_on(), "needs tests/build_with_fixtures.sh")
class PopulatedSectionsTest(unittest.TestCase):
    def setUp(self):
        self.home = load("index.html")

    def test_nav_shows_new_sections(self):
        self.assertEqual(nav_labels(self.home), ["Writing", "Photo", "Video", "About"])

    def test_essay_grid_and_page(self):
        photo = self.home.nodes("section", id="photo")
        self.assertEqual(len(photo), 1)
        self.assertIn("/photo/flood-season/", [a.attrs["href"] for a in self.home.nodes("a", within=photo[0])])
        page = load("photo/flood-season/index.html")
        frames = page.nodes("div", cls="frames")[0]
        self.assertEqual(len(page.nodes("figure", within=frames)), 5)
        pairs = page.nodes("div", cls="pair", within=frames)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(len(page.nodes("figure", within=pairs[0])), 2)
        self.assertEqual(len(page.nodes("figure", cls="inset", within=frames)), 1)
        self.assertIn("Test fixture reporting note.", page.text())

    def test_video_embeds(self):
        video = self.home.nodes("section", id="video")[0]
        srcs = [f.attrs.get("src") for f in self.home.nodes("iframe", within=video)]
        self.assertIn("https://www.youtube-nocookie.com/embed/abc123XYZ_9", srcs)
        self.assertIn("https://player.vimeo.com/video/76979871", srcs)
        self.assertIn("https://www.youtube-nocookie.com/embed/shortID42", srcs)
        self.assertEqual(len(srcs), 3, "a non-YouTube/Vimeo link must not become an iframe")
        links = [a for a in self.home.nodes("a", within=video) if a.attrs.get("href") == "https://example.com/videos/before-the-storm"]
        self.assertEqual([a.text() for a in links], ["Watch Before the Storm"])

    def test_blank_video_fields_leave_no_empty_elements(self):
        video = self.home.nodes("section", id="video")[0]
        for tag in ("dd", "p", "dt", "h4"):
            empty = [n for n in self.home.nodes(tag, within=video) if not n.text()]
            self.assertEqual(empty, [], f"empty <{tag}> in Video section")
        self.assertNotIn(", 2026", [n.text()[:6] for n in self.home.nodes("p", within=video)])

    def test_blank_essay_cover_and_location(self):
        photo = self.home.nodes("section", id="photo")[0]
        texts = [p.text() for p in self.home.nodes("p", within=photo)]
        self.assertFalse(any(t.startswith(",") for t in texts), texts)

    def test_lead_video_first(self):
        video = self.home.nodes("section", id="video")[0]
        lead = self.home.nodes("div", cls="video-lead", within=video)
        self.assertEqual(len(lead), 1)
        self.assertIn("Rising Rent, Empty Rooms", lead[0].text())


if __name__ == "__main__":
    unittest.main()
