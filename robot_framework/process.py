"""This module contains the main process of the robot."""

import json
import threading

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement, QueueStatus
from itk_dev_shared_components.sap import multi_session, opret_kundekontakt


def process(orchestrator_connection: OrchestratorConnection, queue_elements: list[QueueElement]) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")

    orchestrator_connection.log_info(f"Creating {len(queue_elements)} kundekontakter.")

    lock = threading.Lock()
    args_list = [[qe, orchestrator_connection, lock] for qe in queue_elements]

    multi_session.run_batch(do_task, args_list)


def do_task(session, queue_element: QueueElement, orchestrator_connection: OrchestratorConnection, lock: threading.Lock):
    """A function for multithreading.
    Extract queue element data.
    Create kundekontakt.
    Mark queue element as Done/Failed

    Args:
        session: A SAP session.
        queue_element: A queue element.
        orchestrator_connection: The orchestrator connection for setting status.
        lock: A threading lock used in opret_kundekontakter.
    """
    data = json.loads(queue_element.data)

    fp = queue_element.reference
    aftaleindhold = data['aftaleindhold'] or None
    art = data['art']
    notat = data['notat']

    try:
        opret_kundekontakt.opret_kundekontakter(session, fp, aftaleindhold, art, notat, lock)
        orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.DONE)
    # pylint: disable-next=broad-exception-caught
    except Exception as exc:
        orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.FAILED)
        raise exc
