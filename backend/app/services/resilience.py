import time
import logging
import functools
from typing import Callable, Any

logger = logging.getLogger(__name__)

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    """
    Circuit Breaker pattern for external OSINT calls.
    Trips open after `failure_threshold` consecutive failures and stays open for `reset_timeout` seconds.
    """
    def __init__(self, name: str, failure_threshold: int = 3, reset_timeout: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.is_open = False

    def call(self, func: Callable, *args, **kwargs) -> Any:
        now = time.time()
        if self.is_open:
            if now - self.last_failure_time > self.reset_timeout:
                # Half-open retry state
                logger.info(f"[CircuitBreaker:{self.name}] Attempting reset (half-open).")
                self.is_open = False
                self.failure_count = 0
            else:
                logger.warning(f"[CircuitBreaker:{self.name}] Circuit is OPEN. Fast failing call.")
                raise CircuitBreakerOpenException(f"Circuit breaker for {self.name} is OPEN.")

        try:
            result = func(*args, **kwargs)
            # Success -> reset failure count
            self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            logger.warning(f"[CircuitBreaker:{self.name}] Failure #{self.failure_count}: {e}")
            
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
                logger.error(f"[CircuitBreaker:{self.name}] Failure threshold reached. Circuit TRIPPED OPEN.")
            raise e

def with_retry_and_circuit_breaker(circuit_name: str, max_retries: int = 3, backoff_base: float = 1.0):
    """
    Decorator adding exponential backoff and circuit breaker protection to external calls.
    """
    # Trip only after several consecutive failures, independent of how many retries each call gets.
    cb = CircuitBreaker(circuit_name, failure_threshold=max(3, max_retries))
    
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                def run_attempt():
                    for attempt in range(1, max_retries + 1):
                        try:
                            return func(*args, **kwargs)
                        except Exception as err:
                            if attempt == max_retries:
                                raise err
                            sleep_dur = backoff_base * (2 ** (attempt - 1))
                            logger.info(f"[Retry:{circuit_name}] Attempt {attempt}/{max_retries} failed ({err}). Retrying in {sleep_dur}s...")
                            time.sleep(sleep_dur)

                return cb.call(run_attempt)
            except (CircuitBreakerOpenException, Exception) as final_err:
                logger.error(f"[Resilience:{circuit_name}] Gracefully degrading call due to failure: {final_err}")
                return f"[{circuit_name} Search Unavailable - Circuit Breaker Graceful Fallback]"
        return wrapper
    return decorator
