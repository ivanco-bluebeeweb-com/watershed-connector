"""Extension declaration, secrets, lifecycle hooks.

WHY BYOK, same reasoning as every other connector here -- the user's own
emissions and ESG disclosure data is already tracked inside THEIR OWN
Watershed organization.

WHY A STATIC BEARER API KEY (confirmed against apis.io/apis/watershed/
platform-api and dashboard.watershedclimate.com/settings/api,
2026-08-29): Watershed issues an API key from Organization Settings,
sent as "Authorization: Bearer <key>". No OAuth, no expiry.

WHY WRITES ARE INCLUDED IN V1 (unlike some sibling connectors that defer
writes): activity-data-record ingestion (utility bills, travel, spend-
based estimates) is Watershed's own primary documented API use case, not
an edge-case admin operation -- so create/update activity data records
belongs in v1 per PREPARATION.md.
"""
from __future__ import annotations

from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "watershed-connector",
    version="0.1.0",
    display_name="Watershed",
    icon="icon.svg",
    capabilities=["watershed:read", "watershed:write"],
    description=(
        "Connect your own Watershed climate/ESG account (bring your own API key from Organization Settings) "
        "to read computed emissions footprints, datasets and activity data records, supplier data requests, "
        "and climate reports (GHG Protocol/CDP/TCFD-aligned), plus create and update activity data records "
        "(the core way to feed Watershed new emissions activity data), and a value-add emissions overview report."
    ),
)

chat = ChatExtension(ext)
