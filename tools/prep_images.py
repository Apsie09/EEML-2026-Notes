#!/usr/bin/env python3
"""Image pipeline for EEML notes: survey, crop, tile, and export figures."""

import argparse, csv, json, sys
from pathlib import Path

from PIL import Image, ImageOps, ImageDraw
import pillow_heif

pillow_heif.register_heif_opener()

EXTS = {".heic", ".heif", ".png", ".jpg", ".jpeg"}
READ_LIMIT = 1500       # long edge above which the reader downscales
TILE_OVERLAP = 0.12

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"


def rel(p: Path) -> str:
    p = p.resolve()
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def find_images(target: Path):
    target = target.resolve()
    if target.is_file():
        return [target]
    return sorted(
        p for p in target.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTS
    )


def load(path: Path) -> Image.Image:
    """Open any supported format, honour EXIF rotation, return RGB."""
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    return im.convert("RGB")


def parse_box(spec, size):
    """Accept 'l,t,r,b' in pixels or fractions of the frame."""
    w, h = size
    vals = [float(v) for v in spec.split(",")]
    if max(vals) <= 1.0:
        l, t, r, b = vals[0] * w, vals[1] * h, vals[2] * w, vals[3] * h
    else:
        l, t, r, b = vals
    return (int(l), int(t), int(r), int(b))


