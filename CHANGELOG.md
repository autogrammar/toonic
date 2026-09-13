## [Unreleased]

## [1.0.19] - 2026-09-13

### Docs
- Update README.md
- Update project/README.md
- Update project/context.md

### Other
- Update .env.example
- Update .gitignore
- Update .planfile/.store.lock
- Update .planfile/config.yaml
- Update .planfile/config.yaml.fast.json
- Update .planfile/events/.logs.dsl.date
- Update .planfile/events/.logs.dsl.v1
- Update .planfile/events/history/logs-2026-09-08.dsl.txt
- Update .planfile/events/logs.dsl.txt
- Update .planfile/events/operations.jsonl
- ... and 20 more files

## [1.0.18] - 2026-06-29

### Docs
- Update README.md

## [1.0.17] - 2026-06-29

### Docs
- Update README.md

### Test
- Update tests/test_watchers.py

### Other
- Update toonic/server/llm/caller.py
- Update uv.lock

## [Unreleased]

### Summary

refactor(docs): code analysis engine

### Docs

- docs: update README
- docs: update context.md

### Other

- scripts: update project.sh
- update project.toon
- update project/analysis.toon
- update project/evolution.toon
- update toonic/cli.py
- update toonic/server/client.py
- update toonic/server/quick.py
- update toonic/server/quick/__init__.py
- update toonic/server/quick/archive.py
- update toonic/server/quick/builder.py
- ... and 3 more


### Summary

feat(docs): deep code analysis engine with 7 supporting modules

### Docs

- docs: update TODO.md

### Other

- update project.toon
- update toonic/server/__main__.py
- update toonic/server/transport/rest_api.py
- update unified_toon.py


### Summary

feat(toonic): CLI interface with 2 supporting modules

### Other

- update toonic/server/transport/rest_api.py


### Summary

feat(tests): configuration management system

### Test

- update tests/conftest.py
- update tests/test_server.py
- update tests/test_triggers.py
- update tests/test_watchers.py

### Build

- update pyproject.toml

### Other

- update project.toon
- update toonic/server/transport/broxeen_bridge.py


### Summary

feat(docs): deep code analysis engine with 7 supporting modules

### Docs

- docs: update cctv-monitoring.md
- docs: update README

### Build

- update pyproject.toml

### Other

- update project.toon
- update toonic/server/core/router.py
- update toonic/server/main.py
- update toonic/server/watchers/stream_watcher.py


### Summary

feat(docs): configuration management system

### Docs

- docs: update README

### Test

- update tests/test_watchers.py

### Build

- update pyproject.toml

### Other

- update docker/Dockerfile.minimal
- update toonic/server/config.py
- update toonic/server/core/router.py
- update toonic/server/main.py
- update toonic/server/models.py
- update toonic/server/transport/broxeen_bridge.py
- update toonic/server/transport/rest_api.py
- update toonic/server/watchers/__init__.py
- update toonic/server/watchers/base.py
- update toonic/server/watchers/database_watcher.py
- ... and 6 more


### Summary

feat(watchers): 6 new data source watchers — HTTP, Process, Directory, Docker, Database, Network monitoring

### Added

**New Watchers (6 types):**
- **HttpWatcher** — monitor websites, APIs, health endpoints: status codes, response times, content changes (hash-based), SSL certificate expiry, keyword detection, redirect chains
- **ProcessWatcher** — monitor system processes (`proc:nginx`), PIDs (`pid:1234`), TCP ports (`port:8080`), TCP endpoints (`tcp:host:5432`), systemd services (`service:postgresql`), with health check URLs
- **DirectoryWatcher** — monitor directory structure changes: new/deleted/moved files, size changes, permission changes, file rename detection, recursive tree scanning with depth limit and ignore patterns
- **DockerWatcher** — monitor Docker containers (`docker:myapp` or `docker:*`): container status, resource usage (CPU/mem), restart detection, image changes, recent error logs
- **DatabaseWatcher** — monitor databases: SQLite natively, PostgreSQL via asyncpg; schema change detection, row count tracking, custom SQL query result diffs, connection health
- **NetworkWatcher** — monitor network connectivity (`net:8.8.8.8,1.1.1.1`): ping latency, DNS resolution changes, TCP port scanning, latency spike detection, packet loss

