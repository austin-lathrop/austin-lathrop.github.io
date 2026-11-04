import json
import subprocess
import unittest

from sitelib import ROOT, fixtures_on, site_dir

PROFILE_KEYS = {"name", "opening_line", "availability", "email", "linkedin", "portrait", "portrait_alt", "cv",
                "contact_heading", "outlets", "about", "skills"}
STORY_KEYS = {"headline", "dek", "outlet", "date", "original_url", "lead", "image", "image_alt", "image_caption",
              "image_credit", "photos", "body"}
STORY_PHOTO_KEYS = {"image", "alt", "caption", "credit", "after_paragraph"}
ESSAY_KEYS = {"title", "dek", "location", "dates", "outlet", "published_url", "cover", "frames", "reporting_note"}
FRAME_KEYS = {"image", "alt", "caption", "credit", "layout"}
VIDEO_KEYS = {"title", "outlet", "year", "runtime", "role", "url", "lead"}


def load_config():
    out = subprocess.run(
        ["ruby", "-ryaml", "-rjson", "-e", "puts JSON.dump(YAML.load_file(ARGV[0]))", str(ROOT / ".pages.yml")],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def entry(cfg, name):
    found = [c for c in cfg["content"] if c["name"] == name]
    assert len(found) == 1, f"no content entry {name!r}"
    return found[0]


def names(fields):
    return {f["name"] for f in fields}


def subfields(fields, name):
    return [f for f in fields if f["name"] == name][0]["fields"]


class PagesCmsConfigTest(unittest.TestCase):
    def setUp(self):
        self.cfg = load_config()

    def test_all_template_fields_editable(self):
        self.assertEqual(names(entry(self.cfg, "profile")["fields"]), PROFILE_KEYS)
        stories = entry(self.cfg, "stories")["fields"]
        self.assertEqual(names(stories), STORY_KEYS)
        self.assertEqual(names(subfields(stories, "photos")), STORY_PHOTO_KEYS)
        essays = entry(self.cfg, "essays")["fields"]
        self.assertEqual(names(essays), ESSAY_KEYS)
        self.assertEqual(names(subfields(essays, "frames")), FRAME_KEYS)
        videos = entry(self.cfg, "videos")
        self.assertTrue(videos.get("list"))
        self.assertEqual(names(videos["fields"]), VIDEO_KEYS)

    def test_paths_match_site(self):
        self.assertEqual(entry(self.cfg, "profile")["path"], "_data/profile.yml")
        self.assertEqual(entry(self.cfg, "videos")["path"], "_data/videos.yml")
        self.assertEqual(entry(self.cfg, "stories")["path"], "_stories")
        self.assertEqual(entry(self.cfg, "essays")["path"], "_essays")

    def test_media_config(self):
        media = {m["name"]: m for m in self.cfg["media"]}
        images = media["images"]
        self.assertEqual((images["input"], images["output"]), ("assets/images", "/assets/images"))
        self.assertEqual(images["rename"], "safe")
        self.assertTrue({"jpg", "jpeg", "png", "webp"} <= set(images["extensions"]))
        files = media["files"]
        self.assertEqual((files["input"], files["output"]), ("assets/files", "/assets/files"))
        self.assertEqual(files["rename"], "safe")
        self.assertIn("pdf", files["extensions"])

    def test_story_filename_pattern(self):
        self.assertEqual(entry(self.cfg, "stories")["filename"], "{year}-{month}-{day}-{primary}.md")

    def test_required_story_fields(self):
        req = {f["name"] for f in entry(self.cfg, "stories")["fields"] if f.get("required")}
        self.assertEqual(req, {"headline", "outlet", "date", "original_url"})

    def test_frame_layout_values_match_template(self):
        frames = subfields(entry(self.cfg, "essays")["fields"], "frames")
        layout = [f for f in frames if f["name"] == "layout"][0]
        self.assertEqual(layout["options"]["values"], ["full", "pair", "inset"])


@unittest.skipUnless(fixtures_on(), "needs tests/build_with_fixtures.sh")
class CmsEdgeCasesTest(unittest.TestCase):
    def test_future_dated_story_still_published(self):
        self.assertTrue((site_dir() / "stories" / "future-dated" / "index.html").is_file())


if __name__ == "__main__":
    unittest.main()
