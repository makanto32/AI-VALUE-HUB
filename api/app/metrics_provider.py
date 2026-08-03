from __future__ import annotations

import json
import os
from pathlib import Path

from .analytics_service import AnalyticsService
from .models import ExecutiveDashboardMetrics
from .store import idea_store


class DashboardMetricsProvider:
    """Abstract provider for executive dashboard metrics."""

    def get_executive_dashboard(self, tenant_id: str, period: str) -> ExecutiveDashboardMetrics:
        raise NotImplementedError


class LocalDashboardMetricsProvider(DashboardMetricsProvider):
    """Build metrics directly from transactional records (SQLite store)."""

    def __init__(self, annual_ai_investment: float = 100_000) -> None:
        self.annual_ai_investment = annual_ai_investment

    def get_executive_dashboard(self, tenant_id: str, period: str) -> ExecutiveDashboardMetrics:
        ideas = idea_store.list_by_tenant(tenant_id)
        analytics = AnalyticsService(all_ideas=ideas)
        return analytics.calculate_executive_dashboard(
            tenant_id=tenant_id,
            annual_ai_investment=self.annual_ai_investment,
            period=period,
        )


class SemanticFileDashboardMetricsProvider(DashboardMetricsProvider):
    """Read metrics from a Gold artifact generated for Fabric semantic model ingestion."""

    def __init__(self, semantic_path: Path) -> None:
        self.semantic_path = semantic_path

    def get_executive_dashboard(self, tenant_id: str, period: str) -> ExecutiveDashboardMetrics:
        if not self.semantic_path.exists():
            raise FileNotFoundError(f"Semantic metrics file not found: {self.semantic_path}")

        payload = json.loads(self.semantic_path.read_text(encoding="utf-8"))
        # Allow one file per tenant or a full map of tenants.
        if "tenant_id" in payload:
            selected = payload
        else:
            selected = payload.get(tenant_id)
            if selected is None:
                raise KeyError(f"Tenant '{tenant_id}' not found in semantic metrics payload")

        selected["period"] = period
        return ExecutiveDashboardMetrics.model_validate(selected)


def build_dashboard_metrics_provider() -> DashboardMetricsProvider:
    source = os.getenv("AIHUB_DASHBOARD_METRICS_SOURCE", "local").strip().lower()
    semantic_file = Path(
        os.getenv(
            "AIHUB_SEMANTIC_METRICS_FILE",
            str(Path(__file__).resolve().parents[2] / "data" / "fabric" / "gold" / "executive_dashboard_current.json"),
        )
    )

    if source == "semantic":
        return SemanticFileDashboardMetricsProvider(semantic_path=semantic_file)

    return LocalDashboardMetricsProvider()
