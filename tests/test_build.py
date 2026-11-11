import unittest

from sitelib import html_files, site_dir


class BuildTest(unittest.TestCase):
    def test_site_builds(self):
        self.assertTrue((site_dir() / "index.html").is_file(), f"no index.html in {site_dir()}")

    def test_no_unrendered_liquid(self):
        files = html_files()
        self.assertTrue(files, "no HTML files built")
        for f in files:
            raw = f.read_text(encoding="utf-8")
            self.assertNotIn("{{", raw, f"unrendered Liquid in {f}")
            self.assertNotIn("{%", raw, f"unrendered Liquid in {f}")

    def test_stylesheet_is_cache_busted(self):
        raw = (site_dir() / "index.html").read_text(encoding="utf-8")
        self.assertRegex(raw, r'href="/assets/css/site\.css\?v=\d+"')

    def test_site_address_uses_owner_name(self):
        raw = (site_dir() / "index.html").read_text(encoding="utf-8")
        self.assertIn('property="og:url" content="https://austin-lathrop.github.io/"', raw)


if __name__ == "__main__":
    unittest.main()
