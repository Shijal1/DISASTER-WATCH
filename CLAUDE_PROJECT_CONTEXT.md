# DISASTERWATCH — Project Context and Technical Handoff

> This document is a code-oriented handoff for an AI assistant working on this repository. It describes the implementation found in the project scan on **2026-10-26**. Treat the source code as authoritative if this document and the code diverge. In particular, this is a prototype/demo decision-support application: it is not a validated emergency-response system, and its predictions must not be presented as authoritative forecasts.

## 1. Project in one paragraph

**DISASTERWATCH** is a web-based disaster intelligence and emergency-response coordination prototype. It combines incident reports submitted through an SOS form with public hazard-event feeds (USGS earthquakes, NASA EONET events, and GDACS alerts), stores normalized incidents and response-related records in SQLite, and presents them on a React/Leaflet map. Operators can view/acknowledge alerts, move incidents through response states, create heuristic impact zones, assign a nearby compatible response asset, and optionally request satellite-based flood-water detection from Copernicus Sentinel-2. A WebSocket endpoint pushes selected backend events to connected browsers.

The project’s declared goal is an **AI-assisted** disaster platform. The currently implemented SOS classifier is a deterministic word-list/lexicon heuristic, and propagation and population figures are assumption-based estimates. Do not describe these components as trained machine-learning models or validated forecasts.

## 2. Product surfaces and primary users

- **Citizen reporter:** submits category, description, affected-person count, and coordinates on `/sos`; browser geolocation can fill coordinates.
- **Operator/dispatcher:** uses the main map to inspect incidents and alerts, generate impact zones, start/resolve response, request an asset assignment, or run the flood-analysis action for flood incidents.
- **Administrator/demo operator:** uses `/admin` to view and create sample ambulance assets and relief camps. The current page is deliberately narrow; it is not a complete management console.

The frontend has three routes: `/` (map/operations view), `/sos` (citizen submission), and `/admin` (assets and camps). The backend has no user, role, login, or authorization model. “operator” names in the interface and API are labels, not authenticated identities.

## 3. Repository layout

```text
README.md                         Empty at scan time
CLAUDE_PROJECT_CONTEXT.md         This handoff document
backend/
  .env.example                    Example settings (satellite key names currently mismatch app)
  requirements.txt                Pinned Python dependencies
  app/
    main.py                       FastAPI setup, lifecycle, WebSocket, router registration
    config.py                     Environment-backed settings
    database.py                   SQLAlchemy engine/session/Base and create_all
    feeds/                        External public-event adapters and polling scheduler
    intelligence/                 SOS triage, correlation, predictions, allocation,
                                  escalation, satellite access, flood image analysis
    models/                       SQLAlchemy database entities
    realtime/manager.py           In-process WebSocket connection/broadcast manager
    routers/                      HTTP API endpoints
    schemas/                      Pydantic request/response models
    utils/geo.py                  Haversine distance and GeoJSON circle helpers
  data/disasterwatch.db           Existing SQLite database
  benchmark.py                    Script that exercises a running API
  benchmark_report.json           Saved benchmark output from 2026-10-08
  check_db.py                     SQLite table/count inspection utility
  count_corr.py                   Correlation-specific inspection utility
  migrate_response_lifecycle.py   Manual SQLite ALTER TABLE migration
frontend/
  package.json                    React/Vite dependencies and scripts
  vite.config.js                  Dev server and API/WebSocket proxy
  src/
    App.jsx, main.jsx, index.css  App shell, route setup, global styling
    pages/                        Map, SOS, and admin screens
    api/                          Axios API wrappers
    components/                   Map layers, panels, shared components, SOS form
    hooks/useWebSocket.js         WebSocket connection and reconnect
    store/                        Zustand incident, asset, and UI state
```

The repository also contains local `backend/venv` and `frontend/node_modules` directories in this workspace, but they are installed artifacts, not source modules. Do not treat vendor files as project code.

## 4. Technology stack

### Backend

