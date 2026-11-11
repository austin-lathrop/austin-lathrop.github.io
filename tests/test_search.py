import json
import re
import unittest
import xml.etree.ElementTree as ET

from sitelib import load, site_dir

SITE = "https://austin-lathrop.github.io"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class SearchTest(unittest.TestCase):
    def test_google_verification_tag(self):
        home = load("index.html")
        tags = home.find_all("meta", name="google-site-verification")
        self.assertEqual([t["attrs"]["content"] for t in tags], ["iAXYt6YNzmt5yTthFGUYZEFdbFtd0oDDuRGVgaegWGA"])

    def test_home_title_says_journalist_and_place(self):
        home = load("index.html")
        self.assertEqual(home.find_all("title")[0]["text"], "Austin Lathrop | Journalist in Athens, Georgia")

    def test_story_titles_unchanged(self):
        page = load("stories/beef-prices/index.html")
        self.assertEqual(page.find_all("title")[0]["text"],
                         "Experts, ranchers say beef prices likely to remain high for years | Austin Lathrop")

    def test_person_profile_card(self):
        home = load("index.html")
        scripts = home.nodes("script", type="application/ld+json")
        self.assertEqual(len(scripts), 1)
        data = json.loads("".join(scripts[0].text_parts))
        self.assertEqual(data["@type"], "Person")
        self.assertEqual(data["name"], "Austin Lathrop")
        self.assertEqual(data["jobTitle"], "Journalist")
        self.assertEqual(data["url"], SITE + "/")
        self.assertIn("https://www.linkedin.com/in/austin-lathrop-658bb330a/", data["sameAs"])
        self.assertEqual(data["email"], "mailto:austinlathrop132@gmail.com")

    def test_sitemap_lists_only_pages_this_site_owns(self):
        tree = ET.parse(site_dir() / "sitemap.xml")
        locs = [e.text for e in tree.getroot().findall("s:url/s:loc", NS)]
        self.assertIn(SITE + "/", locs)
        # Story pages point search engines at the outlet's original, so they stay out of the sitemap.
        self.assertFalse([l for l in locs if "/stories/" in l], locs)

    def test_robots_points_to_sitemap(self):
        robots = (site_dir() / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("User-agent: *", robots)
        self.assertIn(f"Sitemap: {SITE}/sitemap.xml", robots)
        self.assertNotRegex(robots, r"(?m)^Disallow: /\s*$")


if __name__ == "__main__":
    unittest.main()
