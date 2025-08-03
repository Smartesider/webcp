"""
CONFIGURATION FILE FOR SKYCODE.NO HOSTING DASHBOARD

LOCKED CONSTANTS - DO NOT MODIFY WITHOUT APPROVAL
These constants define core operational parameters that must remain consistent
to ensure system security and stability.
"""

# LOCK: FastAPI server port - MUST be 8098
API_PORT: int = 8098

# LOCK: API base URL - frontend and backend must use this
API_BASE_URL: str = "https://cp.skycode.no/api/v1"

# LOCK: Root directory for all frontend static files
BASE_FRONTEND_DIR: str = "/home/skycode.no/public_html/cp/"

# LOCK: Allowed CORS origin
ALLOWED_ORIGIN: str = "https://cp.skycode.no"

# LOCK: Max backup versions per file/config
MAX_BACKUP_VERSIONS: int = 5

# LOCK: Lock file directory for operation locks
LOCK_DIR: str = "/var/lock/skycode/"

# LOCK: Log directory
LOG_DIR: str = "/var/log/skycode/"

# Add more config constants below as needed...
