"""Performance report writers.

Strategy-agnostic helpers for emitting performance reports. Currently exposes
:func:`write_performance_pdf` which builds a multi-page PDF from a metrics
dict and a list of pre-rendered matplotlib Figure objects.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Union


def write_performance_pdf(
    pdf_path: Union[str, Path],
    title: str,
    metrics: Dict[str, object],
    figs: Iterable,
    period_text: str = "",
) -> Path:
    """Write a multi-page PDF performance report.

    The first page is a cover page with the bold title, optional period text,
    and a monospace block of metric key/value pairs. Subsequent pages each
    contain one matplotlib Figure.

    Args:
        pdf_path: Output path for the PDF file. Parent directory must exist.
        title: Bold title for the cover page.
        metrics: Mapping of metric name -> value rendered as monospace lines.
        figs: Iterable of matplotlib Figure objects to append, one per page.
        period_text: Optional first line on the cover page describing the
            reporting period (e.g. ``"Period: 2025-01-01 to 2026-01-01"``).

    Returns:
        Path: The path the PDF was written to.
    """

    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    pdf_path = Path(pdf_path)

    with PdfPages(pdf_path) as pdf:
        cover = plt.figure(figsize=(8.5, 11))
        cover.suptitle(title, fontsize=14, fontweight="bold")
        lines = []
        if period_text:
            lines.append(period_text)
            lines.append("")
        lines.extend(f"{k}: {v}" for k, v in metrics.items())
        cover.text(
            0.08,
            0.88,
            "\n".join(lines),
            fontsize=10,
            family="monospace",
            verticalalignment="top",
        )
        pdf.savefig(cover, bbox_inches="tight")
        plt.close(cover)

        for fig in figs:
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    return pdf_path