**New Source Categories:**
- `WEB`, `NETWORK`, `CONTAINER`, `PROCESS` added to SourceCategory enum (14 total)

**Source URL Prefixes:**
- `http://`, `https://` → HttpWatcher
- `proc:`, `pid:`, `port:`, `tcp:`, `service:` → ProcessWatcher
- `dir:` → DirectoryWatcher
- `docker:` → DockerWatcher
- `db:`, `sqlite:`, `database:`, `postgresql://` → DatabaseWatcher
- `net:`, `ping:`, `dns:` → NetworkWatcher

**Tests:**
- 67 new tests for all 6 watchers (227 total, all passing)
- Registry resolution, URL routing, change detection, TOON format output
- Integration tests: SQLite full check cycle, PID monitoring, directory change detection

### Changed

- WatcherRegistry fallback routing updated for all new categories
- SourceConfig category comment updated with new types
- pyproject.toml: added `monitoring` optional dependency group
- Updated README with new watchers in architecture table, CLI examples, roadmap
- Test badge updated: 160 → 227 passed

### Docs

- docs: update README with 6 new watchers, CLI examples, architecture table
- docs: update server.md
- docs: update web-ui.md

### Build

- update pyproject.toml (monitoring extras, Python 3.13 classifier)
- docker: fix libgl1-mesa-glx → libgl1 in Dockerfile and Dockerfile.test


### Summary

feat(triggers): Complete event-driven trigger system with NLP2YAML, 7 detectors, new Web UI, persistent logging

### Added

**Trigger System:**
- Event-driven LLM dispatch: periodic, on_event, hybrid modes
- 7 event detectors: motion, scene_change, object, audio_level, speech, pattern, anomaly
- YAML DSL for declarative trigger rules
- NLP2YAML: natural language → YAML trigger config (local parser + LLM fallback)
- TriggerScheduler with cooldown, fallback, and source filtering
- CLI flags: `--when` (NLP), `--triggers` (YAML file)
- Auto-save generated triggers.yaml to CWD

**Data Directory & Logging:**
- Persistent data directory: `toonic_data/` (configurable via `$TOONIC_DATA_DIR`)
- JSONL logs: `events.jsonl` (all events), `exchanges.jsonl` (LLM actions)
- File logging: `server.log` (console + file)
- SQLite history moved to data directory: `history.db`
- Startup info displays data paths

**Web UI Redesign:**
- New tabbed layout with 6 tabs: Events, LLM Actions, History, Triggers, Sources, Overview
- Live event stream with filtering (all/context/trigger/action/status/error)
- Expandable events and exchanges (click to show full content)
- History browser with NLP query interface
- Trigger rules display with runtime stats (event_count, periodic_count, last_triggered)
- Dark theme with color-coded events

**REST API:**
- `/api/events` — browsable event log with filters
- `/api/triggers` — trigger config + runtime stats
- `/api/data-dir` — list files in data directory
- `/api/history/stats` — history statistics
- `/api/sql` — direct SQL query on history

### Changed

- Updated README.md with trigger system, data directory, new Web UI sections
- Updated docs/server.md with --when, --triggers, data directory, file logging
- Updated docs/web-ui.md with tabbed layout, new endpoints, JavaScript API
- Updated docs/triggers.md (already comprehensive)
- Updated examples/log-monitoring with trigger usage
- Badge: 160 tests passed (was 105)
- Version: 1.0.8

### Files Modified

- `toonic/server/__main__.py` — triggers.yaml saving, file logging setup
- `toonic/server/main.py` — data_dir, event log, JSONL persistence
- `toonic/server/transport/rest_api.py` — complete Web UI rewrite, new endpoints
- `toonic/server/triggers/` — new module: dsl.py, detectors.py, scheduler.py, nlp2yaml.py
- `.gitignore` — added toonic_data/, triggers.yaml
- `README.md`, `docs/server.md`, `docs/web-ui.md` — comprehensive updates

### Tests

- 160 tests passing (was 105)
- New test coverage: triggers DSL, detectors, scheduler, NLP2YAML
- Verified with real RTSP camera + OpenRouter

### Summary

refactor(config): deep code analysis engine with 6 supporting modules

### Build

