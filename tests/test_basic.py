import pytest
from datetime import datetime, timezone, timedelta
from domain.models.tle import TLE
from domain.models.tle_entry import TLEEntry
from infrastructure.utils.tle_parser import TLEParser
from infrastructure.mocks.mock_tle_service import MockTLEService
from infrastructure.repositories.tle_storage import TLEStorage
from domain.services.tle_coordinator_service import TLECoordinatorService
from flask import Flask
from presentation.routes import create_routes


# PDF examples
EXAMPLE_LINE1 = "1 54234U 22150A   26025.23306172  .00000191  00000+0  11139-3 0  9995"
EXAMPLE_LINE2 = "2 54234  98.7509 326.0095 0000754 215.9195 144.1931 14.19539113166262"

NOAA21_LINE1 = "1 54234U 22150A   26018.88939962  .00000052  00000+0  45304-4 0  9995"
NOAA21_LINE2 = "2 54234  98.7504 319.7421 0000606 261.7569  98.3539 14.19535520165361 " 


def _make_app_client():
    """Create Flask app + test client with mock service."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    storage = TLEStorage()
    coordinator = TLECoordinatorService(storage, MockTLEService(), refresh_interval_hours=1)
    create_routes(app, coordinator)
    return app.test_client()


def test_tle_model_creation():
    """Test creating a TLE model."""
    tle = TLE(line1=EXAMPLE_LINE1, line2=EXAMPLE_LINE2)
    assert tle.norad_id == "54234"
    assert tle.line1 == EXAMPLE_LINE1
    assert tle.line2 == EXAMPLE_LINE2


def test_tle_parser_extracts_norad_id():
    """Test parser extracts NORAD ID correctly."""
    tle = TLEParser.parse_tle(EXAMPLE_LINE1, EXAMPLE_LINE2)
    assert tle.norad_id == "54234"


def test_tle_parser_extracts_epoch():
    """Test parser extracts and converts epoch."""
    tle = TLEParser.parse_tle(EXAMPLE_LINE1, EXAMPLE_LINE2)
    assert tle.epoch is not None
    assert tle.epoch.endswith("Z")
    assert "2026-01-25" in tle.epoch


def test_tle_validation():
    """Test TLE validation."""
    assert TLEParser.validate_tle(EXAMPLE_LINE1, EXAMPLE_LINE2) is True


def test_mock_service():
    """Test mock service returns TLE for known satellite."""
    service = MockTLEService()
    tle = service.fetch_tle("54234")
    assert tle is not None
    assert tle.norad_id == "54234"


def test_storage_get_latest_tle():
    """Test coordinator fetches and returns latest TLE."""
    service = MockTLEService()
    storage = TLEStorage()
    coordinator = TLECoordinatorService(storage, service, refresh_interval_hours=1)
    
    tle_entry = coordinator.get_latest_tle("54234")
    assert tle_entry is not None
    assert isinstance(tle_entry, TLEEntry)
    assert tle_entry.tle.line1 is not None
    assert tle_entry.tle.line2 is not None
    assert tle_entry.tle.epoch is not None
    assert tle_entry.source is not None


def test_storage_add_custom_tle():
    """Test adding custom TLE."""
    service = MockTLEService()
    storage = TLEStorage()
    coordinator = TLECoordinatorService(storage, service, refresh_interval_hours=1)
    
    tle_entry = coordinator.add_custom_tle("54234", EXAMPLE_LINE1, EXAMPLE_LINE2)
    assert tle_entry is not None
    assert tle_entry.source == "client"
    
    history = coordinator.get_tle_history("54234")
    assert len(history) > 0
    assert any(tle_entry.source == "client" for tle_entry in history)


def test_api_get_satellite_tle():
    """Test GET /satellite_tle/{norad_id} endpoint."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    service = MockTLEService()
    storage = TLEStorage()
    coordinator = TLECoordinatorService(storage, service, refresh_interval_hours=1)
    create_routes(app, coordinator)
    
    client = app.test_client()
    response = client.get("/satellite_tle/54234")
    
    assert response.status_code == 200
    data = response.get_json()
    assert "line1" in data
    assert "line2" in data
    assert "epoch" in data
    assert "source" in data


def test_api_post_satellite_tle():
    """Test POST /satellite_tle/{norad_id} endpoint."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    service = MockTLEService()
    storage = TLEStorage()
    coordinator = TLECoordinatorService(storage, service, refresh_interval_hours=1)
    create_routes(app, coordinator)
    
    client = app.test_client()
    payload = {
        "line1": EXAMPLE_LINE1,
        "line2": EXAMPLE_LINE2
    }
    
    response = client.post("/satellite_tle/54234", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["source"] == "client"


def test_api_get_history():
    """Test GET /satellite_tle/{norad_id}/history endpoint."""
    client = _make_app_client()
    coordinator = TLECoordinatorService(TLEStorage(), MockTLEService(), refresh_interval_hours=1)
    # Need to fetch first
    app = Flask(__name__)
    app.config["TESTING"] = True
    storage = TLEStorage()
    coord = TLECoordinatorService(storage, MockTLEService(), refresh_interval_hours=1)
    create_routes(app, coord)
    coord.get_latest_tle("54234")
    client = app.test_client()
    response = client.get("/satellite_tle/54234/history")
    assert response.status_code == 200
    data = response.get_json()
    assert "tles" in data
    assert len(data["tles"]) > 0