- Python with **FastAPI 0.111.0**, **Starlette 0.37.2**, and **Uvicorn 0.32.0**.
- **SQLAlchemy 2.0.36** ORM with a default SQLite database.
- **Pydantic 2.9.2** and **pydantic-settings 2.6.1** for settings and API schemas.
- **APScheduler 3.10.4** for periodic polling and alert escalation.
- **httpx 0.27.2** for async external HTTP requests.
- **Pillow 10.4.0** for PNG tile analysis; `python-multipart` is installed, though no upload route is currently present.
- Dependencies are pinned in [`backend/requirements.txt`](backend/requirements.txt).

### Frontend

- React 18, React DOM, React Router 6, Vite 5.
- Leaflet 1.9 / React Leaflet 4 for maps and geographic overlays.
- Axios for JSON API calls and Zustand for shared UI/data state.
- Tailwind CSS 3 with PostCSS and Autoprefixer.
- Lucide React for icons.
- Package versions/scripts are in [`frontend/package.json`](frontend/package.json); `frontend/package-lock.json` is present.

### External services and map tiles

- USGS earthquake GeoJSON, NASA EONET events API, and GDACS RSS.
- Copernicus Data Space OAuth client-credentials token service and WMS endpoint for Sentinel-2 layers.
- OpenStreetMap, Esri World Imagery, and OpenTopoMap basemaps.
- These are network dependencies; external outages, rate limits, credentials, and terms of use can affect behavior.

## 5. Running the project locally

There is no root-level package runner, Docker setup, or documented deployment workflow in the scanned source. Start each application separately.

### Backend (PowerShell)

```powershell
cd C:\path\to\disasterwatch\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Optional: copy .env.example to .env and edit settings
uvicorn app.main:app --reload
```

The API normally listens at `http://127.0.0.1:8000`; FastAPI’s interactive OpenAPI UI is available at `/docs`. The backend expects imports to resolve from the `backend` directory, so run Uvicorn from there.

### Frontend

```powershell
cd C:\path\to\disasterwatch\frontend
npm ci
npm run dev
```

Vite listens on port **5173**. Its dev-server proxy forwards `/api` to `http://127.0.0.1:8000` and `/ws` to the backend WebSocket. `npm run build` runs the production frontend build; `npm run preview` serves the built output locally.

### Database setup and persistence

The default URL is `sqlite:///./data/disasterwatch.db`. Since it is relative, the effective location depends on the backend process working directory; launching from `backend` resolves to `backend/data/disasterwatch.db`. At application startup, `init_db()` imports models and calls SQLAlchemy `Base.metadata.create_all()`. This creates missing tables but is **not a schema migration system** and will not add newly introduced columns to existing tables. `migrate_response_lifecycle.py` is a manual migration script for acknowledgement/response lifecycle columns; verify the DB schema before running older databases.

## 6. Configuration and environment

Settings are defined in [`backend/app/config.py`](backend/app/config.py); Pydantic Settings loads `.env` and ignores extra keys.

| Setting | Default | Purpose / caveat |
|---|---|---|
| `APP_NAME` | `DISASTERWATCH` | API title and root response |
| `APP_VERSION` | `0.1.0` | API version string |
| `DEBUG` | `True` | Present in settings; not otherwise used in the scanned app |
| `DATABASE_URL` | `sqlite:///./data/disasterwatch.db` | SQLAlchemy connection |
| `USGS_POLL_INTERVAL` | `300` | Configured setting; scheduler currently does not read it |
| `EONET_POLL_INTERVAL` | `600` | Configured setting; scheduler currently does not read it |
| `GDACS_POLL_INTERVAL` | `900` | Configured setting; scheduler currently does not read it |
| `COPERNICUS_CLIENT_ID` | empty | Required by satellite token helper |
| `COPERNICUS_CLIENT_SECRET` | empty | Required by satellite token helper |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | Included in backend CORS allowlist |

**Important mismatch:** [`backend/.env.example`](backend/.env.example) currently documents `COPERNICUS_USER` and `COPERNICUS_PASSWORD`, but the implementation requires `COPERNICUS_CLIENT_ID` and `COPERNICUS_CLIENT_SECRET`. The sample values therefore will not enable satellite credentials without correcting the names. The scheduler uses a hard-coded five-minute feed interval despite the three per-source interval settings.

## 7. Backend architecture and startup lifecycle

