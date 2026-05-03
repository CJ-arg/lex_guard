import asyncio
import os


class RateLimiter:
    """Asyncio semaphore-based rate limiter. Releases a slot after `interval` seconds."""

    def __init__(self, rps: float, burst: int = 1):
        self._semaphore = asyncio.Semaphore(burst)
        self._interval = 1.0 / rps

    async def __aenter__(self):
        await self._semaphore.acquire()
        return self

    async def __aexit__(self, *args):
        asyncio.get_event_loop().call_later(self._interval, self._semaphore.release)


def _make_limiter(rps_env: str, burst_env: str, default_rps: float, default_burst: int) -> RateLimiter:
    rps = float(os.getenv(rps_env, str(default_rps)))
    burst = int(os.getenv(burst_env, str(default_burst)))
    return RateLimiter(rps=rps, burst=burst)


csjn_limiter = _make_limiter("CSJN_RPS", "CSJN_BURST", 1.0, 3)
saij_limiter = _make_limiter("SAIJ_RPS", "SAIJ_BURST", 1.0, 3)
juba_limiter = _make_limiter("JUBA_RPS", "JUBA_BURST", 0.5, 2)
