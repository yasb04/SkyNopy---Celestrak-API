from flask import Flask
from infrastructure.repositories.tle_storage import TLEStorage
from infrastructure.mocks.mock_tle_service import MockTLEService
from domain.services.tle_coordinator_service import TLECoordinatorService
from presentation.routes import create_routes


app = Flask(__name__)

tle_service = MockTLEService()

"""
USE_MOCK = false

if USE_MOCK:
    tle_service = MockTLEService()
else:
    # use the service instead
"""

storage = TLEStorage()

# DI
coordinator = TLECoordinatorService(
    repository=storage,
    service=tle_service,
    refresh_interval_hours=1
)

# Register routes
create_routes(app, coordinator)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
