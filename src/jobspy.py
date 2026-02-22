import pandas as pd
import time

def scrape_jobs(site_name, search_term, location, results_wanted=5, hours_old=1, country_indeed=None):
    """Minimal local stub for `scrape_jobs` used for testing.

    Returns a pandas DataFrame with columns: job_url, company, title, site_name.
    Produces deterministic-ish dummy results based on the search_term.
    """
    rows = []
    ts = int(time.time())
    # Normalize site_name to a string for the stub
    site_label = site_name[0] if isinstance(site_name, (list, tuple)) and site_name else str(site_name)
    for i in range(max(0, int(results_wanted))):
        jid = f"{abs(hash((search_term, site_label, i, ts))) % 100000}"
        rows.append({
            "job_url": f"https://example.com/jobs/{jid}",
            "company": f"ExampleCo-{i%5}",
            "title": f"Sample {search_term} - {i}",
            "site_name": site_label
        })
    return pd.DataFrame(rows)

__all__ = ["scrape_jobs"]