def tile(im: Image.Image, limit=READ_LIMIT, overlap=TILE_OVERLAP):
    """Split into overlapping tiles so each tile's long edge is under limit."""
    w, h = im.size
    if max(w, h) <= limit:
        return [((0, 0, w, h), im)]
    nx = max(1, -(-w // int(limit * (1 - overlap))))
    ny = max(1, -(-h // int(limit * (1 - overlap))))
    step_x = (w - limit) / max(1, nx - 1) if nx > 1 else 0
    step_y = (h - limit) / max(1, ny - 1) if ny > 1 else 0
    out = []
    for j in range(ny):
        for i in range(nx):
            l = int(i * step_x) if nx > 1 else 0
            t = int(j * step_y) if ny > 1 else 0
            box = (l, t, min(l + limit, w), min(t + limit, h))
            out.append((box, im.crop(box)))
    return out


def cmd_survey(args):
    """Contact sheets: many thumbnails per image read, for classification."""
    imgs = find_images(Path(args.target))
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    cols, rows = args.cols, args.rows
    per = cols * rows
    cell = args.cell
    label_h = 26
    manifest = []
    for page, start in enumerate(range(0, len(imgs), per), 1):
        chunk = imgs[start:start + per]
        sheet = Image.new("RGB", (cols * cell, rows * (cell + label_h)), "white")
        draw = ImageDraw.Draw(sheet)
        for k, p in enumerate(chunk):
            try:
                im = load(p)
            except Exception as e:
                print(f"  !! {p}: {e}", file=sys.stderr)
                continue
            th = im.copy()
            th.thumbnail((cell, cell))
            cx = (k % cols) * cell + (cell - th.width) // 2
            cy = (k // cols) * (cell + label_h)
            sheet.paste(th, (cx, cy + (cell - th.height) // 2))
            tag = f"{k+1}. {p.name}"
            draw.text((( k % cols) * cell + 4, cy + cell + 6), tag, fill="black")
            manifest.append({"sheet": page, "cell": k + 1, "source": rel(p)})
        name = f"{args.name}_sheet{page:02d}.jpg"
        sheet.save(outdir / name, quality=88)
        print(f"{outdir / name}  ({len(chunk)} images)")
    (outdir / f"{args.name}_manifest.json").write_text(json.dumps(manifest, indent=1))


def detect_screen(im: Image.Image, margin=0.02, frac=0.30):
    """Bounding box of the projected screen: the large bright region.

    Every lecture photo in this set is a shot of a projector screen, which is far
    brighter than the room. Threshold on luminance, then take the contiguous span
    of rows and columns that are mostly bright. Returns a box in full-frame pixels,
    widened by `margin` so a top line of writing is never clipped.
    """
    import numpy as np
    small = im.convert("L")
    small.thumbnail((600, 600))
    a = np.asarray(small, dtype=float)
    thr = a.max() * 0.62
    mask = a > thr
    if mask.mean() < 0.01:
        return None
    rows = mask.mean(axis=1) > frac
    cols = mask.mean(axis=0) > frac
    if not rows.any() or not cols.any():
        return None
    ys, xs = np.flatnonzero(rows), np.flatnonzero(cols)
    t, b = ys[0] / a.shape[0], (ys[-1] + 1) / a.shape[0]
    l, r = xs[0] / a.shape[1], (xs[-1] + 1) / a.shape[1]
    l, t = max(0.0, l - margin), max(0.0, t - margin)
    r, b = min(1.0, r + margin), min(1.0, b + margin)
    W, H = im.size
    return (int(l * W), int(t * H), int(r * W), int(b * H))


def cmd_screens(args):
    """Auto-crop each photo to its projector screen at full resolution."""
    imgs = find_images(Path(args.target))
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for p in imgs:
        im = load(p)
        box = detect_screen(im, margin=args.margin)
        if box is None:
            print(f"{p.name}: NO SCREEN FOUND, skipped")
            manifest.append({"out": "", "source": rel(p), "full_size": im.size,
                             "box": "", "out_size": "", "note": "no screen found"})
            continue
        crop = im.crop(box)
        fw, fh = im.size
        cover = (crop.width * crop.height) / (fw * fh)
        if args.limit and max(crop.size) > args.limit:
            crop2 = crop.copy()
            crop2.thumbnail((args.limit, args.limit), Image.LANCZOS)
        else:
            crop2 = crop
        out = outdir / f"{p.stem}.jpg"
        crop2.save(out, quality=args.quality)
        note = "LOW COVERAGE, check" if cover < 0.06 else ""
        print(f"{p.name}: {fw}x{fh} -> box={box} crop={crop.size} saved={crop2.size} "
              f"cover={cover:.0%} {note}")
        manifest.append({"out": out.name, "source": rel(p), "full_size": im.size,
                         "box": box, "out_size": crop2.size, "note": note})
    write_manifest(outdir / "manifest.csv", manifest)


def cmd_locate(args):
    """Downscaled full frame with a percentage grid, to read crop coords off."""
    imgs = find_images(Path(args.target))
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    for p in imgs:
        im = load(p)
        im.thumbnail((args.size, args.size))
        w, h = im.size
        d = ImageDraw.Draw(im)
        for i in range(1, 10):
            x, y = w * i / 10, h * i / 10
            d.line([(x, 0), (x, h)], fill=(255, 0, 0), width=1)
            d.line([(0, y), (w, y)], fill=(0, 128, 255), width=1)
            d.text((x + 2, 2), f".{i}", fill=(255, 0, 0))
            d.text((2, y + 2), f".{i}", fill=(0, 90, 200))
        out = outdir / f"{p.stem}_grid.jpg"
        im.save(out, quality=80)
        print(f"{out}  frame={load(p).size}")


def cmd_tiles(args):
    """Crop to the board region at full resolution, then tile for reading."""
    imgs = find_images(Path(args.target))
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for p in imgs:
        im = load(p)
        full = im.size
        if args.crop:
            im = im.crop(parse_box(args.crop, full))
        stem = p.stem
        pieces = tile(im, args.limit)
        single = len(pieces) == 1
        for n, (box, piece) in enumerate(pieces, 1):
            name = f"{stem}.jpg" if single else f"{stem}_t{n}.jpg"
            piece.save(outdir / name, quality=args.quality)
            manifest.append({
                "out": name, "source": rel(p),
                "full_size": full, "crop": args.crop or None,
                "tile_box": box, "tile_size": piece.size,
            })
        print(f"{p.name}: {full[0]}x{full[1]} -> {im.size[0]}x{im.size[1]} in {len(pieces)} tile(s)")
    write_manifest(outdir / "manifest.csv", manifest)


def render_page(pdf: Path, page: int, dpi: int) -> Image.Image:
    """Render one PDF page to a PIL image via pdftoppm."""
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as td:
        stem = Path(td) / "pg"
        subprocess.run(
            ["pdftoppm", "-r", str(dpi), "-f", str(page), "-l", str(page),
             "-png", str(pdf), str(stem)],
            check=True, capture_output=True,
        )
        hits = sorted(Path(td).glob("pg*.png"))
        if not hits:
            raise RuntimeError(f"pdftoppm produced nothing for {pdf} p{page}")
        return Image.open(hits[0]).convert("RGB")


def cmd_deckpages(args):
    """Render deck pages for inspection, so crop boxes can be chosen."""
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    for page in [int(p) for p in args.pages.split(",")]:
        im = render_page(Path(args.pdf), page, args.dpi)
        out = outdir / f"p{page:03d}.jpg"
        im.save(out, quality=88)
        print(f"{out}  {im.size}")


def cmd_deckfig(args):
    """Extract a figure straight from a slide deck page into figures/."""
    im = render_page(Path(args.pdf), args.page, args.dpi)
    full = im.size
    if args.crop:
        im = im.crop(parse_box(args.crop, full))
    if args.max_width and im.width > args.max_width:
        im = im.resize(
            (args.max_width, round(im.height * args.max_width / im.width)),
            Image.LANCZOS,
        )
    clean = Image.new("RGB", im.size, "white")
    clean.paste(im)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    clean.save(out, quality=args.quality, optimize=True)
    kb = out.stat().st_size / 1024
    print(f"{out}  {clean.size[0]}x{clean.size[1]}  {kb:.0f} kB  "
          f"<- {Path(args.pdf).name} p{args.page} crop={args.crop}")
    append_manifest(BUILD / "figures_manifest.csv", {
        "out": rel(out), "source": f"{rel(Path(args.pdf))}#p{args.page}",
        "full_size": f"{full[0]}x{full[1]}", "crop": args.crop or "",
        "rotate": 0, "final_size": f"{clean.size[0]}x{clean.size[1]}",
        "kb": round(kb),
    })


def cmd_figure(args):
    """Export a cropped, EXIF-stripped, recompressed figure for the PDF."""
    p = Path(args.target)
    im = load(p)
    full = im.size
    if args.crop:
        im = im.crop(parse_box(args.crop, full))
    if args.rotate:
        im = im.rotate(args.rotate, expand=True, resample=Image.BICUBIC)
    if args.max_width and im.width > args.max_width:
        im = im.resize(
            (args.max_width, round(im.height * args.max_width / im.width)),
            Image.LANCZOS,
        )
    clean = Image.new("RGB", im.size)     # new image carries no EXIF
    clean.paste(im)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    clean.save(out, quality=args.quality, optimize=True)
    kb = out.stat().st_size / 1024
    print(f"{out}  {clean.size[0]}x{clean.size[1]}  {kb:.0f} kB  <- {p.name} crop={args.crop}")
    log = BUILD / "figures_manifest.csv"
    row = {
        "out": rel(out), "source": rel(p),
        "full_size": f"{full[0]}x{full[1]}", "crop": args.crop or "",
        "rotate": args.rotate, "final_size": f"{clean.size[0]}x{clean.size[1]}",
        "kb": round(kb),
    }
    append_manifest(log, row)


def write_manifest(path, rows):
    if not rows:
        return
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"manifest: {path}")


def append_manifest(path, row):
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if new:
            w.writeheader()
        w.writerow(row)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("survey", help="contact sheets for cheap classification")
    s.add_argument("target")
    s.add_argument("--out", default=str(BUILD / "survey"))
    s.add_argument("--name", required=True)
    s.add_argument("--cols", type=int, default=4)
    s.add_argument("--rows", type=int, default=3)
    s.add_argument("--cell", type=int, default=360)
    s.set_defaults(func=cmd_survey)

    sc = sub.add_parser("screens", help="auto-crop each photo to its projector screen")
    sc.add_argument("target")
    sc.add_argument("--out", required=True)
    sc.add_argument("--margin", type=float, default=0.02)
    sc.add_argument("--limit", type=int, default=READ_LIMIT)
    sc.add_argument("--quality", type=int, default=92)
    sc.set_defaults(func=cmd_screens)

    lo = sub.add_parser("locate", help="grid overlay to read crop coords off")
    lo.add_argument("target")
    lo.add_argument("--out", default=str(BUILD / "locate"))
    lo.add_argument("--size", type=int, default=900)
    lo.set_defaults(func=cmd_locate)

    t = sub.add_parser("tiles", help="crop at full res, tile under the read limit")
    t.add_argument("target")
    t.add_argument("--out", required=True)
    t.add_argument("--crop", help="l,t,r,b in px or fractions")
    t.add_argument("--limit", type=int, default=READ_LIMIT)
    t.add_argument("--quality", type=int, default=92)
    t.set_defaults(func=cmd_tiles)

    dp = sub.add_parser("deckpages", help="render deck pages to pick crops from")
    dp.add_argument("pdf")
    dp.add_argument("--pages", required=True, help="comma-separated page numbers")
    dp.add_argument("--out", required=True)
    dp.add_argument("--dpi", type=int, default=110)
    dp.set_defaults(func=cmd_deckpages)

    df = sub.add_parser("deckfig", help="extract a figure from a slide deck page")
    df.add_argument("pdf")
    df.add_argument("--page", type=int, required=True)
    df.add_argument("--out", required=True)
    df.add_argument("--crop", help="l,t,r,b in px or fractions of the page")
    df.add_argument("--dpi", type=int, default=220)
    df.add_argument("--max-width", type=int, default=1500)
    df.add_argument("--quality", type=int, default=84)
    df.set_defaults(func=cmd_deckfig)

    f = sub.add_parser("figure", help="export one processed figure")
    f.add_argument("target")
    f.add_argument("--out", required=True)
    f.add_argument("--crop")
    f.add_argument("--rotate", type=float, default=0)
    f.add_argument("--max-width", type=int, default=1600)
    f.add_argument("--quality", type=int, default=82)
    f.set_defaults(func=cmd_figure)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