[`backend/app/main.py`](backend/app/main.py) creates the FastAPI application and registers routers. Its lifespan sequence is:

1. `init_db()` ensures model tables exist.
2. `start_scheduler()` starts APScheduler jobs.
3. `asyncio.create_task(poll_all())` requests an immediate initial feed poll.
4. On shutdown, the current lifespan code does not explicitly stop the scheduler or await that task.

The scheduler in [`backend/app/feeds/scheduler.py`](backend/app/feeds/scheduler.py) polls all three sources sequentially every **300 seconds** and checks escalation every **60 seconds**. Poll failures are logged to stdout and do not stop the loop. The service has root and health JSON endpoints and a WebSocket at `/ws/events`.

Routers depend on `get_db()` in [`backend/app/database.py`](backend/app/database.py), which yields a SQLAlchemy session and closes it after each request. There is a single process-local in-memory WebSocket manager; it is not a distributed event bus and does not coordinate across multiple backend workers.

### Feed ingestion pipeline

1. Each `FeedAdapter` fetches data asynchronously, then normalizes individual entries into the internal incident shape.
2. Adapters are `USGSAdapter`, `EONETAdapter`, and `GDACSAdapter` in `backend/app/feeds/`.
3. The scheduler deduplicates against existing incidents using source + type + latitude/longitude within a simple `0.01` degree box.
4. New incidents are committed individually and broadcast as `feed_incident`.

Normalization details:

- **USGS:** Uses the all-day GeoJSON feed. Converts magnitude to severity: `>=6 CRITICAL`, `>=5 HIGH`, `>=4 MODERATE`, otherwise `LOW`; event coordinates are GeoJSON longitude, latitude.
- **EONET:** Uses open events from the preceding 20 days. Maps selected category titles to local hazard types; all imported events receive `MODERATE`.
- **GDACS:** Parses the RSS XML `georss:point` coordinates and infers hazard type from title words; all imported events receive `MODERATE`.
- Unknown categories may map to `other`; EONET/GDACS can map `volcano`, though the propagation algorithm has no volcano-specific parameter set and will use its `other` fallback.

`GET /api/feeds/status` is currently a static stub that reports each feed as unhealthy with no last-success time. It is not wired to the scheduler’s actual health or run history.

## 8. Domain model and relationships

The SQLAlchemy entities are declared under [`backend/app/models/`](backend/app/models/); Pydantic schemas under [`backend/app/schemas/`](backend/app/schemas/). Coordinates use latitude/longitude floats. Status, type, and severity are mostly free-form strings rather than database enums.

| Entity / table | Main data and relationships |
|---|---|
| **Incident** (`incidents`) | Hazard `type`, optional location name, coordinates, severity, description, source, verification flag, status, creation time, acknowledged operator, responding and resolved timestamps. Parent of predictions and alerts; assets can point to an assigned incident. |
| **Alert** (`alerts`) | Alert type/severity/message/status, optional related incident, creation time, acknowledgment operator/time, escalation level. Belongs optionally to an incident. |
| **Asset** (`assets`) | Type, label, coordinates, availability, status, optional incident ID and team ID, update time. Asset-to-incident is an ORM relationship. |
| **Team** (`teams`) | Name/type, member count, specialization, coordinates, availability, and an `assigned_mission_id` integer described as a soft incident reference. |
| **Camp** (`camps`) | Name, coordinates, capacity, current population, status, update time. Owns resources with delete-orphan cascade. |
| **Resource** (`resources`) | Camp ID, resource type, quantity/unit, minimum threshold, update time. Belongs to one camp. |
| **Prediction** (`predictions`) | Incident ID, hazard type, risk tier, GeoJSON stored as text, optional arrival/population/action, generation time, and an estimate marker. Belongs to one incident. |

Incident lifecycle values observed in code are `active`, `responding`, and `resolved`. Alert values include `active`, `acknowledged`, and `resolved`. Asset examples include `idle`, `assigned`, `en_route`, `on_scene`, and `offline`; the code does not enforce a transition graph.

