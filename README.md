# EEML 2026 Lecture Notes

Summary notes from the Eastern European Machine Learning Summer School, held in Cetinje,
Montenegro, from 27 July to 1 August 2026.

Eleven lecture chapters and three synthesis chapters, 59 pages. These are notes, not a
transcript. Each lecture chapter states what the lecture was arguing, gives the three to six
ideas that carry that argument together with the mathematics where the mathematics is the
point, and closes by locating the lecture among the others.

The three synthesis chapters at the end are the reason the rest exists. They cover the ideas
that recurred across the week including two places where speakers disagreed, the open problems
raised, and an ordered queue of material worth returning to.

Download the built PDF from `master.pdf`, or build it yourself as described below.

## The week

| Day | Ch | Lecture | Speaker |
|--|--|--|--|
| Mon 27 Jul | 2 | Introduction to Deep Learning | Sarath Chandar |
| | 3 | Representational Geometry and Alignment in Neural Nets | Phillip Isola |
| | 4 | Diffusion Models | Sander Dieleman |
| Tue 28 Jul | 5 | Introduction to Reinforcement Learning | Andreea Deac |
| | 6 | Statistics: Learning to Estimate | Kyunghyun Cho |
| Wed 29 Jul | 7 | Continual Learning | Clare Lyle |
| | 8 | To Be Figured Out | Razvan Pascanu |
| Thu 30 Jul | 9 | ML for Mathematics | Matija Tapuskovic |
| Fri 31 Jul | 10 | Spectral Analysis of Directed Acyclic Graphs | Isidora Stankovic |
| | 11 | Computationally-Efficient Learning | Dan Alistarh |
| Sat 1 Aug | 12 | A Modern Tutorial on Geometric Deep Learning | Petar Velickovic |

Four tutorial notebooks also ran during the week, on reinforcement learning, multimodal
learning, mechanistic interpretability and quantization. They are not written up here because
they are self contained and better worked through directly. Lecture chapters point to the
matching notebook where one exists.

## Building

Needs a LaTeX installation with `latexmk` and `biber`. On Debian or Ubuntu:

```
sudo apt install -y latexmk biber texlive-latex-recommended texlive-latex-extra \
                    texlive-fonts-recommended texlive-bibtex-extra \
                    texlive-pictures texlive-science
```

Then:

| Command | What it does |
|--|--|
| `make` | builds `master.pdf` |
| `make check` | fails on undefined references, undefined citations, missing files, overfull lines and em dashes |
| `make pages` | prints the page count of every chapter |
| `make clean` | removes build products |

## Figures

All 25 figures are reproduced from the speakers' own slide decks, or from photographs of
slides projected during the two lectures where no deck was distributed. Copyright in that
material stays with the respective speakers. The figures appear here with the permission of
the EEML organisers. Any speaker who would rather a figure were removed can open an issue and
it will be taken down.

Every caption names the lecture the figure came from. One figure is not an extract: the
greedy layerwise pretraining diagram in Chapter 2 is redrawn in TikZ, because that lecture
distributed no deck.

`tools/prep_images.py` is the pipeline that produced the figures. It converts HEIC, finds the
projector screen in a photograph, crops at full resolution, and exports figures with metadata
stripped. Regenerating the figures needs the original decks, which are not in this repository.

## Accuracy

Every displayed equation was checked against its source slide at full resolution rather than
against extracted text, because text extraction garbles mathematics. One transcription error
was found that way and corrected. Where a slide's notation was changed, for instance to avoid
a symbol clashing across two lectures, the chapter's Notation section says so.

Anything in these notes that did not come from a lecture sits in a marked box, so it is always
clear which claims belong to a speaker and which are the author's own.

## Reuse

The written text and the tooling are the author's own work and may be reused with attribution.
The figures are not covered by that, for the reason given above.
