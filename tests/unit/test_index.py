"""Unit tests for the Dedeman sinapsi jobs API parser."""

import json

from scraper import index

SAMPLE_PAYLOAD = {
    "d": {
        "JobAnnounces": [
            {"Id": "abc-123", "Function": "Consultant vanzari", "City": "Arad",
             "WorkingPoint": "Arad 2 - Micalaca"},
            {"Id": "def-456", "Function": "Lucrator depozit", "City": "Bacau",
             "WorkingPoint": "Bacau 1 - Republicii"},
        ]
    }
}


def test_build_listing_url():
    url = index.build_listing_url()
    assert url.startswith("https://")
    assert "/api/sinapsi/jobs" in url


def test_build_job_url():
    assert index.build_job_url("abc-123", "Consultant vanzari") == (
        "https://recrutare.dedeman.ro/detalii-post"
        "?job=Consultant%20vanzari&id=abc-123"
    )


def test_build_job_url_preserves_job_id():
    assert index.build_job_url("def-456", "Lucrator depozit").endswith("&id=def-456")


def test_extract_location_takes_first_token():
    assert index.extract_location("Bucuresti, Bucuresti, Romania") == ["Bucuresti"]
    assert index.extract_location("Cluj-Napoca") == ["Cluj-Napoca"]


def test_extract_location_single_token():
    assert index.extract_location("Romania") == ["România"]


def test_extract_location_missing():
    assert index.extract_location(None) == []
    assert index.extract_location("") == []


def test_parse_api_jobs():
    jobs = index.parse_api_jobs(SAMPLE_PAYLOAD)
    assert len(jobs) == 2
    assert jobs[0]["title"] == "Consultant vanzari"
    assert jobs[0]["url"] == (
        "https://recrutare.dedeman.ro/detalii-post"
        "?job=Consultant%20vanzari&id=abc-123"
    )
    assert jobs[0]["location"] == ["Arad"]
    assert jobs[1]["location"] == ["Bacau"]


def test_parse_api_jobs_skips_without_title():
    payload = {"d": {"JobAnnounces": [
        {"Id": "x", "Function": "", "City": "Arad"},
        {"Id": "y", "Function": "Agent securitate", "City": "Arad"},
    ]}}
    jobs = index.parse_api_jobs(payload)
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Agent securitate"


def test_parse_api_jobs_deduplicates():
    payload = {"d": {"JobAnnounces":
                     SAMPLE_PAYLOAD["d"]["JobAnnounces"] * 2}}
    jobs = index.parse_api_jobs(payload)
    assert len(jobs) == 2


def test_parse_api_jobs_empty():
    assert index.parse_api_jobs({"d": {"JobAnnounces": []}}) == []
    assert index.parse_api_jobs(None) == []


def test_map_to_job_model_adds_company_and_status():
    raw = {"url": "https://recrutare.dedeman.ro/detalii-post?job=X&id=abc-123",
           "title": "Consultant vanzari", "location": ["Arad"]}
    index.COMPANY_NAME = "DEDEMAN S.R.L."
    job = index.map_to_job_model(raw, "2816464")
    assert job["company"] == "DEDEMAN S.R.L."
    assert job["cif"] == "2816464"
    assert job["status"] == "scraped"
    assert job["location"] == ["Arad"]


def test_transform_jobs_for_solr_keeps_required_fields():
    jobs = [{"url": "https://x/job", "title": "Test Job", "location": ["Cluj-Napoca"],
             "company": "DEDEMAN S.R.L.", "cif": "2816464"}]
    transformed = index.transform_jobs_for_solr({"company": "DEDEMAN S.R.L.", "jobs": jobs})
    assert len(transformed["jobs"]) == 1
    t = transformed["jobs"][0]
    assert t["url"]
    assert t["title"]
    assert t["location"] == ["Cluj-Napoca"]
    assert t["company"] == "DEDEMAN S.R.L."


def test_transform_keeps_new_dedeman_cities():
    jobs = [{"url": "https://x/1", "title": "Agent", "location": ["Bârlad"]},
            {"url": "https://x/2", "title": "Agent", "location": ["Sfântu Gheorghe"]},
            {"url": "https://x/3", "title": "Agent", "location": ["Câmpulung Moldovenesc"]}]
    transformed = index.transform_jobs_for_solr({"company": "DEDEMAN S.R.L.", "jobs": jobs})
    assert [j["location"] for j in transformed["jobs"]] == [
        ["Bârlad"], ["Sfântu Gheorghe"], ["Câmpulung Moldovenesc"]]


def test_transform_workmode_normalized():
    jobs = [{"url": "https://x/1", "title": "Dev", "location": ["Cluj-Napoca"], "workmode": "Remote"}]
    transformed = index.transform_jobs_for_solr({"company": "DEDEMAN S.R.L.", "jobs": jobs})
    assert transformed["jobs"][0]["workmode"] == "remote"


def test_transform_missing_workmode_dropped():
    jobs = [{"url": "https://x/1", "title": "Dev", "location": ["Cluj-Napoca"]}]
    transformed = index.transform_jobs_for_solr({"company": "DEDEMAN S.R.L.", "jobs": jobs})
    assert "workmode" not in transformed["jobs"][0]


def test_generate_jobs_markdown(tmp_path, company_config):
    jobs = [{"url": "https://x/job", "title": "Consultant vanzari",
             "company": "DEDEMAN S.R.L.", "cif": "2816464",
             "location": ["Arad"], "workmode": "on-site"}]
    md = index.generate_jobs_markdown(company_config, jobs)
    assert f"# {company_config['company']}" in md
    assert "## Jobs (1)" in md
    assert "Consultant vanzari" in md
    assert "](https://x/job)" in md


def test_generate_jobs_markdown_empty():
    md = index.generate_jobs_markdown({}, [])
    assert "## Jobs (0)" in md
    assert "_No jobs found._" in md


def test_main_dry_run_writes_summary(tmp_path, monkeypatch):
    fake_jobs = [{"url": f"https://x/{i}", "title": f"Job {i}", "location": ["Cluj-Napoca"]}
                 for i in range(3)]
    monkeypatch.setattr(index, "parse_api_jobs", lambda payload: fake_jobs)
    monkeypatch.setattr(index, "fetch_listing", lambda: {"d": {"JobAnnounces": []}})
    monkeypatch.setattr(index, "query_solr", lambda cif: {"numFound": 1, "docs": []})
    monkeypatch.setattr(index, "upsert_jobs", lambda jobs: None)
    monkeypatch.setattr(index, "delete_job_by_url", lambda url: None)
    monkeypatch.setattr(index, "upsert_company", lambda cfg: None)
    monkeypatch.setattr(index, "validate_and_get_company", lambda: {
        "company": "DEDEMAN S.R.L.", "cif": "2816464", "status": "active",
        "address": "BACAU"})
    monkeypatch.setattr(index, "search_anofm", lambda cif: [])

    index.main(root=tmp_path)
    out = tmp_path / "scraper" / "jobs.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert len(data["jobs"]) >= 3
