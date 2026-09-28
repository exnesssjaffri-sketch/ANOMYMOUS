"""Analytics tracking for provider usage.

Tracks:
- Request counts per provider/model
- Error rates and categories
- Latency distributions
- Token usage statistics

Does NOT persist:
- API keys or secrets
- Full request payloads
- Sensitive user data
"""

import time
import json
import os
from typing import Dict, Any, List, Optional
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class RequestMetric:
    """Metric for a single request."""
    provider: str
    model: str
    status: str  # "success" or "error"
    error_type: Optional[str] = None
    duration: float = 0.0
    estimated_tokens: int = 0
    attempt: int = 1
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "status": self.status,
            "error_type": self.error_type,
            "duration": self.duration,
            "estimated_tokens": self.estimated_tokens,
            "attempt": self.attempt,
            "timestamp": self.timestamp,
        }


class AnalyticsTracker:
    """Tracks analytics for LLM requests."""

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._metrics: List[RequestMetric] = []
        self._provider_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_duration": 0.0,
            "total_tokens": 0,
            "error_types": defaultdict(int),
        })

    def record(self, metric: RequestMetric):
        """Record a request metric."""
        self._metrics.append(metric)
        if len(self._metrics) > self.max_history:
            self._metrics = self._metrics[-self.max_history:]

        stats = self._provider_stats[metric.provider]
        stats["total_requests"] += 1
        if metric.status == "success":
            stats["successful_requests"] += 1
        else:
            stats["failed_requests"] += 1
            if metric.error_type:
                stats["error_types"][metric.error_type] += 1
        stats["total_duration"] += metric.duration
        stats["total_tokens"] += metric.estimated_tokens

    def get_summary(self) -> Dict[str, Any]:
        """Get analytics summary."""
        total_requests = len(self._metrics)
        successful = sum(1 for m in self._metrics if m.status == "success")
        failed = total_requests - successful

        return {
            "total_requests": total_requests,
            "successful_requests": successful,
            "failed_requests": failed,
            "success_rate": successful / max(1, total_requests),
            "providers": dict(self._provider_stats),
        }

    def get_provider_stats(self, provider: str) -> Dict[str, Any]:
        """Get stats for a specific provider."""
        return dict(self._provider_stats.get(provider, {}))

    def get_recent_metrics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent metrics."""
        return [m.to_dict() for m in self._metrics[-limit:]]

    def get_error_breakdown(self) -> Dict[str, int]:
        """Get error breakdown by type."""
        breakdown = defaultdict(int)
        for m in self._metrics:
            if m.error_type:
                breakdown[m.error_type] += 1
        return dict(breakdown)

    def get_latency_stats(self) -> Dict[str, Any]:
        """Get latency statistics."""
        durations = [m.duration for m in self._metrics if m.duration > 0]
        if not durations:
            return {"count": 0}
        durations.sort()
        return {
            "count": len(durations),
            "min": durations[0],
            "max": durations[-1],
            "avg": sum(durations) / len(durations),
            "median": durations[len(durations) // 2],
            "p95": durations[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0],
        }

    def clear(self):
        """Clear all metrics."""
        self._metrics = []
        self._provider_stats = defaultdict(lambda: {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_duration": 0.0,
            "total_tokens": 0,
            "error_types": defaultdict(int),
        })


# Global analytics tracker instance
analytics = AnalyticsTracker()