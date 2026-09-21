"""End-to-end test: scrape the real Dedeman careers board.

The Dedeman board (recrutare.dedeman.ro) exposes its postings through the
sinapsi JSON API. Skips (rather than fails) when the board is unreachable, so
that CI does not break on transient network issues.
"""

import socket

import pytest

from scraper import index

# A sane lower bound protects against board restructures without being brittle.
EXPECTED_MIN_JOBS = 1


def _board_reachable():
    try:
        with socket.create_connection(("recrutare.dedeman.ro", 443), timeout=5):
            return True
    except OSError:
        return False


def test_scrape_real_board():
    if not _board_reachable():
        pytest.skip("recrutare.dedeman.ro not reachable")
    payload = index.fetch_listing()
    jobs = index.parse_api_jobs(payload)
    assert len(jobs) >= EXPECTED_MIN_JOBS, f"Expected >= {EXPECTED_MIN_JOBS} jobs, got {len(jobs)}"
    for job in jobs:
        assert job["url"].startswith("https://recrutare.dedeman.ro/detalii-post?")
        assert job["title"]
    urls = {j["url"] for j in jobs}
    assert len(urls) == len(jobs), "duplicate job URLs found"
