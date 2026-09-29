"""Tests for the CLI entry point (geo-uri-parse-pure __main__)."""

import subprocess
import sys


class TestCLIHelp:
    def test_help_exits_zero(self):
        result = subprocess.run(
            [sys.executable, "-m", "geo_uri_parse_pure", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "geo-uri-parse-pure" in result.stdout.lower()

    def test_parse_help_exits_zero(self):
        result = subprocess.run(
            [sys.executable, "-m", "geo_uri_parse_pure", "parse", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_validate_help_exits_zero(self):
        result = subprocess.run(
            [sys.executable, "-m", "geo_uri_parse_pure", "validate", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestCLIParse:
    def test_parse_valid_uri(self):
        result = subprocess.run(
            [sys.executable, "-m", "geo_uri_parse_pure", "parse", "geo:51.5,-0.12"],
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, "PYTHONPATH": "src"},
        )
        assert result.returncode == 0
        assert '"lat"' in result.stdout
        assert '"lon"' in result.stdout
        assert '"lat": 51.5' in result.stdout
        assert '"lon": -0.12' in result.stdout

    def test_parse_invalid_uri_exits_2(self):
        result = subprocess.run(
            [sys.executable, "-m", "geo_uri_parse_pure", "parse", "geo:91,0"],
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, "PYTHONPATH": "src"},
        )
        assert result.returncode == 2
        assert "error" in result.stderr.lower()

    def test_parse_empty_exits_2(self):
        result = subprocess.run(
            [sys.executable, "-m", "geo_uri_parse_pure", "parse", ""],
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, "PYTHONPATH": "src"},
        )
        assert result.returncode == 2

    def test_parse_3d_uri(self):
        result = subprocess.run(
            [sys.executable, "-m", "geo_uri_parse_pure", "parse", "geo:37.4,-122.1,10.5"],
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, "PYTHONPATH": "src"},
        )
        assert result.returncode == 0
        assert '"alt": 10.5' in result.stdout


class TestCLIValidate:
    def test_validate_valid_exits_zero(self):
        result = subprocess.run(
            [sys.executable, "-m", "geo_uri_parse_pure", "validate", "geo:0,0"],
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, "PYTHONPATH": "src"},
        )
        assert result.returncode == 0
        assert "valid" in result.stdout

    def test_validate_invalid_exits_2(self):
        result = subprocess.run(
            [sys.executable, "-m", "geo_uri_parse_pure", "validate", "geo:91,0"],
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, "PYTHONPATH": "src"},
        )
        assert result.returncode == 2

    def test_validate_wrong_scheme_exits_2(self):
        result = subprocess.run(
            [sys.executable, "-m", "geo_uri_parse_pure", "validate", "http://example.com"],
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, "PYTHONPATH": "src"},
        )
        assert result.returncode == 2


class TestCLISubcommandRequired:
    def test_no_subcommand_exits_2(self):
        result = subprocess.run(
            [sys.executable, "-m", "geo_uri_parse_pure"],
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, "PYTHONPATH": "src"},
        )
        assert result.returncode == 2
