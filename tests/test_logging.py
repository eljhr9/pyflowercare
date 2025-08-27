import logging
import sys
from unittest.mock import Mock, patch

import pytest

from pyflowercare.logging import disable_bleak_logs, get_logger, setup_logging


class TestLogging:
    """Test logging functionality."""

    def test_setup_logging_default(self):
        """Test default logging setup."""
        with patch("logging.basicConfig") as mock_basic_config:
            setup_logging()

            mock_basic_config.assert_called_once()
            call_args = mock_basic_config.call_args[1]

            assert call_args["level"] == logging.INFO
            assert call_args["stream"] == sys.stdout
            assert "asctime" in call_args["format"]
            assert "name" in call_args["format"]
            assert "levelname" in call_args["format"]
            assert "message" in call_args["format"]

    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level."""
        with patch("logging.basicConfig") as mock_basic_config:
            setup_logging("DEBUG")

            call_args = mock_basic_config.call_args[1]
            assert call_args["level"] == logging.DEBUG

    def test_setup_logging_custom_level_lowercase(self):
        """Test logging setup with lowercase level."""
        with patch("logging.basicConfig") as mock_basic_config:
            setup_logging("debug")

            call_args = mock_basic_config.call_args[1]
            assert call_args["level"] == logging.DEBUG

    def test_setup_logging_custom_format(self):
        """Test logging setup with custom format."""
        custom_format = "%(name)s: %(message)s"

        with patch("logging.basicConfig") as mock_basic_config:
            setup_logging(format_string=custom_format)

            call_args = mock_basic_config.call_args[1]
            assert call_args["format"] == custom_format

    def test_setup_logging_no_timestamp(self):
        """Test logging setup without timestamp."""
        with patch("logging.basicConfig") as mock_basic_config:
            setup_logging(include_timestamp=False)

            call_args = mock_basic_config.call_args[1]
            assert "asctime" not in call_args["format"]
            assert "name" in call_args["format"]
            assert "levelname" in call_args["format"]
            assert "message" in call_args["format"]

    def test_setup_logging_all_parameters(self):
        """Test logging setup with all parameters."""
        custom_format = "CUSTOM: %(message)s"

        with patch("logging.basicConfig") as mock_basic_config:
            setup_logging(level="WARNING", format_string=custom_format, include_timestamp=False)

            call_args = mock_basic_config.call_args[1]
            assert call_args["level"] == logging.WARNING
            assert call_args["format"] == custom_format
            assert call_args["stream"] == sys.stdout

    def test_get_logger(self):
        """Test getting a logger."""
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            result = get_logger("test")

            assert result == mock_logger
            mock_get_logger.assert_called_once_with("flowercare.test")

    def test_get_logger_different_names(self):
        """Test getting loggers with different names."""
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # Test various logger names
            names = ["device", "scanner", "models"]
            for name in names:
                get_logger(name)
                mock_get_logger.assert_called_with(f"flowercare.{name}")

    def test_disable_bleak_logs(self):
        """Test disabling Bleak logs."""
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            disable_bleak_logs()

            # Should be called twice - once for "bleak" and once for "bleak.backends"
            assert mock_get_logger.call_count == 2
            mock_get_logger.assert_any_call("bleak")
            mock_get_logger.assert_any_call("bleak.backends")

            # Should set log level to WARNING for both loggers
            assert mock_logger.setLevel.call_count == 2
            mock_logger.setLevel.assert_called_with(logging.WARNING)

    def test_integration_setup_and_get_logger(self):
        """Test integration between setup_logging and get_logger."""
        # This is more of an integration test to ensure they work together
        logger_name = "test_integration"

        # Setup logging (this should work without raising exceptions)
        setup_logging("INFO")

        # Get a logger (this should also work)
        logger = get_logger(logger_name)

        # Verify we got a logger
        assert isinstance(logger, logging.Logger)
        assert logger.name == f"flowercare.{logger_name}"

    def test_logging_levels(self):
        """Test different logging levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            with patch("logging.basicConfig") as mock_basic_config:
                setup_logging(level)

                call_args = mock_basic_config.call_args[1]
                expected_level = getattr(logging, level)
                assert call_args["level"] == expected_level
