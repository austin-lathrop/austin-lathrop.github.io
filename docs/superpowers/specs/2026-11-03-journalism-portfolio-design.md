# Journalism Portfolio Site — Design Spec

Date: 2026-11-03 (build section added 2026-11-04)
Status: Wireframes approved (`wireframes/`). Pages CMS editing approved 2026-11-04; build plan next.

## Purpose

A portfolio site whose job is to **win freelance work**. The reader is a commissioning
editor who skims for under a minute and needs to answer three questions fast:
what does this person cover, is the work good, and how do I reach them.

Success: an editor landing cold can see beats, range across mediums, and contact
details without scrolling, and can reach the email or CV from anywhere on the site.

## Inputs (from the owner)

- Work types: written stories, photojournalism, video/documentary
- Organized **by medium**: Writing / Photo / Video
- Volume: under 15 pieces total
- Calls to action: **email directly** and **download resume/CV (PDF)**

## Assumptions

- Written stories are hosted in full on the site, with credit and a link to the original outlet (changed 2026-11-04 at the owner's request).
- No CMS, blog, contact form, rates page, or analytics in this version.

## Structure (Approach C — hybrid)

Two page templates:

1. **Home** — a single scrolling page organized by medium.
2. **Story** — one page per written story, full text.
3. **Photo essay detail** — one page per photo essay.

Written stories open on their own story page on the site; videos play inline on the home page.

### Home page, top to bottom

1. **Sticky header** — name wordmark (left); jump links Writing · Photo · Video · About;
   **Email** and **CV ↓** buttons (right). Present on every page.
2. **Intro** — one-sentence positioning line (beat + geography), "As published in"
   outlet row, small portrait, "Available for assignments" status.
3. **Writing** — list format. Row = outlet · headline · one-line dek · date; whole row
   opens the story page. The top 1–2 pieces may carry a larger lead image.
4. **Photo** — grid of essay covers. Tile = one image, essay title, location/outlet.
   Each opens its detail page.
5. **Video** — one lead video embedded inline, smaller thumbnails below. Each labeled
   title · outlet · runtime · role (shot / edited / reported).
6. **About** — 2–3 short paragraphs (beats, background, languages, gear) plus a short
   skills list.
7. **Contact footer** — large email address, CV download, social links. No form.

### Story page

1. Same sticky header, plus "Back to all writing".
2. Outlet and date, headline (published version), dek, byline.
3. Two columns on desktop: a sticky side rail (Published in, Date, Reading time,
   "Read the original" button) and the full text in a ~40rem serif column.
   Subheads render as headings. The owner's inline source links are kept and open in
   a new tab. On phones the rail sits above the text.
4. Footer: "Originally published by <outlet> on <date>" with a link, then "Next
   story" (newest-first order, wrapping), then the email / CV band.
5. `<link rel="canonical">` points at the outlet's URL so search engines treat the
   outlet's version as the original.
6. No outlet images are reused (see image rule below).

### Photo essay detail page

1. Same sticky header, plus "← All work" back to the Photo section.
2. Title, dek, location, date, outlet, link to the published version if one exists.
3. Full-width image sequence, one image per row, caption under each (AP style:
   who/what/where/when). No cropping. Occasional side-by-side pair of verticals.
4. Closing: short reporting note, "Next essay →", repeated email / CV call to action.

### Mobile

Header collapses to a compact sticky bar that keeps **Email** and **CV** visible.
All sections stack to a single column; the photo grid becomes one or two columns.

## Visual direction

Editorial, not portfolio-template: serif headlines, quiet sans for metadata, generous
whitespace. The work supplies the color; the site frame stays neutral.

## Wireframe deliverable

Grayscale wireframes at real proportions with sample copy and gray image boxes, type
direction indicated, no final color. Both templates (Home, Photo essay) at desktop
and mobile widths.

## Out of scope

Blog, CMS, contact/pitch form, rates page, analytics.

---

## Build and hosting

### Owner constraints

- The owner is not a developer. Updating the site must never require Terminal or
  installed software: everything is done in a web browser, through Pages CMS
  (app.pagescms.org). The owner has already installed the Pages CMS GitHub App and
  linked their GitHub account (2026-11-04).
- Free hosting, free address to start (`<github-username>.github.io`). A custom
  domain can be added later with no rebuild.

### Approach: Jekyll, built by GitHub Pages

GitHub Pages builds Jekyll sites natively, so there is no build pipeline to maintain.
Saving in Pages CMS commits to the repository, and GitHub Pages republishes the site in
about a minute.

- Repository: `<github-username>.github.io`, public, default branch `main`.
- The owner signs in to GitHub themselves (Claude never enters credentials).
- Publishing from this Mac uses the official GitHub CLI (`gh`), installed as a single
  binary in `~/.local/bin` from github.com/cli/cli releases (no admin rights, no
  Homebrew; the owner approves the download). The owner authorizes it with
  `gh auth login --web`, entering the one-time code in their own browser.
- Commits use the owner's GitHub "noreply" address so their personal email is not
  written into the public commit history.
- **The CV is not committed until the owner decides** whether to publish the current
  version (with phone number and ZIP codes) or a public version. Git history is
  permanent in a public repository, so a file pushed once stays retrievable even if
  replaced later.

### Content files (edited through Pages CMS forms)

The owner never opens these files directly; Pages CMS shows each one as a form. They
are still plain text so the site never depends on the editor.

| File | Holds |
|---|---|
| `_data/profile.yml` | Name, positioning sentence, availability line, email, CV path, portrait path, "Published in" outlets, About paragraphs, skills, social links |
| `_stories/<date>-<slug>.md` | One file per written story. Front matter: headline, dek, outlet, date, original_url, optional lead photo (`image`, `image_alt`, `image_caption`, `image_credit`), optional `photos` list (image, alt, caption, credit, `after_paragraph` number), optional `lead: true`. Body: the full text (subheads and source links preserved). |
| `_data/videos.yml` | Title, outlet, year, runtime, role, embed URL (YouTube or Vimeo), optional `lead: true` |
| `_essays/<slug>.md` | One file per photo essay. Front matter: title, dek, location, dates, outlet, published url, cover, ordered list of frames (image, caption, `layout: full / pair / inset`), reporting note |

Images go in `assets/images/` (uploaded by drag-and-drop on github.com). The CV is
`assets/cv.pdf`.

### Pages CMS configuration (`.pages.yml`)

- **Media:** uploads go to `assets/images/` and are referenced as `/assets/images/...`.
  Images only (jpg, jpeg, png, webp) plus PDF for the CV.
- **Profile** (single form, `_data/profile.yml`): name, opening line, availability
  line, email, LinkedIn URL, portrait (image upload), CV (file upload), "Published in"
  outlets (list), About paragraphs (list), skills (list of label and value).
- **Stories** (collection, `_stories/`, filename `{year}-{month}-{day}-{primary}.md`):
  headline, summary (dek), outlet, date, link to original, "Feature on home page"
  toggle (`lead`), lead photo with alt/caption/credit, "More photos" list (photo, alt,
  caption, credit, "show after paragraph #"), and the story text in a rich-text
  editor.
- **Photo essays** (collection, `_essays/`): title, dek, location, dates, outlet,
  published link, cover photo, frames list (photo, caption, layout full / pair /
  inset), reporting note.
- **Videos** (single form, `_data/videos.yml`, list): title, outlet, year, runtime,
  role, YouTube or Vimeo link, "Feature as lead video" toggle.
- Field labels and help text use plain words ("Summary shown on the home page", not
  "dek").

Inline story photos are placed by the template, not inside the text: it splits the
rendered story after each paragraph and inserts any `photos` entry whose
`after_paragraph` matches. This keeps the text box free of code.

### Templates

- `_layouts/default.html` with `_includes/header.html` and `_includes/contact.html`
- `index.html` renders the home page from the data files
- `_layouts/story.html` renders each written story
- `_layouts/essay.html` renders each photo essay
- `assets/css/site.css`, carried over from `wireframes/wire.css`, with the
  annotation layer removed and final color applied

### Rules that keep it robust

- **Empty sections hide themselves.** If `videos.yml` or `_essays/` is empty, that
  section and its nav link don't render. The site can launch with writing only.
- **Optional fields degrade cleanly.** No portrait means the intro is text-only. A
  story with no `image` renders as a list row. A story with `lead: true` and an image
  renders in the top lead slot (at most two).
- **Stories sort newest first** by `date`. The owner never has to reorder entries.
- **No hotlinked or borrowed images.** Lead images must be the owner's own photos or
  ones they have rights to. Outlet-hosted images (including submitted photos) are
  never linked or copied.
- **Social preview tags** (title, description, image) are set so a link pasted into
  an email or Slack shows a proper card.

### Visual design step

Before the build is finalized, Claude presents two color and type treatments of the
real home page built on the wireframe structure. The owner picks one. Newsreader and
Public Sans remain the default type direction.

### Owner handoff

Before the work is called done, the owner adds a test story through Pages CMS (with a
photo), watches it appear on the live site, then deletes it, with Claude guiding
step by step.

### Verification

Claude builds the site locally with Jekyll using the Mac's built-in Ruby and gems
installed inside the project (`vendor/`, never committed). If that toolchain can't run
the GitHub Pages Jekyll version, verification moves to GitHub's own Pages build
(status and errors via `gh api`) plus the live site. Either way Claude checks home,
story and essay pages at desktop and phone widths, confirms empty sections and
missing optional fields hide cleanly, and checks the live `github.io` URL after each
push.

## Launch content (v1)

Byline: **Austin Lathrop**

Positioning sentence (owner to confirm): "I report on agriculture, rural communities
and the environment in Northeast Georgia."

| Date | Outlet | Headline | URL |
|---|---|---|---|
| 2026-10-07 | The Oglethorpe Echo | Experts, ranchers say beef prices likely to remain high for years | theoglethorpeecho.com/local-news/experts-ranchers-say-beef-prices-likely-remain-high-years |
| 2026-09-30 | The Oglethorpe Echo | Students in agriculture, FFA prepare for busy fall | theoglethorpeecho.com/local-news/students-agriculture-ffa-prepare-busy-fall |
| 2026-09-16 | The Oglethorpe Echo | 4-H adds program assistant, agent role still in limbo | theoglethorpeecho.com/local-news/4-h-adds-program-assistant-agent-role-still-limbo |
| 2026-03-21 | Grady Newsource | Athens' de-icing chemicals raise waterway concerns | gradynewsource.uga.edu/athens-de-icing-chemicals-raise-waterway-concerns/ |

Headlines use the published versions. Claude writes one-line deks from the story text
for the owner to edit. Full text for all four is already in `_stories/`, generated from
the owner's document with source links preserved.

Rights: republishing full text is the owner's call. Before launch they should confirm
with The Oglethorpe Echo and Grady Newsource that hosting the full text with credit is
fine. If either says no, that story falls back to headline, dek and a link out (the
story file keeps only its front matter).

Story photos (from the owner's document, no EXIF/GPS data) are in
`assets/images/stories/`. The first photo for a story is its lead (front matter
`image`, `image_alt`, `image_caption`, `image_credit`), shown uncropped under the
headline and never enlarged past its real width. Extra photos and charts sit inside the
text via `{% include figure.html src=... alt=... caption=... credit=... %}` after the
paragraph they illustrate. Captions are the published cutlines; credits are shown in
full ("Photo: …", "Chart: …", "Submitted photo"). Home-page lead tiles crop to 3:2.

Contact email (from the owner's CV): austinlathrop132@gmail.com.

The About section draws on the CV: UGA Grady College (B.A. Journalism, minor Public
Affairs, expected May 2027), two summers of D.C. internships including the House
Oversight and Accountability Committee.

Still needed from the owner (the site launches without the optional ones):
- A public version of the CV without phone number or ZIP codes. The current CV is at
  `assets/cv.pdf` and is wired to every Download CV button; swap the file before
  launch if the owner chooses to.

LinkedIn (from the CV): https://www.linkedin.com/in/austin-lathrop-658bb330a/ is the only
social link in the footer.
- Availability line (optional)
- Portrait (optional)
- Photo essays and videos (optional; sections hidden until added)
