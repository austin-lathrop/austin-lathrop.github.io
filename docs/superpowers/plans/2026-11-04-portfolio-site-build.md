# Journalism Portfolio Site Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the approved wireframes into a live Jekyll site at `https://<username>.github.io` that the owner updates entirely through Pages CMS forms in a browser.

**Architecture:** A plugin-free Jekyll 3.10 site built natively by GitHub Pages. All copy lives in two YAML data files and two collections (`_stories`, `_essays`). Layouts render optional fields only when present, so empty sections and missing photos disappear instead of leaving holes. `.pages.yml` exposes every content file to Pages CMS as a form. A stdlib-only Python test suite checks the built `_site/` HTML.

**Tech Stack:** Jekyll 3.10 + kramdown GFM (GitHub Pages versions), Liquid, plain CSS, Pages CMS, GitHub CLI, Python 3.9 `unittest` + `html.parser` for tests.

**Spec:** `docs/superpowers/specs/2026-11-03-journalism-portfolio-design.md`. Visual reference: `wireframes/` (home.html, story-*.html, essay.html, wire.css).

## Global Constraints

- The owner never uses Terminal or edits files by hand after launch; anything they maintain must be a Pages CMS form field.
- Claude never enters credentials. The owner signs in to GitHub and authorizes `gh` themselves.
- Repository `<username>.github.io`, public, branch `main`. No GitHub Actions, no Jekyll plugins (GitHub Pages safe mode).
- Commits use the owner's GitHub noreply address, never austinlathrop132@gmail.com.
- **`assets/cv.pdf` is never committed until the owner chooses which CV to publish** (Task 8 gate). Until then it stays in `.gitignore`.
- Type: Newsreader (headlines, story text) and Public Sans (metadata), from Google Fonts. Copy is sentence case. No all-caps labels, no "→" on links.
- Story pages: `<link rel="canonical">` to `original_url`, credit line "Originally published by {outlet} on {date}.", source links open in a new tab.
- Lead photos are never upscaled past natural width; home lead tiles crop to 3:2.
- No outlet-hosted images are hotlinked; all images live in `assets/images/`.
- Responsive to 375px with no horizontal scroll; visible keyboard focus; `prefers-reduced-motion` respected.
- Byline "By Austin Lathrop". Email austinlathrop132@gmail.com. LinkedIn https://www.linkedin.com/in/austin-lathrop-658bb330a/.

## Review Focus

1. **Story text saved from Pages CMS' rich-text editor** may arrive as HTML or Markdown, and with `after_paragraph` higher than the paragraph count. Every photo must still appear (extra ones at the end), never silently dropped. Tested in Task 4.
2. **Optional profile fields left blank** (no portrait, no CV, no availability, no LinkedIn) must remove their element entirely: no empty `<img>`, no `href=""`, no dangling "Download CV" button. Tested in Task 3.
3. **Headlines with apostrophes, quotes and ampersands** (e.g. "Athens' de-icing…", "Field & Commons") must be escaped correctly in `<title>`, `og:` meta tags and link text. Tested in Task 4.
4. **Uploaded filenames with spaces, capitals or parentheses** (e.g. `IMG 0423 (1).JPG`) must still load on the live site. Handled by Pages CMS rename rules plus `| relative_url`, tested in Task 7.
5. **`lead: true` on a story with no lead photo, or on more than two stories**, must not break the home layout: photo-less leads render as rows, and only the newest two with photos fill the lead slots. Tested in Task 4.

---

## File Structure

| Path | Responsibility |
|---|---|
| `_config.yml` | Site settings, collections (`stories` → `/stories/:slug/`, `essays` → `/photo/:slug/`), excludes |
| `Gemfile` | `jekyll "~> 3.10"`, `kramdown-parser-gfm` (matches GitHub Pages) |
| `.gitignore` | `_site/`, `vendor/`, `.bundle/`, `.jekyll-cache/`, `.claude/`, `assets/cv.pdf` (until Task 8) |
| `_data/profile.yml` | Name, opening line, availability, contact, portrait, CV, outlets, About, skills |
| `_data/videos.yml` | List of videos (empty list at launch) |
| `_stories/*.md` | One file per story (four exist; converted in Task 4) |
| `_essays/*.md` | One file per photo essay (none at launch) |
| `_layouts/default.html` | `<head>` (fonts, CSS, meta and og tags), header, `{{ content }}`, contact band |
| `_layouts/story.html` | Story page with photo insertion |
| `_layouts/essay.html` | Photo essay page |
| `_includes/header.html` | Sticky header; nav links only for non-empty sections |
| `_includes/contact.html` | "Assigning a story in Northeast Georgia?" band with Email / CV |
| `_includes/figure.html` | `<figure>`: params `src`, `alt`, `caption`, `credit`, `class` |
| `_includes/video-embed.html` | YouTube/Vimeo URL to iframe; param `url`, `title` |
| `index.html` | Home page: intro, Writing, Photo, Video, About, footer |
| `assets/css/site.css` | All styles (from `wireframes/wire.css` and page styles, minus `.note`, `.sample-flag`, `.ph`) |
| `assets/images/` | All photos (seven story images already in `assets/images/stories/`) |
| `.pages.yml` | Pages CMS forms |
| `tests/sitelib.py` | Test helpers: `load(path) -> Page`, `Page.find_all(tag, **attrs)`, `Page.text()`, `site_dir()` |
| `tests/test_*.py` | One module per task's behavior |
| `tests/fixtures/` | Sample essay, videos and edge-case stories, used only by `tests/build_with_fixtures.sh` |
| `README.md` | One page: how to update the site with Pages CMS (owner-facing) |

