from langgraph.errors import GraphInterrupt
import time
from functools import wraps

from utils.logger import get_logger


def log_agent_execution(agent_name: str):
    """
    Decorator that logs agent start, completion, execution time,
    and failures.
    """

    logger = get_logger(agent_name)

    def decorator(func):

        @wraps(func)
        def wrapper(state, *args, **kwargs):

            service = state.get(
                "service",
                "unknown"
            )

            incident = state.get(
                "incident",
                "unknown"
            )

            start_time = time.perf_counter()

            logger.info(
                "Started | service=%s | incident=%s",
                service,
                incident
            )

            try:

                result = func(
                    state,
                    *args,
                    **kwargs
                )

                duration = (
                    time.perf_counter()
                    - start_time
                )

                logger.info(
                    "Completed | service=%s | duration=%.2fs",
                    service,
                    duration
                )

                return result

            except GraphInterrupt:

                duration = (
                    time.perf_counter()
                    - start_time
                )

                logger.info(
                    "Paused | service=%s | duration=%.2fs | reason=human_approval",
                    service,
                    duration
                )

                raise

            except Exception:

                duration = (
                    time.perf_counter()
                    - start_time
                )

                logger.exception(
                    "Failed | service=%s | duration=%.2fs",
                    service,
                    duration
                )

                raise

        return wrapper

    return decorator
