"""Value-add report for Watershed Connector -- emissions overview across
footprints, same "aggregate raw records into one glance" shape as every
other connector's handlers_reports.py this session.
"""
from __future__ import annotations

from imperal_sdk import ActionResult

import watershed_client as ws
from app import chat
from handlers_connection import resolve_or_error
from schemas import GetEmissionsOverviewParams, EmissionsOverviewReport


@chat.function(
    "get_emissions_overview_report",
    "Value-add report: one-glance emissions overview across the connected Watershed account's footprints -- "
    "total tCO2e and a breakdown by GHG Protocol scope.",
    action_type="read", chain_callable=True, data_model=EmissionsOverviewReport,
)
async def get_emissions_overview_report(ctx, params: GetEmissionsOverviewParams) -> ActionResult:
    """Scan footprints and aggregate emissions by scope."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    data = await ws.request(ctx, conn, "GET", "/v1/footprints", params={"limit": 100}, action="get footprints for emissions overview")
    rows = data.get("footprints", data) if isinstance(data, dict) else data
    rows = rows if isinstance(rows, list) else []
    total = 0.0
    by_scope: dict[str, float] = {}
    for r in rows:
        if not isinstance(r, dict):
            continue
        try:
            tco2e = float(r.get("totalTco2e", r.get("total_tco2e", 0)) or 0)
        except (TypeError, ValueError):
            tco2e = 0.0
        total += tco2e
        scope = r.get("scope") or r.get("ghgScope") or "Unspecified"
        by_scope[scope] = by_scope.get(scope, 0.0) + tco2e
    return ActionResult.success(EmissionsOverviewReport(
        footprint_count=len(rows),
        total_tco2e=round(total, 3),
        by_scope={k: round(v, 3) for k, v in by_scope.items()},
    ), summary="Emissions overview report retrieved.")
