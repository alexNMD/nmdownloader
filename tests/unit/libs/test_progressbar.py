"""Unit tests for libs/progressbar.py module."""

import pytest


from services.download.helpers.progressbar import get_progress_bar, BAR_LENGTH


class TestGetProgressBar:
    """Tests for get_progress_bar function."""

    def test_progress_bar_at_zero_percent(self):
        """Test progress bar at 0% completion."""
        result = get_progress_bar(0, 100)

        assert "0.0%" in result
        assert "⬛" not in result  # No filled blocks at 0%
        assert "⬜" * BAR_LENGTH in result  # All empty blocks

    def test_progress_bar_at_100_percent(self):
        """Test progress bar at 100% completion."""
        result = get_progress_bar(100, 100)

        assert "100.0%" in result
        assert "⬛" * BAR_LENGTH in result  # All filled blocks
        assert "⬜" not in result  # No empty blocks at 100%

    def test_progress_bar_at_50_percent(self):
        """Test progress bar at 50% completion."""
        result = get_progress_bar(50, 100)

        assert "50.0%" in result
        # At 50%, we should have half filled, half empty
        # BAR_LENGTH is 15, so 7 or 8 filled
        filled_count = result.count("⬛")
        empty_count = result.count("⬜")
        assert filled_count > 0
        assert empty_count > 0
        assert filled_count + empty_count == BAR_LENGTH

    def test_progress_bar_returns_string(self):
        """Test that progress bar returns a string."""
        result = get_progress_bar(50, 100)
        assert isinstance(result, str)

    def test_progress_bar_format(self):
        """Test the format of the progress bar string."""
        result = get_progress_bar(50, 100)

        # Should start with carriage return and pipe
        assert result.startswith("\r|")
        # Should contain percentage
        assert "%" in result
        # Should have pipe characters
        assert "|" in result

    def test_progress_bar_with_small_total(self):
        """Test progress bar with small total value."""
        result = get_progress_bar(1, 2)

        assert "50.0%" in result
        assert isinstance(result, str)

    def test_progress_bar_with_large_total(self):
        """Test progress bar with large total value."""
        result = get_progress_bar(500, 1000)

        assert "50.0%" in result

    def test_progress_bar_edge_case_one(self):
        """Test progress bar when progress equals total (both 1)."""
        result = get_progress_bar(1, 1)

        assert "100.0%" in result

    def test_progress_bar_contains_carriage_return(self):
        """Test that progress bar contains carriage return for terminal update."""
        result = get_progress_bar(50, 100)

        assert "\r" in result

    def test_progress_bar_pipe_characters(self):
        """Test that progress bar has pipe characters."""
        result = get_progress_bar(25, 100)

        # Should have exactly 2 pipe characters (start and end)
        assert result.count("|") == 2

    def test_progress_bar_percentage_precision(self):
        """Test percentage precision in progress bar."""
        result = get_progress_bar(1, 3)

        # 1/3 = 33.333...%, should show 33.3%
        assert "33.3%" in result

    def test_progress_bar_blocks_count(self):
        """Test that the number of blocks equals BAR_LENGTH."""
        result = get_progress_bar(75, 100)

        filled_count = result.count("⬛")
        empty_count = result.count("⬜")
        assert filled_count + empty_count == BAR_LENGTH

    def test_progress_bar_zero_total(self):
        """Test progress bar with zero total (edge case)."""
        # This might cause division by zero, but let's see how it's handled
        # The function should handle this gracefully
        with pytest.raises(ZeroDivisionError):
            get_progress_bar(0, 0)