The SQLite DB present in the local workspace contained **882 incidents, 30 alerts, 101 predictions, 1 asset, 1 camp, 0 teams, and 0 resources** at scan time. These are a point-in-time local data snapshot, not guaranteed seed data or production statistics. The saved benchmark report is older (timestamp `2026-10-08`) and reports a different set of counts.

## 9. Intelligence / decision-support behavior

All algorithms below are implemented as deterministic rules or coarse geometric heuristics unless explicitly stated. They should be exposed as decision support, never as guaranteed outcomes.

### 9.1 SOS triage

[`backend/app/intelligence/sos_triage.py`](backend/app/intelligence/sos_triage.py) normalizes report text, tokenizes words, and matches curated high- and moderate-urgency terms:

- Any high-urgency match yields `CRITICAL`.
- Otherwise, one or more moderate terms yields `MODERATE`.
- No matches yields `LOW`.
- A numeric score is computed (high match weight 2, moderate match weight 1), but the classification decision is based on presence of hits rather than score thresholds.
- Location extraction returns up to four words following the first marker among `at`, `near`, `in`, `on`, `beside`, `behind`, and `opposite`.

This is English, exact-token lexicon matching. It does not understand negation, context, misspellings, multilingual reports, or category-specific meaning. The classifier sees the description only; the submitted category and `affected_people` do not influence severity. The extracted candidate location is used as the incident `location_name`; coordinates still come from the form.

### 9.2 Citizen-report correlation

[`backend/app/intelligence/correlation.py`](backend/app/intelligence/correlation.py) looks for at least **3 citizen reports** from the last **2 hours** within a greedy **25 km** cluster. It skips mixed-type clusters and skips clusters if it finds a same-type official-source incident within 50 km and the last six hours. A not-yet-nearby duplicate correlation incident is created with source `correlation`, severity `HIGH`, `verified_flag=False`, and an active `CRITICAL` `emerging_event` alert. A broadcast identifies the emerging cluster.

The grouping is simple seed-based greedy clustering, not a density-based or statistically validated cluster method. The “already exists” check uses a small latitude/longitude bounding box, not a cluster identity. It is invoked after SOS submission. Treat resulting events as leads for human verification, not confirmed disasters.

### 9.3 Impact-zone generation

[`backend/app/intelligence/propagation.py`](backend/app/intelligence/propagation.py) creates four circular GeoJSON polygons, labeled `CORE`, `HIGH`, `MEDIUM`, and `LOW`, using hard-coded radius/velocity pairs by hazard type. It calculates:

- estimated arrival as `radius / velocity` from generation time, except velocities `>=999`, which produce `null`;
- estimated population as circular area × assumed **400 people/km²**;
- recommended action from a partial hazard/tier lookup, falling back to generic SOP text.

The implementation explicitly calls the outputs estimates. These circles are not weather, hydrology, fire-spread, seismic, terrain, or population-model forecasts. Circle geometry is a planar approximation based on latitude/longitude offsets.

### 9.4 Nearest-asset assignment

[`backend/app/intelligence/allocation.py`](backend/app/intelligence/allocation.py) filters available assets to a hazard-to-asset-type compatibility list, computes Haversine distance, then greedily assigns the nearest. It sets the asset unavailable and `assigned`; it does not route around roads, check capacity, dispatch an assigned team, or optimize across simultaneous incidents. The direct assignment endpoint is even simpler and does not check compatibility or asset availability.

### 9.5 Alert escalation

[`backend/app/intelligence/escalation.py`](backend/app/intelligence/escalation.py) checks active `CRITICAL` or `ESCALATED_CRITICAL` alerts every minute. At 5 minutes it sets escalation level 1 and broadcasts; at 15 minutes it sets level 2, changes severity to `ESCALATED_CRITICAL`, and broadcasts. Acknowledging an alert changes its status from `active` to `acknowledged`, taking it out of this candidate query. Age is measured from alert creation time.

### 9.6 Satellite overlay and flood detection

[`backend/app/intelligence/satellite.py`](backend/app/intelligence/satellite.py) obtains and caches a Copernicus OAuth token and declares true-color, NDWI, and NDVI layer metadata. [`backend/app/intelligence/damage_detection.py`](backend/app/intelligence/damage_detection.py) fetches a fixed `0.5° × 0.5°`, `512 × 512` NDWI WMS image around an incident, treats sufficiently saturated blue pixels as water, derives a rectangular polygon around detected water pixels, and estimates affected area/population with a fixed density of 400/km².

