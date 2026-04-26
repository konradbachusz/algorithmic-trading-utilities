import sys

sys.path.insert(1, "algorithmic_trading_utilities")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common.report_ops import write_performance_pdf


class TestWritePerformancePdf:

    def test_writes_pdf_with_cover_and_figures(self, tmp_path):
        """End-to-end: cover page + N figure pages produce a non-empty PDF."""
        fig1, ax1 = plt.subplots()
        ax1.plot([1, 2, 3], [1, 4, 9])
        fig2, ax2 = plt.subplots()
        ax2.bar([1, 2, 3], [3, 1, 2])

        out = tmp_path / "report.pdf"
        result = write_performance_pdf(
            pdf_path=out,
            title="Test Strategy - Performance",
            metrics={"sharpe": 1.23, "max_drawdown": -0.15},
            figs=[fig1, fig2],
            period_text="Period: 2025-01-01 to 2026-01-01",
        )

        assert result == out
        assert out.exists()
        assert out.stat().st_size > 0
        # PDF magic header
        with open(out, "rb") as f:
            assert f.read(4) == b"%PDF"

    def test_handles_empty_metrics_and_no_period(self, tmp_path):
        """Cover page renders even with no metrics and no period text."""
        fig, _ = plt.subplots()
        out = tmp_path / "empty.pdf"
        write_performance_pdf(
            pdf_path=out, title="Empty", metrics={}, figs=[fig]
        )
        assert out.exists()
        assert out.stat().st_size > 0

    def test_handles_zero_figures(self, tmp_path):
        """Cover page is still emitted when no figures are supplied."""
        out = tmp_path / "cover_only.pdf"
        write_performance_pdf(
            pdf_path=out,
            title="Cover Only",
            metrics={"win_rate": 0.5},
            figs=[],
        )
        assert out.exists()
        assert out.stat().st_size > 0

    def test_returns_path_as_path_object(self, tmp_path):
        """String path input is normalised to ``pathlib.Path`` on return."""
        fig, _ = plt.subplots()
        out = tmp_path / "str_path.pdf"
        result = write_performance_pdf(
            pdf_path=str(out), title="t", metrics={}, figs=[fig]
        )
        assert hasattr(result, "exists")
        assert str(result) == str(out)
