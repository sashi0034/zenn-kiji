# -*- coding: utf-8 -*-
"""Split Filament.md.html into chapter source files and convert Markdeep quirks."""
from __future__ import annotations

import re
from pathlib import Path

SRC = Path(r"F:\Downloads\filament\docs\Filament.md.html")
OUT = Path(__file__).parent / "_src"

# (slug, title_en, start_line_1based, end_line_exclusive_1based)
CHAPTERS = [
    ("01-about", "About", 9, 18),
    ("02-overview", "Overview", 18, 62),
    ("03-notation", "Notation", 62, 107),
    ("04-material-standard", "Material system — Standard model", 107, 201),
    ("05-specular-brdf", "Specular BRDF", 201, 385),
    ("06-diffuse-brdf", "Diffuse BRDF", 385, 503),
    ("07-improving-brdfs", "Improving the BRDFs", 503, 596),
    ("08-parameterization", "Parameterization", 596, 806),
    ("09-clear-coat", "Clear coat model", 806, 926),
    ("10-anisotropic", "Anisotropic model", 926, 1042),
    ("11-subsurface-cloth", "Subsurface / Cloth model", 1042, 1197),
    ("12-lighting-units", "Lighting — Units", 1197, 1298),
    ("13-direct-lighting", "Direct lighting", 1298, 1762),
    ("14-ibl", "Image based lights", 1762, 2436),
    ("15-other-lighting", "Other lighting / Volumetrics / AA", 2436, 2673),
    ("16-imaging-camera", "Imaging pipeline — Camera", 2673, 2973),
    ("17-imaging-post", "Imaging pipeline — Post / Path / Validation", 2973, 3329),
    ("18-annex-specular", "Annex — Specular color", 3329, 3460),
    ("19-annex-sampling", "Annex — Importance sampling", 3460, 3657),
    ("20-annex-sh", "Annex — Spherical Harmonics", 3657, 3906),
    ("21-annex-misc", "Annex — Validation / Froxels", 3906, 4228),
    ("22-revisions", "Revisions", 4228, 4251),
    ("23-bibliography", "Bibliography", 4251, 4316),
]

NEWCOMMANDS = r"""$$
\newcommand{NoL}{n \cdot l}
\newcommand{NoV}{n \cdot v}
\newcommand{NoH}{n \cdot h}
\newcommand{VoH}{v \cdot h}
\newcommand{LoH}{l \cdot h}
\newcommand{fNormal}{f_{0}}
\newcommand{fDiffuse}{f_d}
\newcommand{fSpecular}{f_r}
\newcommand{fX}{f_x}
\newcommand{aa}{\alpha^2}
\newcommand{fGrazing}{f_{90}}
\newcommand{schlick}{F_{Schlick}}
\newcommand{nior}{n_{ior}}
\newcommand{Ed}{E_d}
\newcommand{Lt}{L_{\bot}}
\newcommand{Lout}{L_{out}}
\newcommand{cosTheta}{\left< \cos \theta \right> }
$$
"""

NEEDS_MACROS = {
    "03-notation",
    "04-material-standard",
    "05-specular-brdf",
    "06-diffuse-brdf",
    "07-improving-brdfs",
    "08-parameterization",
    "09-clear-coat",
    "10-anisotropic",
    "11-subsurface-cloth",
    "12-lighting-units",
    "13-direct-lighting",
    "14-ibl",
    "15-other-lighting",
    "16-imaging-camera",
    "17-imaging-post",
    "18-annex-specular",
    "19-annex-sampling",
    "20-annex-sh",
    "21-annex-misc",
}


def convert_markdeep(text: str) -> str:
    # Drop HTML meta / style preamble leftovers
    text = re.sub(r"<meta[^>]*>\s*", "", text)
    text = re.sub(r"<style>.*?</style>\s*", "", text, flags=re.S)

    # Image paths
    text = re.sub(r"\(images/", "(/images/filament-md-ja/", text)

    # Code fences: ~~~~...~~~~ → ```glsl
    def code_repl(m: re.Match) -> str:
        body = m.group(1).strip("\n")
        return f"```glsl\n{body}\n```"

    text = re.sub(
        r"~{5,}\n(.*?)~{5,}",
        code_repl,
        text,
        flags=re.S,
    )

    # Listing captions after code
    text = re.sub(
        r"\[Listing \[([^\]]+)\]:\s*([^\]]+)\]",
        r"*リスト [\1]: \2*",
        text,
    )

    # Table captions
    text = re.sub(
        r"\[Table \[([^\]]+)\]:\s*([^\]]+)\]",
        r"*表 [\1]: \2*",
        text,
    )

    # Figure alt text stays; normalize Figure prefix later in translation

    # !!! Note / Warning blocks (Markdeep)
    def note_repl(m: re.Match) -> str:
        kind = m.group(1).strip()
        title = (m.group(2) or "").strip()
        body = m.group(3)
        # Unindent body lines that start with 4 spaces
        lines = []
        for line in body.splitlines():
            if line.startswith("    "):
                lines.append(line[4:])
            else:
                lines.append(line)
        body2 = "\n".join(lines).strip()
        head = f"**{kind}" + (f": {title}" if title else "") + "**"
        return f":::message\n{head}\n\n{body2}\n:::"

    text = re.sub(
        r"!!!\s+(\w+)(?::\s*([^\n]+))?\n((?:[ \t].*\n?)*)",
        note_repl,
        text,
    )

    # Definition lists (term\n:   def) → bold + indent
    def deflist_repl(m: re.Match) -> str:
        term = m.group(1).strip()
        definition = m.group(2)
        lines = []
        for line in definition.splitlines():
            if line.startswith("    "):
                lines.append(line[4:])
            elif line.startswith(":   "):
                lines.append(line[4:])
            else:
                lines.append(line.lstrip(": ").lstrip())
        return f"**{term}**\n\n{chr(10).join(lines).strip()}\n"

    text = re.sub(
        r"^([^\n:]+)\n:   (.+(?:\n(?:    .+|:   .+))*)",
        deflist_repl,
        text,
        flags=re.M,
    )

    # Strip colored metal swatch divs (not useful in Zenn)
    text = re.sub(
        r'<div style="background-color:[^"]+;[^"]*">\s*&nbsp;\s*</div>',
        "",
        text,
    )

    # Footnotes stay as-is (Zenn supports [^id])

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def main() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)
    OUT.mkdir(parents=True, exist_ok=True)

    index = []
    for slug, title, start, end in CHAPTERS:
        chunk = "".join(lines[start - 1 : end - 1])
        chunk = convert_markdeep(chunk)
        # Drop the leading # Title for chapters (front matter title used instead),
        # but keep ## subsections. For Notation keep macros injection.
        body = chunk
        if slug in NEEDS_MACROS and "\\newcommand" not in body:
            # Inject after first heading if present
            parts = body.split("\n", 1)
            if parts and parts[0].startswith("#"):
                body = parts[0] + "\n\n" + NEWCOMMANDS + "\n" + (parts[1] if len(parts) > 1 else "")
            else:
                body = NEWCOMMANDS + "\n" + body

        out_path = OUT / f"{slug}.md"
        out_path.write_text(body, encoding="utf-8")
        index.append(f"- {slug}: {title} ({end - start} lines) → {out_path.name}")
        print(f"wrote {out_path.name} ({len(body)} chars)")

    (OUT / "INDEX.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
