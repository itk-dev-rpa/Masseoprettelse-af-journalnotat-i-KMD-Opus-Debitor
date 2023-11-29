"""This module contains the main process of the robot."""

import json
import threading

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement, QueueStatus
from itk_dev_shared_components.sap import multi_session, opret_kundekontakt


def process(orchestrator_connection: OrchestratorConnection) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")

    multi_session.spawn_sessions(6)

    # Create 20x6 kundekontakter per run
    for _ in range(20):
        queue_elements: list[QueueElement] = []

        # Get up to 6 new queue elements
        for _ in range(6):
            qe = orchestrator_connection.get_next_queue_element("Masseoprettelse-af-journalnotat-i-KMD-Opus-Debitor")
            if qe is None:
                break
            queue_elements.append(qe)

        # Stop if no more queue elements
        if len(queue_elements) == 0:
            orchestrator_connection.log_info("No more queue elements.")
            break

        orchestrator_connection.log_info(f"Creating {len(queue_elements)} kundekontakter.")

        lock = threading.Lock()
        args = [[qe, orchestrator_connection, lock] for qe in queue_elements]

        multi_session.run_batch(do_task, args)

    else:
        orchestrator_connection.log_info("Limit reached (120). Stopping for now.")


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
    except Exception:
        orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.FAILED)
