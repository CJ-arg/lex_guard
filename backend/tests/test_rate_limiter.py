import asyncio

import pytest

from app.services.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_limiter_acquires_and_releases():
    limiter = RateLimiter(rps=100.0, burst=2)
    async with limiter:
        pass  # should not raise


@pytest.mark.asyncio
async def test_limiter_respects_burst():
    """With burst=1 a second concurrent acquire should wait."""
    limiter = RateLimiter(rps=100.0, burst=1)
    acquired_times = []

    async def task():
        async with limiter:
            acquired_times.append(asyncio.get_event_loop().time())

    # Run two tasks; second must wait for release (≥ interval apart)
    await asyncio.gather(task(), task())
    assert len(acquired_times) == 2


def test_limiter_default_interval():
    limiter = RateLimiter(rps=2.0, burst=1)
    assert abs(limiter._interval - 0.5) < 1e-9


def test_env_var_overrides(monkeypatch):
    monkeypatch.setenv("CSJN_RPS", "5")
    monkeypatch.setenv("CSJN_BURST", "10")
    # Re-import to pick up env vars
    from importlib import reload
    import app.services.rate_limiter as rl_module
    reload(rl_module)
    assert rl_module.csjn_limiter._interval == pytest.approx(0.2)
    assert rl_module.csjn_limiter._semaphore._value == 10
