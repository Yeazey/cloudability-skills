"""Shared Cloudability V3 API client.

Makes direct HTTP calls to the Cloudability API using httpx,
replacing the pattern where Node.js projects spawned an MCP server subprocess.

Usage:
    from cloudability_dashboards.client import CloudabilityClient, DateHelper

    client = CloudabilityClient.from_env()
    start, end = DateHelper.current_month()
    data = client.cost_report(
        dimensions="vendor,service_name",
        metrics="unblended_cost",
        start_date=start,
        end_date=end,
    )
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

import httpx

BASE_URL = "https://api.cloudability.com"

# Default vendor/service combinations for rightsizing fan-out
_RIGHTSIZING_ENDPOINTS: list[tuple[str, str]] = [
    ("aws", "ec2"),
    ("aws", "ebs"),
    ("aws", "rds"),
    ("azure", "compute"),
    ("gcp", "compute"),
]


class CloudabilityError(Exception):
    """Raised when the Cloudability API returns a non-success response."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class CloudabilityClient:
    """Thin HTTP client for the Cloudability V3 API.

    Authentication is handled via two headers:
      - apptio-opentoken: bearer token for the API
      - apptio-environmentid: target environment/org identifier
    """

    def __init__(self, token: str, environment_id: str, *, timeout: float = 30.0) -> None:
        self._token = token
        self._environment_id = environment_id
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={
                "apptio-opentoken": token,
                "apptio-environmentid": environment_id,
                "Accept": "application/json",
            },
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def from_env(cls) -> "CloudabilityClient":
        """Create a client from environment variables.

        Requires:
          - CLOUDABILITY_OPEN_TOKEN
          - CLOUDABILITY_ENVIRONMENT_ID
        """
        token = os.environ.get("CLOUDABILITY_OPEN_TOKEN", "")
        env_id = os.environ.get("CLOUDABILITY_ENVIRONMENT_ID", "")
        if not token:
            raise EnvironmentError("CLOUDABILITY_OPEN_TOKEN is not set")
        if not env_id:
            raise EnvironmentError("CLOUDABILITY_ENVIRONMENT_ID is not set")
        return cls(token=token, environment_id=env_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if resp.status_code >= 400:
            raise CloudabilityError(resp.status_code, resp.text[:500])

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        resp = self._client.get(path, params=params)
        self._raise_for_status(resp)
        return resp.json()

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def cost_report(
        self,
        dimensions: str,
        metrics: str,
        start_date: str,
        end_date: str,
        *,
        filters: list[str] | None = None,
        sort: str | None = None,
        limit: int = 1000,
        view_id: str = "0",
    ) -> dict:
        """Run a cost report.

        GET /v3/reporting/cost/run

        Args:
            dimensions: Comma-separated dimension names (e.g. "vendor,service_name").
            metrics: Comma-separated metric names (e.g. "unblended_cost").
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            filters: Filter expressions (e.g. ["vendor==Amazon", "region=@us-"]).
            sort: Sort string (e.g. "unblended_costDESC").
            limit: Maximum rows to return.
            view_id: View ID to scope the report ("0" for unrestricted).
        """
        params: dict[str, Any] = {
            "start_date": start_date,
            "end_date": end_date,
            "dimensions": dimensions,
            "metrics": metrics,
            "limit": limit,
            "view_id": view_id,
        }
        if filters:
            params["filters"] = filters
        if sort:
            params["sort"] = sort
        return self._get("/v3/reporting/cost/run", params=params)

    def usage_report(
        self,
        dimensions: str,
        metrics: str,
        start_date: str,
        end_date: str,
        *,
        filters: list[str] | None = None,
        sort: str | None = None,
        limit: int = 1000,
    ) -> dict:
        """Run a usage report.

        GET /v3/reporting/usage/run

        Args:
            dimensions: Comma-separated dimension names.
            metrics: Comma-separated metric names.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            filters: Filter expressions.
            sort: Sort string.
            limit: Maximum rows to return.
        """
        params: dict[str, Any] = {
            "start_date": start_date,
            "end_date": end_date,
            "dimensions": dimensions,
            "metrics": metrics,
            "limit": limit,
        }
        if filters:
            params["filters"] = filters
        if sort:
            params["sort"] = sort
        return self._get("/v3/reporting/usage/run", params=params)

    # ------------------------------------------------------------------
    # Kubernetes / Kubecost
    # ------------------------------------------------------------------

    def kubecost_allocation(
        self,
        aggregate: str,
        window: str,
        *,
        accumulate: bool = True,
        filters: str | None = None,
    ) -> dict:
        """Get Kubecost allocation data.

        GET /v3/kubecost/model/allocation

        Args:
            aggregate: Grouping dimensions (e.g. "cluster,namespace").
            window: Time window (e.g. "7d", "30d", "lastmonth").
            accumulate: Whether to accumulate over the window.
            filters: Optional Kubecost filter string.
        """
        params: dict[str, Any] = {
            "window": window,
            "aggregate": aggregate,
            "accumulate": "true" if accumulate else "false",
        }
        if filters:
            params["filter"] = filters
        return self._get("/v3/kubecost/model/allocation", params=params)

    # ------------------------------------------------------------------
    # Rightsizing
    # ------------------------------------------------------------------

    def rightsizing(
        self,
        vendor: str | None = None,
        service: str | None = None,
        *,
        limit: int = 50,
        sort: str = "-recommendations.savings",
    ) -> dict:
        """Get rightsizing recommendations.

        GET /v3/rightsizing/{vendor}/{service}

        If vendor is None, fans out across all default endpoints and
        merges results into a single response dict.

        Args:
            vendor: Cloud vendor (aws, azure, gcp). None for fan-out.
            service: Service within vendor (ec2, ebs, rds, compute).
            limit: Max results per endpoint.
            sort: Sort expression.
        """
        params: dict[str, Any] = {"limit": limit, "sort": sort}

        if vendor is not None:
            path = f"/v3/rightsizing/{vendor}"
            if service:
                path = f"{path}/{service}"
            return self._get(path, params=params)

        # Fan out across default endpoints
        combined: dict[str, Any] = {"results": [], "endpoints_queried": []}
        for v, s in _RIGHTSIZING_ENDPOINTS:
            path = f"/v3/rightsizing/{v}/{s}"
            try:
                data = self._get(path, params=params)
                combined["endpoints_queried"].append(f"{v}/{s}")
                if isinstance(data, dict) and "results" in data:
                    combined["results"].extend(data["results"])
                elif isinstance(data, list):
                    combined["results"].extend(data)
                else:
                    combined["results"].append(data)
            except CloudabilityError:
                # Some endpoints may not be available for all orgs
                continue
        return combined

    # ------------------------------------------------------------------
    # Anomalies
    # ------------------------------------------------------------------

    def anomalies(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 20,
    ) -> dict:
        """List detected cost anomalies.

        GET /v3/anomalies

        Args:
            start_date: Filter anomalies from this date (YYYY-MM-DD).
            end_date: Filter anomalies until this date (YYYY-MM-DD).
            limit: Max results.
        """
        params: dict[str, Any] = {"limit": limit}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._get("/v3/anomalies", params=params)

    # ------------------------------------------------------------------
    # Budgets
    # ------------------------------------------------------------------

    def budgets(self) -> dict:
        """List all budgets.

        GET /v3/budgets
        """
        return self._get("/v3/budgets")

    # ------------------------------------------------------------------
    # Forecast
    # ------------------------------------------------------------------

    def forecast(self, *, view_id: str | None = None) -> dict:
        """Get spend forecast.

        GET /v3/forecast

        Args:
            view_id: Optional view ID to scope the forecast.
        """
        params: dict[str, Any] = {}
        if view_id:
            params["viewId"] = view_id
        return self._get("/v3/forecast", params=params)

    # ------------------------------------------------------------------
    # Views
    # ------------------------------------------------------------------

    def views(self) -> dict:
        """List all accessible views.

        GET /v3/views
        """
        return self._get("/v3/views")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> "CloudabilityClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


# ======================================================================
# Date Helper
# ======================================================================


class DateHelper:
    """Utility for generating common date ranges as (start, end) string tuples.

    All dates are returned in YYYY-MM-DD format.
    """

    @staticmethod
    def current_month() -> tuple[str, str]:
        """Return (first day of current month, today)."""
        today = date.today()
        start = today.replace(day=1)
        return start.isoformat(), today.isoformat()

    @staticmethod
    def previous_month() -> tuple[str, str]:
        """Return (first day of previous month, last day of previous month)."""
        today = date.today()
        first_of_current = today.replace(day=1)
        last_of_prev = first_of_current - timedelta(days=1)
        first_of_prev = last_of_prev.replace(day=1)
        return first_of_prev.isoformat(), last_of_prev.isoformat()

    @staticmethod
    def last_n_days(n: int) -> tuple[str, str]:
        """Return (n days ago, yesterday).

        Args:
            n: Number of days to look back.
        """
        today = date.today()
        end = today - timedelta(days=1)
        start = today - timedelta(days=n)
        return start.isoformat(), end.isoformat()

    @staticmethod
    def year_to_date() -> tuple[str, str]:
        """Return (Jan 1 of current year, today)."""
        today = date.today()
        start = date(today.year, 1, 1)
        return start.isoformat(), today.isoformat()
