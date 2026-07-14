# -*- coding: utf-8 -*-
"""Fix remaining KaTeX issues: nested-brace newcommand blocks + GFM tables."""
from __future__ import annotations

import re
from pathlib import Path

BOOK = Path(__file__).parent

MACROS: list[tuple[str, str]] = [
    (r"\fDiffuse", r"f_d"),
    (r"\fSpecular", r"f_r"),
    (r"\fGrazing", r"f_{90}"),
    (r"\fNormal", r"f_{0}"),
    (r"\cosTheta", r"\left< \cos \theta \right>"),
    (r"\schlick", r"F_{Schlick}"),
    (r"\NoL", r"n \cdot l"),
    (r"\NoV", r"n \cdot v"),
    (r"\NoH", r"n \cdot h"),
    (r"\VoH", r"v \cdot h"),
    (r"\LoH", r"l \cdot h"),
    (r"\Lout", r"L_{out}"),
    (r"\nior", r"n_{ior}"),
    (r"\fX", r"f_x"),
    (r"\Ed", r"E_d"),
    (r"\Lt", r"L_{\bot}"),
]


def remove_newcommand_dollars(text: str) -> str:
    """Remove $$ blocks that only contain \\newcommand lines."""

    def repl(m: re.Match) -> str:
        body = m.group(1)
        lines = [ln.strip() for ln in body.strip().splitlines() if ln.strip()]
        if lines and all(ln.startswith(r"\newcommand") for ln in lines):
            return "\n"
        return m.group(0)

    return re.sub(r"\$\$\s*\n?(.*?)\n?\s*\$\$", repl, text, flags=re.S)


def remove_newcommand_lines(text: str) -> str:
    # Match \newcommand{Name}{...} with nested braces in replacement
    pattern = re.compile(
        r"^\\newcommand\{[A-Za-z]+\}\{(?:[^{}]|\{[^{}]*\})*\}\s*\n",
        re.M,
    )
    return pattern.sub("", text)


def expand_macros(text: str) -> str:
    for src, dst in MACROS:
        text = text.replace(src, dst)
    text = re.sub(r"(?<![A-Za-z])\\aa(?![A-Za-z])", r"\\alpha^2", text)
    return text


def simplify_equations(text: str) -> str:
    def repl(m: re.Match) -> str:
        body = re.sub(r"\\label\{[^}]*\}", "", m.group(1)).strip()
        return f"$$\n{body}\n$$"

    text = re.sub(
        r"\$\$\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}\$\$",
        repl,
        text,
        flags=re.S,
    )
    text = re.sub(
        r"\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}",
        repl,
        text,
        flags=re.S,
    )
    text = re.sub(r"\$?\\ref\{([^}]+)\}\$?", r"`\1`", text)
    return text


def to_gfm_row(row: str) -> str:
    cells = [c.strip() for c in row.split("|")]
    while cells and cells[0] == "":
        cells = cells[1:]
    while cells and cells[-1] == "":
        cells = cells[:-1]
    return "| " + " | ".join(cells) + " |"


def convert_tables(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        s = lines[i].lstrip()
        # separator: ---|--- with optional colons/spaces
        if "|" in s and re.fullmatch(r"[\s:\-|]+", s) and "-" in s and s.count("|") >= 1:
            if out:
                prev = out[-1].lstrip()
                if "|" in prev and not prev.startswith("*"):
                    out[-1] = to_gfm_row(prev)
                    cells = [c.strip() for c in s.split("|")]
                    while cells and cells[0] == "":
                        cells = cells[1:]
                    while cells and cells[-1] == "":
                        cells = cells[:-1]
                    sep = []
                    for c in cells:
                        c2 = c.replace(" ", "")
                        if c2.startswith(":") and c2.endswith(":"):
                            sep.append(":---:")
                        elif c2.endswith(":"):
                            sep.append("---:")
                        elif c2.startswith(":"):
                            sep.append(":---")
                        else:
                            sep.append("---")
                    out.append("| " + " | ".join(sep) + " |")
                    i += 1
                    while i < len(lines):
                        body = lines[i].lstrip()
                        if not body.strip():
                            break
                        if "|" not in body:
                            break
                        if body.startswith("*表") or body.startswith("*リスト") or body.startswith("---"):
                            break
                        if body.startswith("#"):
                            break
                        out.append(to_gfm_row(body))
                        i += 1
                    continue
        out.append(lines[i])
        i += 1
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def fix_file(path: Path) -> None:
    original = path.read_text(encoding="utf-8")
    text = original
    text = remove_newcommand_dollars(text)
    text = remove_newcommand_lines(text)
    text = expand_macros(text)
    text = simplify_equations(text)
    text = text.replace(r"\chi^+", r"\chi^{+}")
    text = convert_tables(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    path.write_text(text, encoding="utf-8")
    left = text.count(r"\newcommand") + text.count(r"\NoL") + text.count(r"\fDiffuse")
    print(f"{path.name}: leftover_markers={left} changed={text != original}")


def main() -> None:
    for p in sorted(BOOK.glob("[0-9]*.md")):
        fix_file(p)


if __name__ == "__main__":
    main()
