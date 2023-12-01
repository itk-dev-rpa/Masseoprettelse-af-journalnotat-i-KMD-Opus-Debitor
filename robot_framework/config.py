"""This module contains configuration constants used across the framework"""

# The number of times the robot retries on an error before terminating.
MAX_RETRY_COUNT = 3

# Error screenshot config
SMTP_SERVER = "smtp.aarhuskommune.local"
SMTP_PORT = 25
SCREENSHOT_SENDER = "robot@friend.dk"

# Constant names
ERROR_EMAIL = "Error Email"
SAP_CREDENTIAL = "Mathias SAP"

MAX_TASK_COUNT = 600
QUEUE_NAME = "Masseoprettelse-af-journalnotat-i-KMD-Opus-Debitor"

THREAD_COUNT = 6