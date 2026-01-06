import functools
import time
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class RetryConfig:
    attempts: int = 3
    delay: float = 0.5
    backoff: float = 2.0
    retry_on: tuple[type[BaseException], ...] = (Exception,)


def _validate_config(cfg: RetryConfig) -> None:
    if cfg.attempts < 1:
        raise ValueError("attempts must be >= 1")
    if cfg.delay < 0:
        raise ValueError("delay must be >= 0")
    if cfg.backoff < 1:
        raise ValueError("backoff must be >= 1")


def _log(logger, level: str, msg: str, *args) -> None:
    if not logger:
        return
    getattr(logger, level)(msg, *args)


def _now_ms() -> float:
    return time.perf_counter() * 1000.0


def _sleep(seconds: float, logger=None) -> None:
    if seconds <= 0:
        return
    _log(logger, "info", "Sleeping %.2f s before retry", seconds)
    time.sleep(seconds)


def _call_with_timing(func: Callable, args: tuple, kwargs: dict) -> tuple[object, float]:
    start = _now_ms()
    result = func(*args, **kwargs)
    elapsed_ms = _now_ms() - start
    return result, elapsed_ms


def _log_attempt_start(logger, attempt: int, total: int, name: str) -> None:
    _log(logger, "info", "Attempt %d/%d: calling %s", attempt, total, name)


def _log_attempt_success(logger, attempt: int, total: int, name: str, elapsed_ms: float) -> None:
    _log(logger, "info", "Attempt %d/%d: success %s (%.2f ms)", attempt, total, name, elapsed_ms)


def _log_attempt_fail(logger, attempt: int, total: int, name: str, elapsed_ms: float, exc: BaseException) -> None:
    _log(
        logger,
        "warning",
        "Attempt %d/%d: failed %s (%.2f ms) %s: %s",
        attempt,
        total,
        name,
        elapsed_ms,
        type(exc).__name__,
        str(exc),
    )


def _log_final_fail(logger, total: int, name: str, exc: BaseException) -> None:
    _log(
        logger,
        "error",
        "All %d attempts failed for %s. Raising last error: %s: %s",
        total,
        name,
        type(exc).__name__,
        str(exc),
    )


def _run_with_retry(
    func: Callable,
    args: tuple,
    kwargs: dict,
    cfg: RetryConfig,
    logger=None,
):
    delay = cfg.delay
    last_exc: Optional[BaseException] = None
    name = getattr(func, "__qualname__", getattr(func, "__name__", "function"))

    for attempt in range(1, cfg.attempts + 1):
        _log_attempt_start(logger, attempt, cfg.attempts, name)

        start = _now_ms()
        try:
            result = func(*args, **kwargs)
            elapsed_ms = _now_ms() - start
            _log_attempt_success(logger, attempt, cfg.attempts, name, elapsed_ms)
            return result

        except cfg.retry_on as exc:
            elapsed_ms = _now_ms() - start
            last_exc = exc
            _log_attempt_fail(logger, attempt, cfg.attempts, name, elapsed_ms, exc)

            if attempt >= cfg.attempts:
                break

            _sleep(delay, logger=logger)
            delay *= cfg.backoff

    _log_final_fail(logger, cfg.attempts, name, last_exc)
    raise last_exc


def retry(*, config: RetryConfig, logger=None):
    _validate_config(config)

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return _run_with_retry(func, args, kwargs, config, logger=logger)

        return wrapper

    return decorator
