# SkyNopy - Interview challange

This project implements a Python-based API that acts as an intelligent proxy and registry for satellite TLE (Two-Line Element) data, as required in the Skynopy coding challenge.

**Requirements:** Python 3.10+, see `requirements.txt` for dependencies.

---

## API Endpoints

### GET /satellite_tle/{norad_id}
Fetches the **latest TLE (by epoch)** for a given NORAD ID.  
If the latest TLE in the local store is **older than 1 hour (based on fetch time)** or does not exist, the API fetches the latest from CelesTrak.

**Response:**
```json
{
  "line1": "1 12345U 24022A   24211.20428626 .00001782 00000+0 38520-3 0 9993",
  "line2": "2 12345 98.3320 160.7411 0001541 53.5545 58.5641 14.59534437182847",
  "epoch": "2024-07-29T04:54:10.332Z",
  "source": "celestrak"
}
```
`source` is either `"celestrak"` or `"client"`.

### GET /satellite_tle/{norad_id}/history
Retrieves all TLEs currently stored for that satellite, **ordered by epoch (latest first)**.

**Response:** `{ "norad_id": "...", "count": N, "tles": [ { "line1", "line2", "epoch", "source", ... } ] }`

### POST /satellite_tle/{norad_id}
Allows clients to upload a **custom TLE** (e.g. after a maneuver).  
Request body must be JSON with `line1` and `line2`. The NORAD ID in the lines must match `{norad_id}`.

---

## Notes on Implementation (AI Usage & Design Decisions)

### AI Usage
AI tools (Cursor AI / ChatGPT) were used for:
- Generating the API endpoints in this README file.
- Generating unit test using my insomnia file.
- Iterating on the TLE epoch parsing logic after validating responses manually using Insomnia.
- Minor boilerplate suggestions for model serialization (`to_dict` methods).


### My Design Decisions
- I introduced **service and repository interfaces** to decouple:
  - External TLE providers (CelesTrak, mock service)
  - Persistence layer (in-memory storage, future DB support)
- I implemented a **Coordinator Service layer** (Works like a controller) to centralize business logic (refresh logic, validation, orchestration).
- A layered architecture was chosen to make the system scalable and maintainable if extended into a production GSaaS platform.
- In-memory storage was used as required by the challenge, but the design allows easy migration to PostgreSQL or Redis.

---

## Future Goals / Potential Extensions

For a more complex and production-ready system, I would add a React-based frontend and integrate Keycloak for user authentication and authorization. Logging and monitoring (Grafana or Datadog) would be introduced to improve observability and operational insight. For larger-scale persistence needs, a database with an ORM such as SQLAlchemy could be added, but it was intentionally avoided here to keep the solution simple and aligned with the challenge scope.
