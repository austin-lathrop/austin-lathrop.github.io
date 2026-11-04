import re
import unittest

from sitelib import ROOT, html_files, load, Page

EMAIL = "austinlathrop132@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/austin-lathrop-658bb330a/"


def profile_value(key):
    """Top-level scalar from _data/profile.yml ('' when blank)."""
    text = (ROOT / "_data" / "profile.yml").read_text(encoding="utf-8")
    m = re.search(rf"^{key}:[ \t]*(.*)$", text, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""


class ProfileHomeTest(unittest.TestCase):
    def setUp(self):
        self.home = load("index.html")

    def test_header_has_name_and_email(self):
        marks = self.home.find_all("a", cls="wordmark")
        self.assertEqual([m["text"] for m in marks], ["Austin Lathrop"])
        solid = [a["attrs"].get("href") for a in self.home.find_all("a", cls="btn-solid")]
        self.assertIn(f"mailto:{EMAIL}", solid)

    def test_opening_line(self):
        h1 = self.home.find_all("h1", cls="statement")
        self.assertEqual(
            [h["text"] for h in h1],
            ["I report on agriculture, rural communities and the environment in Northeast Georgia."],
        )

    def test_outlets(self):
        pub = self.home.nodes("div", cls="published")
        self.assertEqual(len(pub), 1)
        items = [n.text() for n in self.home.nodes("li", within=pub[0])]
        self.assertEqual(items, ["The Oglethorpe Echo", "Grady Newsource"])

    def test_linkedin(self):
        links = [a for a in self.home.find_all("a") if a["attrs"].get("href") == LINKEDIN]
        self.assertTrue(links, "no LinkedIn link")
        for a in links:
            self.assertIn("noopener", a["attrs"].get("rel", ""))

    def test_about_and_skills(self):
        about = self.home.nodes("section", id="about")
        self.assertEqual(len(about), 1)
        text = about[0].text()
        self.assertIn("House Oversight and Accountability Committee", text)
        labels = [n.text() for n in self.home.nodes("dt", within=about[0])]
        self.assertEqual(labels, ["Beats", "Sources and data", "Visual", "Education", "Coverage area"])

    def test_cv_button_matches_profile(self):
        cv = profile_value("cv")
        has_button = "Download CV" in self.home.text()
        if cv:
            self.assertTrue(has_button, "profile has a CV but no Download CV button")
            hrefs = [a["attrs"].get("href") for a in self.home.find_all("a") if "CV" in a["text"]]
            self.assertTrue(all(h == cv for h in hrefs), hrefs)
        else:
            self.assertFalse(has_button, "Download CV shown with no CV file")

    def test_portrait_matches_profile(self):
        intro = self.home.nodes("section", cls="intro")
        self.assertEqual(len(intro), 1)
        imgs = self.home.nodes("img", within=intro[0])
        self.assertEqual(len(imgs), 1 if profile_value("portrait") else 0)
        self.assertEqual(self.home.nodes(cls="ph"), [])

    def test_availability_matches_profile(self):
        status = self.home.find_all("p", cls="status")
        if profile_value("availability"):
            self.assertEqual(len(status), 1)
        else:
            self.assertEqual(status, [])

    def test_social_preview_tags(self):
        metas = {m["attrs"].get("property"): m["attrs"].get("content") for m in self.home.find_all("meta")}
        self.assertEqual(metas.get("og:title"), "Austin Lathrop")
        self.assertTrue(metas.get("og:description"))

    def test_no_empty_hrefs(self):
        for f in html_files():
            page = Page(f.read_text(encoding="utf-8"))
            for a in page.find_all("a"):
                self.assertNotIn(a["attrs"].get("href"), ("", "#", None), f"empty link '{a['text']}' in {f}")


if __name__ == "__main__":
    unittest.main()