This is a rough image-color heuristic; it does not compare pre/post-event imagery or perform a validated damage assessment. Image alpha, resolution, WMS style output, geographic distortion, and scene timing can all affect the result. The front-end selectable `NBR (burn)` mode is mapped to the `NDWI` WMS layer in `SatelliteOverlay.jsx`, so it is not currently a functioning NBR layer. The frontend also fetches `/api/satellite/token`; that endpoint returns the access token as JSON and should be treated as sensitive if satellite integration is enabled.

## 10. HTTP API reference

The router prefixes are in `backend/app/routers/`. Request bodies are validated by Pydantic schemas, including latitude `[-90,90]` and longitude `[-180,180]` where those schemas define coordinates.

| Method and path | Behavior |
|---|---|
| `GET /` | App name, version, and running status. |
| `GET /health`, `GET /api/health` | Basic health response; not a dependency/readiness check. |
| `GET /api/incidents` | List newest first; optional `type`, `severity`, `status`; default limit 500, maximum 2000. |
| `GET /api/incidents/{incident_id}` | Fetch one incident; 404 if missing. |
| `POST /api/incidents` | Create incident directly. |
| `PATCH /api/incidents/{incident_id}` | Update severity, status, verification, description, or acknowledgement name. |
| `POST /api/incidents/{id}/start-response?operator=...` | Set status to responding and set responding time; rejects resolved incidents; default operator is `operator`. |
| `POST /api/incidents/{id}/resolve` | Set resolved status/time and resolve related alerts; broadcasts. |
| `GET /api/alerts?status=active` | List alerts; `status=all` disables filtering. |
| `POST /api/alerts/{id}/acknowledge` | Requires `{"acknowledged_by":"..."}`; only active alerts can be acknowledged; may mark linked incident acknowledged. |
| `POST /api/alerts/{id}/resolve` | Resolve alert and broadcast. |
| `GET /api/assets?availability=true|false` | List/filter assets. |
| `POST /api/assets` | Create asset. |
| `PATCH /api/assets/{id}` | Update location, availability, status, or assignment IDs. |
| `POST /api/assets/{id}/assign?incident_id=...` | Directly assign asset; does not validate incident existence or current availability. |
| `GET /api/teams` / `POST /api/teams` | List/create teams. |
| `POST /api/teams/{id}/assign?incident_id=...` | Set soft mission ID and mark team unavailable. |
| `GET /api/camps` / `POST /api/camps` | List/create camps. |
| `PATCH /api/camps/{id}` | Update capacity, population, or status. |
| `GET /api/camps/{id}/resources` | List camp resources. |
| `POST /api/camps/{id}/resources` | Add camp resource. |
| `PATCH /api/camps/{id}/resources/{resource_id}` | Update quantity/threshold; if quantity is below threshold, creates a `WARNING` low-stock alert. Repeated qualifying updates can create repeated alerts. |
| `GET /api/predictions/{incident_id}` | List generated prediction rows for an incident. |
| `POST /api/predictions/generate?incident_id=...` | Delete old predictions for that incident and store four fresh impact-zone estimates; broadcast. |
| `POST /api/predictions/{incident_id}/auto-assign` | Run nearest-compatible-asset selection; returns an assignment result and broadcasts. |
| `POST /api/sos` | Triage description, create citizen incident and alert, broadcast SOS, run correlation; returns triage summary and incident ID. |
| `GET /api/feeds/status` | Static stub; currently returns all feed health as false. |
| `GET /api/satellite/status` | Reports credential-check result, WMS URL, and layer IDs. |
| `GET /api/satellite/layers` | Descriptive layer metadata. |
| `GET /api/satellite/token` | Returns access token or an error JSON object; used by map overlay. |
| `POST /api/satellite/detect-flood/{incident_id}` | Analyze an incident-area NDWI tile and store a prediction with `AI_DETECTED` marker; 400 if no tile/water detected, 404 if incident absent. |

