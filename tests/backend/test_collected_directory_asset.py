"""Integrity checks for the supplemental directory loaded by the React application."""
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "src" / "frontend" / "public" / "collected-centres.json.gz"


def load_records():
    with gzip.open(ASSET, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def test_collected_asset_has_220_hsamb_records_and_13_leads():
    rows = load_records()
    assert len(rows) == 233
    assert sum(row["dataLayer"] == "official_inventory" for row in rows) == 220
    assert sum(row["dataLayer"] == "discovery_lead" for row in rows) == 13
    assert len({row["id"] for row in rows}) == 233


def test_hsamb_records_keep_source_and_non_operational_caveat():
    rows = [row for row in load_records() if row["dataLayer"] == "official_inventory"]
    assert all(row["state"] == "Haryana" for row in rows)
    assert all(row["sourceUrl"].startswith("https://hsamb.org.in/") for row in rows)
    assert all("current-season activation" in row["verificationNote"].lower() for row in rows)


def test_discovery_leads_are_not_misclassified_as_confirmed_centres():
    rows = [row for row in load_records() if row["dataLayer"] == "discovery_lead"]
    assert all(row["recordStatus"] == "discovery-lead" for row in rows)
    assert all("unverified" in row["verificationNote"].lower() for row in rows)
    assert all(row["displayName"].endswith("— unverified lead") for row in rows)


def test_missing_lead_source_urls_are_not_fabricated():
    rows = [row for row in load_records() if row["dataLayer"] == "discovery_lead"]
    assert any(not row.get("sourceUrl") for row in rows)
