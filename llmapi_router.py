#!/usr/bin/env python3
"""
LLMAPI Router - Multi-provider routing with failover and health tracking.
"""
import time
import random
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from transport import Transport
from llmapi_adapter import LLMAPIAdapter
from error_classifier import ErrorClassifier
from token_estimator import estimate_payload_tokens, reduce_payload_tokens
from providers.health import HealthStatePersistence
from providers.analytics import analytics, RequestMetric


class RouteStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    QUARANTINED = "quarantined"
    UNAVAILABLE = "unavailable"


@dataclass
class ProviderRoute:
    provider: str
    model: str
    transport: Transport
    max_tokens: int = 7000
    priority: int = 0
    weight: float = 1.0
    status: RouteStatus = RouteStatus.HEALTHY
    consecutive_failures: int = 0
    last_success: float = 0
    last_failure: float = 0
    last_error_category: Optional[str] = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

    def __post_init__(self):
        self.adapter = LLMAPIAdapter(self.provider, self.model, self.transport, max_tokens=self.max_tokens)

    def is_healthy(self) -> bool:
        if self.status == RouteStatus.QUARANTINED:
            if time.time() - self.last_failure > 300:
                self.status = RouteStatus.DEGRADED
                return True
            return False
        if self.status == RouteStatus.UNAVAILABLE:
            return False
        return True

    def record_success(self):
        self.consecutive_failures = 0
        self.last_success = time.time()
        self.status = RouteStatus.HEALTHY
        self.total_requests += 1
        self.successful_requests += 1
        # Persist to health state if router is available
        if hasattr(self, '_router') and self._router:
            self._router.health_state.record_success(self.provider, self.model)

    def record_failure(self, error_category: str):
        self.consecutive_failures += 1
        self.last_failure = time.time()
        self.last_error_category = error_category
        self.total_requests += 1
        self.failed_requests += 1
        if ErrorClassifier.should_quarantine_provider(error_category):
            self.status = RouteStatus.QUARANTINED
        elif error_category in (ErrorClassifier.RATE_LIMIT, ErrorClassifier.UNAVAILABLE):
            if self.consecutive_failures >= 3:
                self.status = RouteStatus.DEGRADED
        elif error_category == ErrorClassifier.ALL_MODELS_RATE_LIMITED:
            self.status = RouteStatus.QUARANTINED
        # Persist to health state if router is available
        if hasattr(self, '_router') and self._router:
            self._router.health_state.record_failure(self.provider, self.model, error_category)