Most endpoints have no authentication or authorization. This API should not be exposed as an operational service without an explicit security, privacy, reliability, and safety design.

## 11. Real-time event protocol

The backend WebSocket endpoint is `/ws/events`. It accepts a connection and waits for client text frames; broadcasts are JSON objects of this form:

```json
{"type":"sos_created","data":{"incident_id":123}}
```

Events currently emitted include `sos_created`, `emerging_event`, `feed_incident`, `incident_responding`, `incident_resolved`, `alert_acknowledged`, `alert_resolved`, `alert_escalated`, `predictions_generated`, `asset_assigned`, and `flood_detection_complete`. Payload fields depend on the event. Broadcast is process-local and best-effort; a failed WebSocket is removed, but there is no durable event log or replay.

The frontend hook reconnects two seconds after socket close. `MapPage` refreshes incidents/assets for SOS and feed events, refreshes incidents on prediction events, and passes every received message to `AlertPanel`, which refreshes alerts. Some backend mutations (such as generic incident PATCH and direct asset changes) do not broadcast.

## 12. Frontend architecture and user flows

- [`frontend/src/App.jsx`](frontend/src/App.jsx) defines the shared header/navigation and three routes.
- [`frontend/src/pages/MapPage.jsx`](frontend/src/pages/MapPage.jsx) loads incidents/assets, subscribes to WebSocket, and composes the map, layer controls, incident panel, satellite panel, and alert panel.
- [`frontend/src/components/map/MapView.jsx`](frontend/src/components/map/MapView.jsx) starts centered at `[20, 0]`, zoom 3. Basemaps are OSM, Esri imagery, and OpenTopoMap. Selecting an incident focuses the map and loads its prediction polygons.
- [`frontend/src/components/panels/IncidentPanel.jsx`](frontend/src/components/panels/IncidentPanel.jsx) exposes zone generation, auto-assignment, flood analysis for flood incidents, start-response, and resolve actions.
- [`frontend/src/components/panels/AlertPanel.jsx`](frontend/src/components/panels/AlertPanel.jsx) shows active alerts and supports acknowledge/resolve.
- [`frontend/src/components/sos/SOSForm.jsx`](frontend/src/components/sos/SOSForm.jsx) collects SOS data; default coordinates are in Delhi (28.61, 77.20), and browser GPS is optional.
- [`frontend/src/pages/AdminPage.jsx`](frontend/src/pages/AdminPage.jsx) lists assets/camps and creates sample ambulances/camps at randomized coordinates near Delhi. It does not manage teams or resource stock.
- [`frontend/src/store/incidentStore.js`](frontend/src/store/incidentStore.js), `assetStore.js`, and `uiStore.js` hold fetched data and selected display state. There is no persistence layer for browser state.
- [`frontend/src/api/client.js`](frontend/src/api/client.js) uses relative `/api` paths with a 10-second Axios timeout. The WebSocket URL is derived from current page protocol/host.

Map layers include severity/status-styled incident markers, prediction polygons for the selected incident, damage polygons, and asset markers. Correlation-generated incidents pulse red; resolved incidents are greyed; responding incidents receive a blue ring.

### UI files that are present but not currently functional/in use

At scan time, `CampMarkers.jsx`, `DroneMarkers.jsx`, `AssetPanel.jsx`, `CampPanel.jsx`, `AdminDashboard.jsx`, and `frontend/src/utils/constants.js` are empty. Camp and drone marker components are not rendered in `MapView`; the map layer control has incidents/risk zones/assets only. Some files may be planned placeholders, but do not assume their names imply implemented functionality.

## 13. Testing, benchmark, and data notes

No conventional unit/integration test suite or test-runner script appeared in the source inventory. [`backend/benchmark.py`](backend/benchmark.py) is a custom script that calls a **running** API to exercise:

1. 16 hand-curated SOS descriptions and expected triage labels;
2. repeated request latency for five endpoints;
3. one WebSocket event timing;
4. incident distribution by source, severity, and type.

The saved [`backend/benchmark_report.json`](backend/benchmark_report.json) is dated **2026-10-08** and reports `16/16` (`100%`) on that small curated triage set. This is not a general accuracy evaluation, independent holdout, or evidence of model quality. The report also reflects a past database snapshot and should not be conflated with current DB counts.

