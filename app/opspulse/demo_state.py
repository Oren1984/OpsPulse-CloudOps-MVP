"""Controlled demo-failure switch.

This is an in-memory, process-local flag intentionally kept out of the
database. It only has any effect when `settings.demo_mode_enabled` is
true (development/demo environments) and is never wired into any
production-facing code path.
"""

from opspulse.metrics import DEMO_FAILURE_ACTIVE


class DemoFailureState:
    def __init__(self) -> None:
        self._active = False

    @property
    def active(self) -> bool:
        return self._active

    def trigger(self) -> None:
        self._active = True
        DEMO_FAILURE_ACTIVE.set(1)

    def restore(self) -> None:
        self._active = False
        DEMO_FAILURE_ACTIVE.set(0)


demo_failure_state = DemoFailureState()
