"""This module is the primary module of the robot framework. It collects the functionality of the rest of the framework."""

import traceback
import sys

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement

from robot_framework import initialize
from robot_framework import reset
from robot_framework import error_screenshot
from robot_framework import process
from robot_framework import config


def main():
    """The entry point for the framework. Should be called as the first thing when running the robot."""
    orchestrator_connection = OrchestratorConnection.create_connection_from_args()
    sys.excepthook = log_exception(orchestrator_connection)

    orchestrator_connection.log_trace("Robot Framework started.")
    initialize.initialize(orchestrator_connection)

    error_email = orchestrator_connection.get_constant(config.ERROR_EMAIL).value

    task_count = 0
    error_count = 0
    for _ in range(config.MAX_RETRY_COUNT):
        try:
            reset.reset(orchestrator_connection)

            while task_count < config.MAX_TASK_COUNT:
                queue_elements: list[QueueElement] = []

                # Get up to 6 new queue elements
                for _ in range(config.THREAD_COUNT):
                    queue_element = orchestrator_connection.get_next_queue_element(config.QUEUE_NAME)
                    if queue_element is None:
                        break
                    queue_elements.append(queue_element)
                    task_count += 1

                # Stop if no more queue elements
                if len(queue_elements) == 0:
                    orchestrator_connection.log_info("No more queue elements.")
                    break  # TODO: Break outer loop

                process.process(orchestrator_connection, queue_elements)
            else:
                orchestrator_connection.log_info("Limit reached. Stopping for now.")
                break

        # If any business rules are broken the robot should stop entirely.
        except BusinessError as error:
            orchestrator_connection.log_error(f"BusinessError: {error}\nTrace: {traceback.format_exc()}")
            error_screenshot.send_error_screenshot(error_email, error, orchestrator_connection.process_name)
            break

        # We actually want to catch all exceptions possible here.
        # pylint: disable-next = broad-exception-caught
        except Exception as error:
            error_count += 1
            error_type = type(error).__name__
            orchestrator_connection.log_error(f"Error caught during process. Total number of errors caught: {error_count}. {error_type}: {error}\nTrace: {traceback.format_exc()}")
            error_screenshot.send_error_screenshot(error_email, error, orchestrator_connection.process_name)

    reset.clean_up(orchestrator_connection)
    reset.close_all(orchestrator_connection)
    reset.kill_all(orchestrator_connection)

    if error_count == config.MAX_RETRY_COUNT:
        raise RuntimeError("The process failed too many times.")


def log_exception(orchestrator_connection: OrchestratorConnection) -> callable:
    """Creates a function to be used as an exception hook that logs any uncaught exception in OpenOrchestrator.

    Args:
        orchestrator_connection: The connection to OpenOrchestrator.

    Returns:
        callable: A function that can be assigned to sys.excepthook.
    """
    def inner(exception_type, value, traceback_string):
        orchestrator_connection.log_error(f"Uncaught Exception:\nType: {exception_type}\nValue: {value}\nTrace: {traceback_string}")
    return inner


class BusinessError(Exception):
    """An empty exception used to identify errors caused by breaking business rules"""
