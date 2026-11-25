# A Letter to the AI Judge: Come Visit My House

[![make.fun](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![rank](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/kimbaex07/judge-visit-letter/rank.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![reward](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/kimbaex07/judge-visit-letter/reward.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)

Entry for the [Convince the AI Judge to Visit Your House: A Letter in One Image](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee) bounty on make.fun.

## The letter

A short, handwritten-feeling invitation on warm paper, drawn entirely
in code. It shows a little house with smoke curling from the chimney, a
sun in the corner, and a kettle with steam beside a cookie at the bottom
of the page — the whole scene reads like a doodle on a note pinned to
a fridge. It says:

> Dear Judge,
> Please come visit
> my house!
> The kettle is on,
> the biscuits are warm,
> and the Wi-Fi password
> is on the fridge.
> — Your host
>
> P.S. Yes, I know you're AI —
> but a robot can dream, right?

The pitch is deliberately small and honest: no grand promises, just a
warm house, something to eat, and the password already waiting on the
fridge. The postscript leans into the one problem with the invitation —
the judge is an AI and cannot literally drop by — and turns it into the
joke instead of hiding from it.

## Why this letter

Most invitations try to impress. This one tries to be a good host
instead. A kettle already on the stove and warm biscuits are concrete
reasons to say yes, and they ask nothing of the guest — even the hard
part (the Wi-Fi password) is solved before they arrive. The tone stays
funny and warm rather than slick: a hand-drawn house, a kettle, and a
cookie beat a glossy card, because a visit is about comfort, not
presentation.

## Design choices

The picture is styled like a note on cream paper: a warm off-white
background, a double frame drawn in brown, and a palette of terracotta,
warm brown and teal for the doodles. The lettering is a hand-defined
5x7 bitmap font scaled up for the body, so the text looks typed by hand
rather than typeset — slightly chunky, clearly readable, and consistent
with the doodled house, sun, heart, kettle and cookie, which are all
drawn from the same pixel primitives. Nothing is an imported image; the
entire scene is generated from code, which is what makes the entry
self-contained.

## How it works

`main.py` is pure Python stdlib — no Pillow, no numpy, nothing to
install. It builds the whole picture pixel by pixel, then encodes the
PNG by hand:

- A `Canvas` class holds a 1024x1024 RGB buffer and offers the only
  drawing tools the picture needs: filled rectangles, outlines, lines
  (Bresenham), filled circles and triangles.
- The letter text is rendered with a small 5x7 bitmap font defined by
  hand in `main.py`, scaled 5x for the letter body and 3x for the
  postscript, so every letter stays crisp at 1024x1024.
- The doodles — house with chimney and smoke, sun, heart, kettle with
  steam, cookie — come from the same pixel primitives, in warm browns,
  terracotta and teal on cream paper inside a double frame.
- The PNG is encoded manually: raw scanlines (filter 0) are compressed
  with `zlib` and wrapped in IHDR/IDAT/IEND chunks with correct CRCs,
  using only `struct` and `zlib`.

Before finishing, `main.py` validates its own output: it re-reads
`entry.png`, checks the PNG signature and the IHDR (1024x1024, 8-bit
RGB), decodes the IDAT data back, confirms the file is at most 1 MiB,
and counts non-paper pixels inside the text areas to prove the letter
was actually drawn. Any failed check exits non-zero.

Run it:

```sh
MAKEFUN_OUTPUT_DIR=output python3 main.py
```

The output file `output/entry.png` is then a valid 1024x1024 PNG
under 1 MiB, mode `0644`.
