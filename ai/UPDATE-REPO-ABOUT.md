# Update Repo About

Keep the GitHub repository metadata up to date.

## Description

Scraper automat pentru locurile de muncă DEDEMAN S.R.L. (CIF: 2816464) — extrage
din recrutare.dedeman.ro și publică pe peviitor.ro

## Homepage

https://elenab01234.github.io/DEDEMAN-PYTHON-SCRAPER/

## Topics (exactly 2, per TOPICS.md)

- job-seeker-ro-spider
- peviitor-ro

## Workflow file

`.github/workflows/job-seeker-ro-spider.yml`

## How to apply

```bash
gh repo edit elenab01234/DEDEMAN-PYTHON-SCRAPER \
  --description "Scraper automat pentru locurile de muncă DEDEMAN S.R.L. (CIF: 2816464) — extrage din recrutare.dedeman.ro și publică pe peviitor.ro" \
  --homepage "https://elenab01234.github.io/DEDEMAN-PYTHON-SCRAPER/"
```

## GitHub Pages

- Source: branch `main`, path `/docs` (static site, no Pages workflow needed).
- Builds automatically on every push to `main` (`build_type: legacy`).
- Site: https://elenab01234.github.io/DEDEMAN-PYTHON-SCRAPER/
- `docs/jobs.md` is regenerated on each scrape and served on the site.
- Homepage on the repo points to the Pages URL (same as the template).