Build: `bundle exec jekyll build` → `_site/`. Test: `python3 -I -m unittest discover -s tests -v` (reads `SITE_DIR`, default `_site`).

---

### Task 1: GitHub CLI, owner sign-in, repository identity

**Files:**
- Create: `~/.local/bin/gh` (outside the repo)

**Interfaces:**
- Produces: `GH_USER` (owner's GitHub login), noreply email `"<id>+<login>@users.noreply.github.com"`, a working `gh` on PATH via `~/.local/bin`.

- [ ] **Step 1: Ask the owner to approve the download** (filename, source github.com/cli/cli/releases, approximate size), per the session's download rule. Do not proceed without a clear yes.
- [ ] **Step 2: Install** the latest macOS arm64 release zip into a fresh empty temp dir, verify its SHA-256 against the release's `checksums.txt`, and copy only the `gh` binary to `~/.local/bin/gh`.
  Run: `~/.local/bin/gh --version` → prints `gh version 2.x`.
- [ ] **Step 3: Owner signs in.** Start `~/.local/bin/gh auth login --hostname github.com --git-protocol https --web` in a Terminal tab the owner can see (`run_in_terminal`), and walk them through copying the one-time code into the browser page it opens.
  Run: `~/.local/bin/gh auth status` → "Logged in to github.com account <login>".
- [ ] **Step 4: Record identity.** `gh api user --jq '.login, .id'` gives `GH_USER` and the id. Set repo-local git config in Task 2 (`user.name "Austin Lathrop"`, `user.email "<id>+<login>@users.noreply.github.com"`), plus `gh auth setup-git`.

### Task 2: Jekyll scaffold, local toolchain, test harness

**Files:**
- Create: `_config.yml`, `Gemfile`, `.gitignore`, `tests/sitelib.py`, `tests/test_build.py`, `index.html` (temporary one-line page)

**Interfaces:**
- Consumes: Task 1 identity.
- Produces: `bundle exec jekyll build` works; `tests/sitelib.py` with `site_dir() -> pathlib.Path`, `load(relpath: str) -> Page`, `Page.find_all(tag: str, **attrs) -> list[dict]` (each dict has `attrs` and `text`), `Page.text() -> str`, `Page.raw: str`.

- [ ] **Step 1:** `git init -b main` in the project root, set repo-local identity from Task 1, and write `.gitignore` per File Structure.
- [ ] **Step 2: Write the failing test** `tests/test_build.py::test_site_builds` asserting `site_dir()/"index.html"` exists, and `test_no_unrendered_liquid` asserting no `.html` file under `site_dir()` contains `{{` or `{%`.
- [ ] **Step 3:** Run `python3 -I -m unittest discover -s tests -v`. Expected: FAIL (no `_site`).
- [ ] **Step 4: Toolchain.** `bundle config set --local path vendor/bundle && bundle install` with the system Ruby. If install fails on Ruby 2.6, stop and tell the owner in one paragraph, offering two choices: install a user-local Ruby (no admin), or verify through GitHub's build only (Task 8). Don't pick for them.
- [ ] **Step 5:** `_config.yml`: `title: Austin Lathrop`, `url: https://<GH_USER>.github.io`, `markdown: kramdown`, `kramdown: {input: GFM}`, the collections above with `output: true`, `exclude: [docs, wireframes, tests, vendor, Gemfile, Gemfile.lock, README.md, .pages.yml]`. Then `bundle exec jekyll build`.
- [ ] **Step 6:** Rerun tests. Expected: PASS.
- [ ] **Step 7: Commit** `git add -A && git commit -m "chore: scaffold Jekyll site and test harness"`. Check that `assets/cv.pdf` is not staged (`git ls-files assets/cv.pdf` prints nothing).

### Task 3: Base layout, styles, profile-driven home (intro, About, footer)

**Files:**
- Create: `_data/profile.yml`, `_layouts/default.html`, `_includes/header.html`, `_includes/contact.html`, `assets/css/site.css`, `tests/test_profile.py`
- Modify: `index.html`

**Interfaces:**
- Produces: `site.data.profile` keys: `name`, `opening_line`, `availability`, `email`, `linkedin`, `portrait`, `portrait_alt`, `cv`, `outlets` (list of strings), `about` (list of strings), `skills` (list of `{label, value}`). Layout front matter: `title`, `description`, `image` (for og tags). `site.css` classes reused from the wireframes (`.site-head`, `.wrap`, `.btn`, `.btn-solid`, `.section`, `.section-head`, `.statement`, `.published`, `.about`, `.skills`, `.contact`).

- [ ] **Step 1: Write failing tests** in `tests/test_profile.py` against `index.html`:
  - `test_header_has_name_and_email`: `.wordmark` text == "Austin Lathrop"; an `a.btn-solid` has `href="mailto:austinlathrop132@gmail.com"`.
  - `test_opening_line`: `h1.statement` text == "I report on agriculture, rural communities and the environment in Northeast Georgia."
  - `test_outlets`: `.published li` texts == ["The Oglethorpe Echo", "Grady Newsource"].
  - `test_linkedin`: a link with href == the LinkedIn URL and `rel` containing `noopener`.
  - `test_cv_hidden_without_file`: with `cv` empty in the launch profile, no element contains text "Download CV".
  - `test_portrait_hidden_without_file`: no `img` inside `.intro`, and no element with class `ph`.
  - `test_no_empty_hrefs`: no `a` with `href` "" or "#", across all built pages.
- [ ] **Step 2:** Build and run; expected FAIL.
- [ ] **Step 3: Implement.** `profile.yml` copy comes from `wireframes/home.html`: opening line, availability "Available for freelance assignments. Based in Athens, Georgia.", three About paragraphs, five skills (Beats, Sources and data, Visual, Education, Coverage area), `cv: ""`, `portrait: ""`. `site.css` merges `wireframes/wire.css` with the inline page styles of home/story/essay wireframes, without the annotation, sample and placeholder rules, and with color as custom properties (`--paper --ink --ink-2 --rule --box --accent`) so Task 6 can swap them. Every optional field is wrapped in `{% if %}`. Each page gets `og:title`, `og:description`, `og:image` (absolute via `absolute_url`), and all text is passed through `| escape`.
- [ ] **Step 4:** Build and run; expected PASS.
- [ ] **Step 5: Commit** `feat: base layout, styles and profile-driven home sections`.

### Task 4: Stories: collection, story page, home Writing section

**Files:**
- Create: `_layouts/story.html`, `_includes/figure.html`, `tests/test_stories.py`, `tests/fixtures/_stories/2026-01-01-edge-case.md`, `tests/build_with_fixtures.sh`
- Modify: `_stories/*.md` (four files), `index.html`

**Interfaces:**
- Consumes: `default.html`, `figure.html` params `src, alt, caption, credit, class`.
- Produces: story front matter keys `headline, dek, outlet, date, original_url, lead, image, image_alt, image_caption, image_credit, photos[] {image, alt, caption, credit, after_paragraph}`. URL `/stories/<slug>/` where slug drops the date prefix (e.g. `/stories/beef-prices/`). `tests/build_with_fixtures.sh` copies the repo to a temp dir, overlays `tests/fixtures/`, builds to `$SITE_DIR`, then runs the suite with `FIXTURES=1`.

- [ ] **Step 1: Convert the four story files.** Replace each `{% include figure.html … %}` line with a `photos` entry whose `after_paragraph` is the 1-based count of `<p>` paragraphs before it (beef chart → 3; Miller Learning Center → 3; curb gravel → the paragraph starting "Sand, used far more heavily"). Image paths become `/assets/images/stories/...`. Keep all text and source links unchanged.
- [ ] **Step 2: Write failing tests** in `tests/test_stories.py`:
  - `test_story_pages_exist`: `stories/beef-prices/index.html`, `stories/ffa-busy-fall/…`, `stories/4h-program-assistant/…`, `stories/athens-de-icing/…` exist.
  - `test_canonical_and_credit`: on beef-prices, `link[rel=canonical]` href == its `original_url`; page text contains "Originally published by The Oglethorpe Echo on October 7, 2026."
  - `test_inline_photo_position`: on beef-prices, the chart `figure` is the next sibling element after the 3rd `<p>` of `.body`.
  - `test_lead_photo_not_upscaled`: `assets/css/site.css` (built) has a `.lead-figure img` rule with `width: auto` and `max-width: 100%`, and lead `img` tags carry no `width` attribute. CMS uploads have no stored pixel size, so this must work from CSS alone.
  - `test_home_writing_order`: home `.leads` holds beef-prices then athens-de-icing; `.clips` rows hold ffa-busy-fall then 4h-program-assistant; all hrefs are `/stories/<slug>/`.
  - `test_next_story_wraps`: athens-de-icing's "Next story" links to `/stories/beef-prices/`.
  - `test_escaping` (Review Focus 3): `<title>` of athens-de-icing contains `Athens&#39; de-icing` or `Athens' de-icing`, never a raw broken attribute; the `og:title` content attribute parses back to "Athens' de-icing chemicals raise waterway concerns".
  - Fixture-only (`FIXTURES=1`), using `edge-case.md`, which has headline `Q&A: "Quotes" & 'apostrophes'`, `lead: true`, no `image`, body written as raw HTML `<p>` tags, and one `photos` entry with `after_paragraph: 99`:
    - `test_photo_beyond_last_paragraph_appended` (Review Focus 1): the figure appears after the last paragraph.
    - `test_lead_without_image_renders_as_row` (Review Focus 5): edge-case appears in `.clips`, not `.leads`.
- [ ] **Step 3:** Build (plain and fixtures) and run; expected FAIL.
- [ ] **Step 4: Implement `story.html`.** Header (source line, headline, dek, byline), lead figure, the rail (Published in, Date, Reading time = words/230 rounded up, "Read the original"), body with photo insertion, credit, next story, contact band. Photo insertion:
  ```liquid
  {% assign parts = content | split: '</p>' %}
  {% for part in parts %}{% assign n = forloop.index %}{{ part }}{% unless forloop.last %}</p>
    {% for ph in page.photos %}{% if ph.after_paragraph == n %}{% include figure.html … class="inline" %}{% endif %}{% endfor %}{% endunless %}
  {% endfor %}
  {% for ph in page.photos %}{% if ph.after_paragraph >= parts.size %}{% include figure.html … class="inline" %}{% endif %}{% endfor %}
  ```
  (The paragraph count is `parts.size - 1`, so in-loop placement covers 1…count and the final loop covers anything higher. Nothing is placed twice.) Home Writing: `{% assign sorted = site.stories | sort: 'date' | reverse %}`. Leads are the first two with `lead` and `image`; rows are everything else.
- [ ] **Step 5:** Build both ways and run; expected PASS.
- [ ] **Step 6: Commit** `feat: story pages with inline photos and home writing section`.

### Task 5: Photo essays and videos (hidden until added)

**Files:**
- Create: `_layouts/essay.html`, `_includes/video-embed.html`, `_data/videos.yml` (`[]`), `tests/test_optional_sections.py`, `tests/fixtures/_essays/flood-season.md`, `tests/fixtures/_data/videos.yml`
- Modify: `index.html`, `_includes/header.html`

**Interfaces:**
- Produces: essay front matter `title, dek, location, dates, outlet, published_url, cover, frames[] {image, caption, layout: full|pair|inset}, reporting_note`; URL `/photo/<slug>/`. `videos.yml` items `{title, outlet, year, runtime, role, url, lead}`. `video-embed.html` maps `youtube.com/watch?v=ID` and `youtu.be/ID` to `https://www.youtube-nocookie.com/embed/ID`, and `vimeo.com/ID` to `https://player.vimeo.com/video/ID`. Any other URL renders a plain link titled "Watch {title}".

- [ ] **Step 1: Write failing tests:**
  - `test_sections_hidden_at_launch`: home has no `#photo` or `#video` element; header nav has exactly Writing and About.
  - Fixtures: `test_essay_grid_and_page`: home `#photo` has one tile linking to `/photo/flood-season/`, and that page has as many `figure`s as the fixture has frames, with `.pair` wrapping consecutive `pair` frames.
  - Fixtures: `test_video_embeds`: a YouTube watch URL becomes an `iframe` with a youtube-nocookie src; a non-YouTube/Vimeo URL becomes a link, not an iframe; the nav now includes Photo and Video.
- [ ] **Step 2:** Run; expected FAIL.
- [ ] **Step 3: Implement** from `wireframes/essay.html` and the home Video section. Sections and nav links are wrapped in `{% if site.essays.size > 0 %}` / `{% if site.data.videos.size > 0 %}`. Fixture content comes from the wireframe sample ("Flood Season"), marked as fixture in its front matter.
- [ ] **Step 4:** Run both builds; expected PASS.
- [ ] **Step 5: Commit** `feat: photo essays and videos, hidden until content exists`.

### Task 6: Visual design choice (owner decision)

**Files:**
- Modify: `assets/css/site.css` (custom property values only)

- [ ] **Step 1:** Make two palettes as alternative `:root` blocks, each 4–6 named hex values. Run them through the frontend-design plan, review and self-critique: no cream-and-terracotta, no black-and-acid defaults. Each palette gets one accent, used only on links and focus rings.
- [ ] **Step 2:** Serve `_site` locally, screenshot the home page and the beef-prices story at desktop and phone widths for each palette, and show the owner both side by side.
- [ ] **Step 3:** Apply the owner's pick, remove the other, and check WCAG AA contrast for `--ink-2` on `--paper` and `--accent` on `--paper` (≥ 4.5:1, computed in a test `tests/test_contrast.py::test_text_contrast` that parses the `:root` values).
- [ ] **Step 4:** Build and run all tests; expected PASS. **Commit** `style: apply chosen palette`.

### Task 7: Pages CMS configuration

**Files:**
- Create: `.pages.yml`, `tests/test_pages_cms.py`, `README.md`

**Interfaces:**
- Consumes: every front matter and data key named in Tasks 3–5.

- [ ] **Step 1: Write failing test** `tests/test_pages_cms.py`. A minimal YAML reader is not in the stdlib, so the test first tries `import yaml`, and if that's missing, runs `ruby -ryaml -rjson -e 'puts JSON.dump(YAML.load_file(".pages.yml"))'` and parses the JSON.
  - `test_all_template_fields_editable`: every key listed in the Interfaces of Tasks 3–5 appears as a field `name` in the matching `.pages.yml` entry.
  - `test_media_config`: media `input: assets/images`, `output: /assets/images`; extensions include jpg, jpeg, png, webp, pdf; rename rule set to slugify filenames (Review Focus 4).
  - `test_story_filename_pattern`: stories `filename` == `"{year}-{month}-{day}-{primary}.md"`.
- [ ] **Step 2:** Run; expected FAIL.
- [ ] **Step 3: Implement `.pages.yml`** following pagescms.org/docs/configuration. Use plain-word labels and help text ("Summary shown on the home page", "Show this photo after paragraph number", "Feature on home page (needs a lead photo)"). Make headline, outlet, date and link required. Use the rich-text type for the story body. Also write `README.md`: a short, numbered, plain-English guide to adding a story, adding photos, filling the portrait and swapping the CV.
- [ ] **Step 4:** Run; expected PASS. **Commit** `feat: Pages CMS forms and owner guide`.

### Task 8: Publish to GitHub Pages

- [ ] **Step 1: CV gate.** Ask the owner: publish the current CV (shows phone number and ZIP codes), wait for a public version, or launch without a CV button. Only on an explicit answer, either remove `assets/cv.pdf` from `.gitignore` and set `profile.cv: /assets/cv.pdf`, or leave it out.
- [ ] **Step 2:** Confirm with the owner before creating the public repository (this is outward-facing). Then run `gh repo create <GH_USER>.github.io --public --source . --push`.
- [ ] **Step 3:** Ensure Pages builds from `main` / root: `gh api repos/<GH_USER>/<GH_USER>.github.io/pages` (create with `-X POST -f source[branch]=main -f source[path]=/` if 404). Poll `.../pages/builds/latest` until `status` is `built`. If `errored`, read the error and fix.
- [ ] **Step 4: Verify live.** In the built-in browser, open `https://<GH_USER>.github.io/`, `/stories/beef-prices/` and `/stories/athens-de-icing/` at 1280 and 375 widths. Every image loads, the story links work, the CV link works (if published), and the console has no errors. Run the test suite against a fresh local build of the pushed commit; expected PASS.

### Task 9: Owner handoff in Pages CMS

- [ ] **Step 1:** Guide the owner at app.pagescms.org: open the repository, then Stories, Add entry. Fill a test story with a photo uploaded from their computer, a caption and paragraph 2 placement, then Save.
- [ ] **Step 2:** Watch the Pages build finish, then open the live home page and the new story page together with the owner. Confirm the photo appears after paragraph 2.
- [ ] **Step 3:** Owner deletes the test story in Pages CMS. Confirm it disappears from the live site after the rebuild.
- [ ] **Step 4:** Point the owner to `README.md` on GitHub as their reference, and list what's still optional: portrait, availability wording, photo essays, videos, public CV, editor permission for full-text republishing.
