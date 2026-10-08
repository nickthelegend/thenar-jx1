"""Small helpers shared by the two LaTeX paper generators (technical paper and business paper)."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from string import Template


class TexTemplate(Template):
    """string.Template with '@@' as the delimiter, so LaTeX's '$' math and braces are left alone."""
    delimiter = "@@"
    idpattern = r"[a-z][a-z0-9_]*"


def esc(s: str) -> str:
    """Escape plain text for LaTeX (only for strings that come from data, not from the hand-written template)."""
    rep = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
           "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", "×": r"$\times$", "≈": r"$\approx$", "·": r"$\cdot$",
           "–": "--", "—": "---", "Ø": r"\O{}", "≥": r"$\geq$", "≤": r"$\leq$", "°": r"$^\circ$", "µ": r"$\mu$",
           "Ω": r"$\Omega$", "₹": "INR~", "→": r"$\rightarrow$"}
    return "".join(rep.get(ch, ch) for ch in s)


def num(x: float, nd: int = 0) -> str:
    return f"{x:,.{nd}f}"


def inr(x: float) -> str:
    """INR with international thousands separators (IEEE style), e.g. INR~30,292."""
    return f"INR~{x:,.0f}"


def lakh(x: float) -> str:
    return f"INR~{x / 1e5:.1f}~lakh" if x < 1e7 else f"INR~{x / 1e7:.2f}~crore"


def crore(x: float) -> str:
    return f"INR~{x / 1e7:,.1f}~crore"


def build_pdf(tex: Path, out_pdf: Path) -> None:
    """Compile with latexmk (pdflatex, two passes for references) and copy the PDF to its final name."""
    if not shutil.which("latexmk"):
        raise SystemExit("latexmk/pdflatex not found: apt-get install texlive-latex-extra texlive-publishers latexmk")
    r = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", tex.name],
                       cwd=tex.parent, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        log = tex.with_suffix(".log")
        tail = log.read_text(errors="ignore")[-4000:] if log.exists() else r.stdout[-4000:]
        raise SystemExit(f"LaTeX failed:\n{tail}")
    shutil.copy(tex.with_suffix(".pdf"), out_pdf)