class LLMAPIRouter:
    def __init__(
        self,
        routes: List[ProviderRoute],
        max_candidates: int = 5,
        health_state_file: str = None,
    ):
        self.routes = routes
        self.max_candidates = max_candidates
        self._rng = random.Random()
        self.routes.sort(key=lambda r: (-r.priority, r.provider, r.model))
        # Initialize health persistence
        self.health_state = HealthStatePersistence(health_state_file)
        # Sync route health from persisted state
        self._sync_route_health()
        # Set router reference on routes for health persistence
        for route in self.routes:
            route._router = self

    def _sync_route_health(self):
        """Sync route health from persisted state."""
        for route in self.routes:
            state = self.health_state.get_state(route.provider, route.model)
            if state:
                # Only sync health status, not counters (counters start fresh per router instance)
                route.consecutive_failures = state.consecutive_failures
                route.last_success = state.last_success
                route.last_failure = state.last_failure
                route.last_error_category = state.last_error_category
                if state.consecutive_failures > 0:
                    if ErrorClassifier.should_quarantine_provider(state.last_error_category or ErrorClassifier.UNKNOWN):
                        route.status = RouteStatus.QUARANTINED
                    elif state.consecutive_failures >= 3:
                        route.status = RouteStatus.DEGRADED

    def _persist_route_health(self, route: ProviderRoute):
        """Persist route health state."""
        self.health_state.record_success(route.provider, route.model) if route.consecutive_failures == 0 else None
        if route.consecutive_failures > 0:
            self.health_state.record_failure(
                route.provider, route.model,
                route.last_error_category or ErrorClassifier.UNKNOWN
            )

    def get_eligible_routes(self, payload: Dict[str, Any]) -> List[ProviderRoute]:
        eligible = []
        estimated_tokens = estimate_payload_tokens(payload)
        for route in self.routes:
            if route.is_healthy() and estimated_tokens <= route.max_tokens:
                eligible.append(route)
        return eligible

    def select_routes(self, payload: Dict[str, Any]) -> List[ProviderRoute]:
        eligible = self.get_eligible_routes(payload)
        if not eligible:
            eligible = [r for r in self.routes if r.is_healthy()]
        if not eligible:
            return []
        
        # Sort by health score: prefer routes with recent success, fewer consecutive failures
        def health_score(route):
            # Healthy routes get high score
            if not route.is_healthy():
                return -1000
            
            # Factor in recent success (more recent = higher score)
            success_score = 0
            if route.last_success > 0:
                # Success in last 60 seconds gets bonus
                if time.time() - route.last_success < 60:
                    success_score = 100
                elif time.time() - route.last_success < 300:  # 5 minutes
                    success_score = 50
            
            # Factor in consecutive failures (fewer = better)
            failure_penalty = route.consecutive_failures * 10
            
            # Factor in route weight
            weight_score = route.weight * 10
            
            return success_score + weight_score - failure_penalty
        
        # Sort by health score (descending) then take top candidates
        sorted_routes = sorted(eligible, key=health_score, reverse=True)
        candidates = sorted_routes[:self.max_candidates]
        
        if len(candidates) <= 1:
            return candidates
        
        # Add some randomization to avoid always picking the same top route
        # but still prefer healthier routes
        weights = [max(0.1, health_score(r)) for r in candidates]  # Ensure positive weights
        total = sum(weights)
        if total > 0:
            weights = [w / total for w in weights]
        else:
            weights = [1.0 / len(candidates)] * len(candidates)
        
        selected = []
        remaining = candidates.copy()
        remaining_weights = weights.copy()
        for _ in range(min(3, len(candidates))):  # Select up to 3 routes
            if not remaining:
                break
            idx = self._rng.choices(range(len(remaining)), weights=remaining_weights, k=1)[0]
            selected.append(remaining.pop(idx))
            remaining_weights.pop(idx)
        return selected

    def send_request(
        self,
        task: str,
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": task})
        payload = {
            "model": "test",
            "messages": messages,
            "temperature": 0,
            "response_format": {"type": "json_object"}
        }
        selected_routes = self.select_routes(payload)
        if not selected_routes:
            return {
                "status": "error",
                "provider": None,
                "model": None,
                "output": None,
                "error": "No healthy routes available",
                "error_type": "no_routes",
                "timed_out": False,
                "duration": 0,
                "request_id": None,
                "attempt": 0,
            }
        last_error = None
        attempts = 0
        for route in selected_routes:
            if attempts >= max_retries:
                break
            attempts += 1
            route_payload = dict(payload)
            route_payload["model"] = route.model
            estimated = estimate_payload_tokens(route_payload)
            if estimated > route.max_tokens:
                route_payload = reduce_payload_tokens(route_payload, route.max_tokens)
            route.adapter.max_tokens = route.max_tokens
            route.adapter._reduced_request_used = False
            result = route.adapter.send_request(task, system_prompt)
            # Track analytics
            metric = RequestMetric(
                provider=route.provider,
                model=route.model,
                status=result["status"],
                error_type=result.get("error_type"),
                duration=result.get("duration", 0),
                estimated_tokens=estimated,
                attempt=attempts,
                timestamp=time.time(),
            )
            analytics.record(metric)
            if result["status"] == "success":
                route.record_success()
                result["router_attempt"] = attempts
                return result
            route.record_failure(result.get("error_type", ErrorClassifier.UNKNOWN))
            last_error = result
            error_type = result.get("error_type", ErrorClassifier.UNKNOWN)

            # Auth errors (401/403) are explicit failures - do NOT failover
            if error_type == ErrorClassifier.AUTH_ERROR:
                return {
                    "status": "error",
                    "provider": route.provider,
                    "model": route.model,
                    "output": None,
                    "error": f"Authentication failed for {route.provider}/{route.model}: {result.get('error')}",
                    "error_type": error_type,
                    "timed_out": False,
                    "duration": result.get("duration", 0),
                    "request_id": None,
                    "attempt": attempts,
                }

            # ALL_MODELS_RATE_LIMITED means all candidates genuinely failed - stop immediately
            if error_type == ErrorClassifier.ALL_MODELS_RATE_LIMITED:
                return {
                    "status": "error",
                    "provider": route.provider,
                    "model": route.model,
                    "output": None,
                    "error": f"All models rate limited on {route.provider}/{route.model}: {result.get('error')}",
                    "error_type": error_type,
                    "timed_out": False,
                    "duration": result.get("duration", 0),
                    "request_id": None,
                    "attempt": attempts,
                }

            # For all other error types, failover to the next route
            continue
        return {
            "status": "error",
            "provider": None,
            "model": None,
            "output": None,
            "error": f"All {len(selected_routes)} routes failed. Last error: {last_error.get('error') if last_error else 'unknown'}",
            "error_type": "all_routes_failed",
            "timed_out": False,
            "duration": 0,
            "request_id": None,
            "attempt": attempts,
        }

    def get_route_stats(self) -> List[Dict[str, Any]]:
        return [
            {
                "provider": r.provider,
                "model": r.model,
                "status": r.status.value,
                "total_requests": r.total_requests,
                "successful": r.successful_requests,
                "failed": r.failed_requests,
                "consecutive_failures": r.consecutive_failures,
                "success_rate": r.successful_requests / max(1, r.total_requests),
                "max_tokens": r.max_tokens,
            }
            for r in self.routes
        ]