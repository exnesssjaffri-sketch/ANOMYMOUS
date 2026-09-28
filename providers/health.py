"""Persistent health state for provider routes.

Stores:
- Recent failure counts
- Last success/failure timestamps
- Error category history

Does NOT persist:
- API keys or secrets
- Full request payloads
- Sensitive user data
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RouteHealthState:
    """Health state for a single route."""
    provider: str
    model: str
    consecutive_failures: int = 0
    last_success: float = 0
    last_failure: float = 0
    last_error_category: Optional[str] = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    error_history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "consecutive_failures": self.consecutive_failures,
            "last_success": self.last_success,
            "last_failure": self.last_failure,
            "last_error_category": self.last_error_category,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "error_history": self.error_history[-10:],  # Keep last 10 errors
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RouteHealthState":
        return cls(
            provider=data.get("provider", ""),
            model=data.get("model", ""),
            consecutive_failures=data.get("consecutive_failures", 0),
            last_success=data.get("last_success", 0),
            last_failure=data.get("last_failure", 0),
            last_error_category=data.get("last_error_category"),
            total_requests=data.get("total_requests", 0),
            successful_requests=data.get("successful_requests", 0),
            failed_requests=data.get("failed_requests", 0),
            error_history=data.get("error_history", []),
        )


class HealthStatePersistence:
    """Manages persistence of route health state."""

    def __init__(self, state_file: str = None):
        if state_file is None:
            # Use a unique temp file per instance to avoid interfering with tests
            import tempfile
            import uuid
            self.state_file = os.path.join(tempfile.gettempdir(), f"anonymously_health_{uuid.uuid4().hex}.json")
        else:
            self.state_file = state_file
        self._states: Dict[str, RouteHealthState] = {}
        self._load()

    def _load(self):
        """Load health state from file."""
        if not os.path.exists(self.state_file):
            return
        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
            for key, state_data in data.items():
                self._states[key] = RouteHealthState.from_dict(state_data)
        except (json.JSONDecodeError, OSError):
            pass

    def _save(self):
        """Save health state to file."""
        try:
            data = {key: state.to_dict() for key, state in self._states.items()}
            with open(self.state_file, "w") as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass

    def get_state(self, provider: str, model: str) -> Optional[RouteHealthState]:
        """Get health state for a route."""
        key = f"{provider}/{model}"
        return self._states.get(key)

    def get_or_create_state(self, provider: str, model: str) -> RouteHealthState:
        """Get or create health state for a route."""
        key = f"{provider}/{model}"
        if key not in self._states:
            self._states[key] = RouteHealthState(provider=provider, model=model)
        return self._states[key]

    def record_success(self, provider: str, model: str):
        """Record a successful request."""
        state = self.get_or_create_state(provider, model)
        state.consecutive_failures = 0
        state.last_success = time.time()
        state.total_requests += 1
        state.successful_requests += 1
        self._save()

    def record_failure(self, provider: str, model: str, error_category: str):
        """Record a failed request."""
        state = self.get_or_create_state(provider, model)
        state.consecutive_failures += 1
        state.last_failure = time.time()
        state.last_error_category = error_category
        state.total_requests += 1
        state.failed_requests += 1
        state.error_history.append({
            "timestamp": time.time(),
            "error_category": error_category,
        })
        self._save()

    def get_all_states(self) -> Dict[str, RouteHealthState]:
        """Get all health states."""
        return dict(self._states)

    def reset_state(self, provider: str, model: str):
        """Reset health state for a route."""
        key = f"{provider}/{model}"
        if key in self._states:
            del self._states[key]
            self._save()

    def is_provider_healthy(self, provider: str, quarantine_minutes: int = 300) -> bool:
        """Check if a provider has any healthy routes."""
        for state in self._states.values():
            if state.provider != provider:
                continue
            if state.consecutive_failures == 0:
                return True
            if state.last_failure > 0:
                if time.time() - state.last_failure > quarantine_minutes * 60:
                    return True
        return False