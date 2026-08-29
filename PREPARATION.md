# Watershed Connector -- Preparation (v0.1)

## API surface
Watershed Platform API (enterprise climate/emissions/ESG reporting) --
REST/JSON, resources: footprints, emissions/activity data records,
datasets, supplier data requests, reports (GHG Protocol/CDP/TCFD-aligned).
Confirmed via apis.io/apis/watershed/platform-api and Watershed's own
dashboard docs (dashboard.watershedclimate.com/settings/api, 2026-08-29).

## Auth model
Static **Bearer API key** -- generated and managed in the Watershed
dashboard under Organization Settings, sent as
`Authorization: Bearer <API_KEY>`. No OAuth, no expiry -- same
simplicity class as Vantage/CloudHealth/Expensify/Brex.

## Why BYOK
Same reasoning as every other connector here -- the user's own emissions
and ESG disclosure data is already tracked inside THEIR OWN Watershed
organization. The API key is generated per Watershed organization from
their own dashboard.

## Scope for v1
Read-heavy: footprints (computed emissions results), datasets/activity
data records, supplier data requests, reports. Write: create/update
activity data records (the core "ingest emissions activity data"
operation Watershed's API is built around -- e.g. utility bills, travel
records, spend-based estimates) -- this is Watershed's primary intended
write use case per its own docs, not an edge case, so it is included in
v1 unlike some other categories' write-deferral pattern.

## Rate limits / known constraints
Standard REST pagination. Public developer docs are limited (much of
Watershed's integration surface is partner-mediated), so this connector
targets the documented dataset/activity-data-record ingestion pattern
and the well-known GET footprint/report retrieval endpoints; more
specialized workflows (supplier engagement campaigns) are read-only in
v1 and can be expanded later once broader docs are available.