- update pyproject.toml

### Other

- update .gitignore
- update project.toon
- update toonic/server/__main__.py
- update toonic/server/main.py
- update toonic/server/transport/rest_api.py


### Summary

feat(docs): configuration management system

### Docs

- docs: update README
- docs: update triggers.md
- docs: update README

### Test

- update tests/test_server.py
- update tests/test_triggers.py

### Other

- build: update Makefile
- config: update triggers.yaml
- update project.toon
- update toonic/server/__main__.py
- update toonic/server/main.py
- update toonic/server/transport/rest_api.py
- update toonic/server/triggers/__init__.py
- update toonic/server/triggers/detectors.py
- update toonic/server/triggers/dsl.py
- update toonic/server/triggers/nlp2yaml.py
- ... and 1 more


### Summary

feat(docs): CLI interface improvements

### Docs

- docs: update api.md
- docs: update architecture.md
- docs: update cli.md
- docs: update docker.md
- docs: update history.md
- docs: update plugins.md
- docs: update query.md
- docs: update server.md
- docs: update web-ui.md
- docs: update README
- ... and 1 more

### Test

- update tests/test_server.py

### Other

- build: update Makefile
- docker: update docker-compose.yml
- update toonic/server/client.py
- update toonic/server/config.py
- update toonic/server/core/query.py
- update toonic/server/core/router.py
- update toonic/server/transport/rest_api.py


### Summary

feat(docs): CLI interface improvements

### Docs

- docs: update TODO.md
- docs: update 12-toonic-server-architecture.md
- docs: update README
- docs: update README
- docs: update README
- docs: update README

### Test

- update tests/test_server.py

### Build

- update pyproject.toml

### Other

- update TICKET
- docker: update Dockerfile
- docker: update docker-compose.yml
- update docker/test-data/sample.logfile
- update examples/code-analysis/sample-project/config.py
- update examples/code-analysis/sample-project/main.py
- config: update toonic-server.yaml
- update toonic/server/__init__.py
- update toonic/server/__main__.py
- update toonic/server/client.py
- ... and 13 more


### Summary

feat(tests): CLI interface improvements

### Test

- update tests/__init__.py
- update tests/conftest.py
- update tests/test_cli.py
- update tests/test_core.py
- update tests/test_evidence_graph.py
- update tests/test_handlers.py
- update tests/test_pipeline.py

### Build

- update pyproject.toml

### Config

- config: update goal.yaml

### Other

- update project.toon
- update toonic/__init__.py
- update toonic/__main__.py
- update toonic/cli.py
- update toonic/core/__init__.py
- update toonic/core/base.py
- update toonic/core/detector.py
- update toonic/core/models.py
- update toonic/core/protocols.py
- update toonic/core/registry.py
- ... and 11 more


### Summary

feat(docs): configuration management system

### Docs

- docs: update 08-toonic-multimodal-video.md
- docs: update 09-toonic-audio-vad.md
- docs: update 10-evidence-graph.md
- docs: update 11-videochat-logic.md

### Other

- update TODO/stage_5_video_handler.py
- update TODO/stage_6_audio_handler.py
- update TODO/stage_7_evidence_graph.py


### Summary

refactor(docs): CLI interface improvements

### Docs

- docs: update README
- docs: update TODO.md
- docs: update TOON-SPEC.md
- docs: update 01-code2logic-status.md
- docs: update 02-toonic-vision.md
- docs: update 03-toon-format.md
- docs: update 04-logic2test-status.md
- docs: update 05-logic2code-status.md
- docs: update 06-benchmarks-results.md
- docs: update 07-refactoring-roadmap.md
- ... and 1 more

### Config

- config: update goal.yaml

### Other

- update .gitignore
- update TODO/stage_0_foundation.py
- update TODO/stage_1_document_handlers.py
- update TODO/stage_2_data_config_handlers.py
- update TODO/stage_3_api_infra_handlers.py
- update TODO/stage_4_pipeline_cli.py
- scripts: update project.sh

- feat(toonic): add CLI interface with 2 supporting modules
- feat(docs): add deep code analysis engine with 7 supporting modules
- feat(tests): add configuration management system
- refactor(config): deep code analysis engine with 6 supporting modules
- feat(docs): CLI interface improvements

