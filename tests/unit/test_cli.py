"""Unit tests for Baby LLM CLI argument parser and commands."""

import argparse
from unittest.mock import patch
import pytest

from baby_llm.cli import main


def test_cli_subparser_ui_when_running():
    """Verify `baby-llm ui` opens browser when server already active."""
    with patch("sys.argv", ["baby-llm", "ui", "--port", "21225"]):
        with patch("socket.create_connection"):
            with patch("webbrowser.open") as mock_open:
                main()
                mock_open.assert_called_once_with("http://127.0.0.1:21225/")


def test_cli_subparser_ui_when_not_running():
    """Verify `baby-llm ui` starts server when not active."""
    with patch("sys.argv", ["baby-llm", "ui", "--port", "21225"]):
        with patch("socket.create_connection", side_effect=OSError("connection refused")):
            with patch("uvicorn.run") as mock_uvicorn, patch("threading.Thread") as mock_thread:
                main()
                mock_uvicorn.assert_called_once()
                mock_thread.assert_called_once()


def test_cli_subparser_memories():
    """Verify `baby-llm memories` runs without error."""
    with patch("sys.argv", ["baby-llm", "memories"]):
        with patch("baby_llm.cli.list_memories") as mock_list:
            main()
            mock_list.assert_called_once()


def test_cli_subparser_dream():
    """Verify `baby-llm dream` runs consolidation cycle."""
    with patch("sys.argv", ["baby-llm", "dream"]):
        with patch("baby_llm.dream.worker.dream_worker.run_consolidation_cycle") as mock_dream:
            mock_dream.return_value = {"turns_processed": 0}
            main()
            mock_dream.assert_called_once()
