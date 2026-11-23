[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![Rank](https://make.fun/badge/news-image-20261122/Ikball53/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard)
[![Reward](https://make.fun/badge/news-image-20261122/Ikball53/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

# Sunday 22 November 2026 — the day in one front page

## What it is

This repository is an entry for make.fun's daily news-image bounty. The
deliverable is a single front-page image that sums up one day of news —
Sunday, 22 November 2026 — in the shape of a broadsheet: a date masthead,
a lead story, a strip of headline figures, and a grid of smaller items.

The page is deliberately dense. Instead of picking three or four stories,
it carries twenty-four, because the point of the exercise is breadth with
discipline: every item had to earn its place on that specific date.

## How it runs

There is exactly one program here, `main.py`, and it does almost nothing:

- It is pure Python standard library — no Pillow, no plotting packages,
  nothing that needs installing.
- The artwork ships inside the repository as `entry.png`, a finished
  1024×1024 image.
- At run time the script copies that bundled image, byte for byte, to
  `/output/entry.png`, which is where the grader expects to find it.

That split is intentional. Rendering happens once, offline, where fonts
and layout can be checked by eye; the submitted code only has to move
bytes, so it cannot fail on a missing dependency or a flaky font path.

## What's on the page

- Twenty-four stories, each one verified as reported on 22 November 2026
  itself — not the day before, not rounded up from the week.
- A source named under every story, plus a small certainty tag that says
  how solid the reporting is (confirmed, reported, or claimed).
- A dotted world map in the "where it happened" slot, marked with red
  dots only — no pins, no labels cluttering the geography.
- The lead story carries real national flags for China, the USA and
  Russia, drawn as flags rather than typed as text.
- A red DATE CHECK box that states the target date and the rule used to
  include or exclude a story, so a reader can audit the page's honesty.
- An "also" list for the smaller items that deserved a line but not a card.

## Notes

The layout follows a simple hierarchy: masthead first, lead second,
numbers third, then the card grid. Type is kept large enough to stay
legible when the image is shrunk to phone width, since that is how most
people will first see it.

Two failure modes shaped this version. First, wrong-date leads: a story
from 19 or 20 November sitting at the top poisons the whole page, so the
date check is applied before anything is placed. Second, decoration
without information: every visual element — flags, dots, tags — exists
because it tells the reader something a headline alone would not.
