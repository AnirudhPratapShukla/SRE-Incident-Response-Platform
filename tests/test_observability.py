from utils.logger import get_logger
from utils.instrumentation import log_agent_execution


@log_agent_execution("test_agent")
def test_agent(state):

    return {
        **state,
        "test": "passed"
    }


def test_logger():

    logger = get_logger(
        "observability_test"
    )

    logger.info(
        "Observability logger test"
    )

    assert logger is not None

    print(
        "PASS: Logger creation works"
    )


def test_agent_instrumentation():

    state = {
        "incident": "Test incident",
        "service": "test-service"
    }

    result = test_agent(state)

    assert result["test"] == "passed"

    print(
        "PASS: Agent instrumentation works"
    )


if __name__ == "__main__":

    print(
        "\nStarting Observability Tests...\n"
    )

    test_logger()
    test_agent_instrumentation()

    print(
        "\nAll observability tests passed."
    )