[`backend/check_db.py`](backend/check_db.py) prints local table counts. `count_corr.py` is an ad hoc query for correlation records. `migrate_response_lifecycle.py` alters an existing SQLite database and is not invoked by the application automatically. No frontend test script is defined in `package.json`.

## 14. Important limitations and implementation caveats

1. **Prototype, not life-safety grade.** No operational guarantees, model validation, human-factors validation, monitoring, failover, or disaster-recovery mechanism is visible.
2. **No authentication/authorization.** Any reachable client can use operator and administrative mutation endpoints.
3. **No proper production deployment configuration** was identified: no Docker/compose, reverse proxy, production CORS profile, CI, or production frontend API configuration in the scanned project.
4. **Database migrations are manual.** `create_all()` does not evolve existing schemas; the one-off lifecycle migration is not a versioned migration framework.
5. **Configuration drift.** Satellite env-example names differ from actual settings; feed polling interval settings do not control polling cadence.
6. **Feed monitoring is misleading/incomplete.** `/api/feeds/status` is static, while real polling logs to stdout. Feed normalization is intentionally simplified; deduplication uses coordinate tolerances, not provider event IDs.
7. **SOS triage is lexical.** It ignores category and affected-person count, can be fooled by negation/context, and only supports English terms.
8. **Geospatial estimates are simplistic.** Fixed radii, circular polygons, static density, and fixed NDWI pixel color thresholds are not validated hazard models.
9. **Response workflow is shallow.** No assignment validation across all routes, road routing, team dispatch, asset release workflow, duplicate incident merge, or reliable event persistence.
10. **Satellite details need attention.** Current front-end “NBR” selection renders NDWI; the token endpoint returns a bearer token to the browser; stored detections represent color-based water extent estimates.
11. **Potential noisy alerts.** Low-stock alerts are generated on every qualifying resource update; no deduplication/suppression is present.
12. **Frontend refresh is event-dependent.** The WebSocket updates selected views, but not every backend mutation emits an event; there is no general polling refresh for incidents/assets.
13. **Error handling is mixed.** Some errors are surfaced in UI, while background feed and satellite paths primarily use `print`; APIs have no unified logging/observability setup.
14. **Schema constraints are partial.** Coordinate ranges are checked in some request schemas; free-form strings and many nonnegative/count constraints are not comprehensively enforced.

When extending this system, preserve the explicit distinction between **reported**, **official-feed imported**, **correlation-emerging/unverified**, **heuristic estimate**, and **satellite-derived estimate** data. Avoid silently turning any of these into “confirmed” facts.

## 15. Useful source-of-truth files

- App/lifecycle: [`backend/app/main.py`](backend/app/main.py), [`backend/app/config.py`](backend/app/config.py), [`backend/app/database.py`](backend/app/database.py)
- Core records and validation: [`backend/app/models/`](backend/app/models/), [`backend/app/schemas/`](backend/app/schemas/)
- API: [`backend/app/routers/`](backend/app/routers/)
- Feeds/scheduler: [`backend/app/feeds/`](backend/app/feeds/)
- Algorithms: [`backend/app/intelligence/`](backend/app/intelligence/)
- Realtime: [`backend/app/realtime/manager.py`](backend/app/realtime/manager.py)
- Frontend entry/routing: [`frontend/src/main.jsx`](frontend/src/main.jsx), [`frontend/src/App.jsx`](frontend/src/App.jsx)
- Map and operational UI: [`frontend/src/pages/MapPage.jsx`](frontend/src/pages/MapPage.jsx), [`frontend/src/components/map/`](frontend/src/components/map/), [`frontend/src/components/panels/`](frontend/src/components/panels/)
- SOS experience: [`frontend/src/pages/SOSPage.jsx`](frontend/src/pages/SOSPage.jsx), [`frontend/src/components/sos/SOSForm.jsx`](frontend/src/components/sos/SOSForm.jsx)
- Dependency manifests: [`backend/requirements.txt`](backend/requirements.txt), [`frontend/package.json`](frontend/package.json)
