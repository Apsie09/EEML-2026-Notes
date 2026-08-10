# EEML 2026 Lecture Notes

Summary notes from the Eastern European Machine Learning Summer School, held in Cetinje,
Montenegro, from 27 July to 1 August 2026.

Fifty-nine pages covering the eleven lectures, with three chapters at the end drawing them
together. These are notes rather than a transcript. Each lecture chapter states what the lecture
was arguing, gives the three to six ideas that carry that argument along with the mathematics
where the mathematics is the point, and closes by locating the lecture among the others.

The built book is `master.pdf`. It can also be rebuilt from source, as described below.

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

## The last three chapters

Chapter 13, **Cross-cutting Themes**, follows six ideas that surfaced in more than one lecture,
including two places where speakers reached the same territory and disagreed about what it meant.

Chapter 14, **Research Directions**, separates the open problems the speakers named from
directions inferred by putting two lectures side by side, and marks which is which.

Chapter 15, **Worth Revisiting**, is thirteen specific things from the week that reward a second
pass, each with a pointer and a reason.

## What is not here

Four tutorial notebooks also ran during the week, on reinforcement learning, multimodal learning,
mechanistic interpretability and quantization. They are not written up, since the notebooks are
self contained and better worked through directly. Lecture chapters point to the matching tutorial
where one exists.

Anything in the notes that did not come from a lecture sits in a marked editorial note, so it is
always clear which claims belong to a speaker and which do not.

## Figures

All 25 figures come from the speakers' own slide decks, or from photographs of slides projected
during the two lectures where no deck was distributed. Copyright in that material stays with the
respective speakers. They appear here with the permission of the EEML organisers, and any speaker
who would prefer a figure removed can open an issue and it will be taken down.

Every caption names the lecture the figure came from. One figure is not an extract: the greedy
layerwise pretraining diagram in Chapter 2 is redrawn, because that lecture distributed no deck.

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
| `make check` | fails on undefined references, missing files, overfull lines and em dashes |
| `make pages` | prints the page count of every chapter |
| `make clean` | removes build products |

## Corrections and reuse

Corrections are welcome. Open an issue for anything that misrepresents a lecture.

The written text is the author's own work and may be reused with attribution. The figures are not
covered by that, for the reason given above.
