# -*- coding: utf-8 -*-
"""Zenn 画像サイズ チェック & 圧縮

Zenn は画像アップロード上限が 3MB。超過ファイルを検出・圧縮する。

使い方:
  python compress_images.py              # チェックのみ
  python compress_images.py --fix       # 3MB超をその場で圧縮
  python compress_images.py --fix --limit 2.5  # 余裕を見て 2.5MB 以下に
  python compress_images.py --dir ../../images/filament-md-ja --fix

依存: pip install Pillow
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    print("Pillow が必要です: pip install Pillow", file=sys.stderr)
    sys.exit(1)

DEFAULT_LIMIT_MB = 3.0
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def mb(n: int) -> float:
    return n / (1024 * 1024)


def iter_images(root: Path):
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            yield p


def save_png_bytes(im: Image.Image, colors: int | None = None) -> bytes:
    out = io.BytesIO()
    im2 = im
    if im2.mode not in ("RGB", "RGBA", "L", "LA", "P"):
        im2 = im2.convert("RGBA" if "A" in im2.getbands() else "RGB")
    if colors is not None:
        # Preserve alpha via RGBA -> quantize carefully
        if im2.mode == "RGBA":
            alpha = im2.getchannel("A")
            rgb = im2.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
            rgb = rgb.convert("RGBA")
            rgb.putalpha(alpha)
            im2 = rgb
        else:
            im2 = im2.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    im2.save(out, format="PNG", optimize=True, compress_level=9)
    return out.getvalue()


def save_jpeg_bytes(im: Image.Image, quality: int) -> bytes:
    out = io.BytesIO()
    im2 = im.convert("RGB")
    im2.save(out, format="JPEG", quality=quality, optimize=True, progressive=True)
    return out.getvalue()


def try_resize(im: Image.Image, scale: float) -> Image.Image:
    w, h = im.size
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def compress_to_limit(path: Path, limit_bytes: int) -> tuple[bool, str]:
    """Return (changed, message). Writes in-place if compressed."""
    original = path.read_bytes()
    if len(original) <= limit_bytes:
        return False, f"ok {mb(len(original)):.2f} MB"

    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    suffix = path.suffix.lower()

    candidates: list[tuple[str, bytes]] = []

    # 1) Re-encode PNG optimized / quantized
    if suffix == ".png":
        for colors in (None, 256, 128, 64):
            try:
                data = save_png_bytes(im, colors=colors)
                label = "png-opt" if colors is None else f"png-{colors}c"
                candidates.append((label, data))
                if len(data) <= limit_bytes:
                    break
            except Exception as e:
                candidates.append((f"png-fail:{e}", b""))

        # 2) Resize PNG progressively
        best = min((c for c in candidates if c[1]), key=lambda x: len(x[1]), default=None)
        base = im
        scale = 0.9
        while scale >= 0.4:
            resized = try_resize(base, scale)
            for colors in (None, 256, 128):
                data = save_png_bytes(resized, colors=colors)
                label = f"png-scale{scale:.2f}" + ("" if colors is None else f"-{colors}c")
                candidates.append((label, data))
                if len(data) <= limit_bytes:
                    scale = 0  # break outer
                    break
            else:
                scale -= 0.1
                continue
            break

        # 3) Last resort: JPEG (keep .png extension? better convert to .jpg and warn)
        # Prefer staying PNG for diagrams; try JPEG bytes only if still over
        still = [c for c in candidates if c[1]]
        if still and min(len(c[1]) for c in still) > limit_bytes:
            for q in (85, 75, 65, 55):
                data = save_jpeg_bytes(im, q)
                candidates.append((f"jpeg-q{q}", data))
                if len(data) <= limit_bytes:
                    break
            # also resized jpeg
            for scale in (0.85, 0.7, 0.55):
                resized = try_resize(im, scale)
                for q in (80, 65):
                    data = save_jpeg_bytes(resized, q)
                    candidates.append((f"jpeg-s{scale:.2f}-q{q}", data))
                    if len(data) <= limit_bytes:
                        break

    elif suffix in {".jpg", ".jpeg"}:
        for q in (85, 75, 65, 55, 45):
            data = save_jpeg_bytes(im, q)
            candidates.append((f"jpeg-q{q}", data))
            if len(data) <= limit_bytes:
                break
        scale = 0.9
        while scale >= 0.4 and all(len(c[1]) > limit_bytes for c in candidates if c[1]):
            resized = try_resize(im, scale)
            for q in (80, 65, 50):
                data = save_jpeg_bytes(resized, q)
                candidates.append((f"jpeg-s{scale:.2f}-q{q}", data))
                if len(data) <= limit_bytes:
                    break
            scale -= 0.1

    elif suffix == ".webp":
        out = io.BytesIO()
        im.save(out, format="WEBP", quality=80, method=6)
        candidates.append(("webp", out.getvalue()))
        for q in (70, 60, 50):
            out = io.BytesIO()
            im.save(out, format="WEBP", quality=q, method=6)
            candidates.append((f"webp-q{q}", out.getvalue()))
            if out.tell() <= limit_bytes:
                break

    else:
        return False, f"skip unsupported {suffix}"

    valid = [(k, v) for k, v in candidates if v]
    if not valid:
        return False, "compress failed (no candidates)"

    # Prefer under-limit; else smallest
    under = [c for c in valid if len(c[1]) <= limit_bytes]
    if under:
        # Prefer PNG under limit when original was PNG
        if suffix == ".png":
            png_under = [c for c in under if c[0].startswith("png")]
            choice = min(png_under or under, key=lambda x: len(x[1]))
        else:
            choice = min(under, key=lambda x: len(x[1]))
    else:
        choice = min(valid, key=lambda x: len(x[1]))

    label, data = choice
    if len(data) >= len(original):
        return False, f"no gain ({mb(len(original)):.2f} MB, best {label} {mb(len(data)):.2f} MB)"

    # If best is JPEG but path is .png, write .jpg and leave note — for Zenn refs stay .png
    # So if jpeg was chosen for png path, only accept if we rename OR convert back.
    # Simpler: if jpeg candidate won for .png, write as JPEG into same stem.jpg and
    # caller must update markdown. For automation, prefer staying under limit as PNG;
    # if only jpeg works, write JPEG bytes into .png is wrong.
    if suffix == ".png" and label.startswith("jpeg"):
        jpg_path = path.with_suffix(".jpg")
        jpg_path.write_bytes(data)
        # also replace png with a note file? Keep compressed png best effort AND jpg
        # Update: overwrite png only with png candidates; if need jpg, write jpg and return instruction
        png_best = min((c for c in valid if c[0].startswith("png")), key=lambda x: len(x[1]), default=None)
        if png_best and len(png_best[1]) < len(original):
            path.write_bytes(png_best[1])
        return True, (
            f"{mb(len(original)):.2f}→jpg {mb(len(data)):.2f} MB via {label} "
            f"(wrote {jpg_path.name}; update markdown refs from .png to .jpg). "
            f"png best left at {mb(len(png_best[1])) if png_best else mb(len(original)):.2f} MB"
        )

    path.write_bytes(data)
    status = "OK" if len(data) <= limit_bytes else "STILL_OVER"
    return True, f"{status} {mb(len(original)):.2f}→{mb(len(data)):.2f} MB via {label}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Zenn 3MB image checker/compressor")
    ap.add_argument(
        "--dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "images" / "filament-md-ja",
        help="画像ルート (default: images/filament-md-ja)",
    )
    ap.add_argument("--limit", type=float, default=DEFAULT_LIMIT_MB, help="上限 MB (default: 3)")
    ap.add_argument("--fix", action="store_true", help="超過ファイルを圧縮して上書き")
    ap.add_argument("--all", action="store_true", help="超過以外も一覧表示")
    args = ap.parse_args()

    root: Path = args.dir
    if not root.is_dir():
        print(f"directory not found: {root}", file=sys.stderr)
        return 1

    limit_bytes = int(args.limit * 1024 * 1024)
    files = list(iter_images(root))
    oversized = [p for p in files if p.stat().st_size > limit_bytes]

    print(f"dir: {root}")
    print(f"limit: {args.limit} MB ({limit_bytes} bytes)")
    print(f"images: {len(files)}, over limit: {len(oversized)}")
    print()

    if args.all:
        for p in files:
            print(f"  {mb(p.stat().st_size):6.2f} MB  {p.relative_to(root)}")
        print()

    if not oversized:
        print("すべて制限内です。")
        return 0

    print("超過ファイル:")
    for p in sorted(oversized, key=lambda x: -x.stat().st_size):
        print(f"  {mb(p.stat().st_size):6.2f} MB  {p.relative_to(root)}")
    print()

    if not args.fix:
        print("圧縮するには --fix を付けて再実行してください。")
        return 2

    rc = 0
    for p in oversized:
        changed, msg = compress_to_limit(p, limit_bytes)
        mark = "*" if changed else " "
        print(f"{mark} {p.relative_to(root)}: {msg}")
        if "STILL_OVER" in msg or "wrote" in msg and "update markdown" in msg:
            rc = 3
        if p.stat().st_size > limit_bytes:
            rc = 3
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
