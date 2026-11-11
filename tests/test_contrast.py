import re
import unittest

from sitelib import site_dir


def palette():
    css = (site_dir() / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    root = re.search(r":root\s*\{([^}]*)\}", css).group(1)
    return dict(re.findall(r"--(paper|ink|ink-2|rule|box|accent):\s*(#[0-9a-fA-F]{6})", root))


def luminance(hexcolor):
    def chan(c):
        c = int(c, 16) / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(hexcolor[i:i + 2]) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class ContrastTest(unittest.TestCase):
    def test_text_contrast(self):
        p = palette()
        pairs = {
            "ink on paper": (p["ink"], p["paper"]),
            "ink-2 on paper": (p["ink-2"], p["paper"]),
            "accent on paper": (p["accent"], p["paper"]),
            "paper on accent (buttons)": (p["paper"], p["accent"]),
            "ink-2 on box (contact band)": (p["ink-2"], p["box"]),
        }
        for name, (fg, bg) in pairs.items():
            self.assertGreaterEqual(contrast(fg, bg), 4.5, f"{name}: {contrast(fg, bg):.2f}")

    def test_chosen_palette(self):
        # Owner chose option A, pine green, on 2026-11-11.
        self.assertEqual(palette(), {"paper": "#ffffff", "ink": "#1c2420", "ink-2": "#55605a",
                                     "rule": "#c5cec8", "box": "#eef2ee", "accent": "#2f5d46"})

    def test_solid_buttons_use_accent(self):
        css = (site_dir() / "assets" / "css" / "site.css").read_text(encoding="utf-8")
        rule = re.search(r"\.btn-solid\s*\{([^}]*)\}", css).group(1)
        self.assertIn("var(--accent)", rule)


if __name__ == "__main__":
    unittest.main()
