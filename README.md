# 🎵 Toonic — Universal TOON Format Platform

## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-1.0.19-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$4.95-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-26.6h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $4.9493 (40 commits)
- 👤 **Human dev:** ~$2660 (26.6h @ $100/h, 30min dedup)

Generated on 2026-09-13 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://img.shields.io/badge/tests-227%20passed-brightgreen.svg)](#testing)
[![Version](https://img.shields.io/badge/version-1.0.19-orange.svg)](VERSION)
[![Docker](https://img.shields.io/badge/docker-compose-2496ED.svg)](#docker)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-purple.svg)](https://openrouter.ai)

**Token-Oriented Object Notation** — kompaktowy format reprezentacji plików zoptymalizowany dla LLM.  
Toonic Server dodaje **dwukierunkowe strumieniowanie** danych między źródłami (kod, logi, kamery RTSP) a modelami LLM z pełną historią wymiany danych.

---

## 📑 Spis treści

- [Quick Start](#-quick-start)
- [Architektura](#-architektura)
- [Toonic Server](#-toonic-server)
- [Trigger System](#-trigger-system--event-driven-llm-dispatch)
- [Data Directory](#-data-directory--persistent-logging)
- [CLI Shell](#-cli-shell)
- [Web UI](#-web-ui)
- [Docker](#-docker)
- [RTSP Cameras](#-rtsp-cameras)
- [Conversation History](#-conversation-history)
- [NLP/SQL Query](#-nlpsql-query)
- [LLM Router](#-llm-router)
- [Przykłady](#-przykłady)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Dokumentacja](#-dokumentacja)
- [Roadmap](#-roadmap)

---

# 1. Instalacja
git clone https://github.com/wronai/toonic.git
cd toonic
cp .env.example .env          # ← uzupełnij LLM_API_KEY
make install-all

# 2. Konwersja pliku do TOON
toonic spec ./main.py --format toon

# 5. Monitoring kamery RTSP
make server-camera
```

## 🏗 Architektura

```
Sources (watchers)  →  TOON Pipeline  →  Context Accumulator  →  LLM Router  →  Actions
     ↑                        ↓                (token budget)            ↓
     │                  Trigger Scheduler                               ↓
     │                  (event detectors)                               ↓
     └────────── feedback ←──── History DB ←──── ActionResponse ←────── LLM
                                    ↓
                         NLP/SQL Query ← User
                         Data Directory (JSONL logs)
```

| Komponent | Opis |
|-----------|------|
| **FileWatcher** | Monitoruje katalogi, konwertuje pliki do TOON |
| **LogWatcher** | Tail log files, kategoryzacja ERR/WARN/INFO |
| **StreamWatcher** | RTSP video, scene detection, keyframe extraction |
| **HttpWatcher** | Monitoring stron WWW, API, health endpoints, SSL, content changes |
| **ProcessWatcher** | Monitoring procesów, portów TCP, usług systemowych |
| **DirectoryWatcher** | Detekcja zmian struktury katalogów (nowe/usunięte/przeniesione pliki) |
| **DockerWatcher** | Monitoring kontenerów Docker (status, zasoby, logi) |
| **DatabaseWatcher** | Monitoring baz danych — schema changes, row counts, custom SQL queries |
| **NetworkWatcher** | Monitoring sieci — ping, DNS, TCP ports, latency |
| **TriggerScheduler** | Event-driven dispatch: periodic/on_event/hybrid modes |
| **Event Detectors** | Motion, scene_change, object, pattern, speech, anomaly |
| **Accumulator** | Token budget management per kategoria |
| **LLM Router** | Routing do odpowiedniego modelu (text/code/multimodal) |
| **History DB** | SQLite log wszystkich wymian z LLM |
| **Data Directory** | JSONL logs: events, exchanges, server logs |
| **NLP/SQL Adapter** | Przeszukiwanie historii przez zapytania naturalne |

→ Pełna dokumentacja: [docs/architecture.md](docs/architecture.md)

# Minimalny start
python -m toonic.server --source file:./src/ --goal "analyze code"

# Multi-source z kamerą
python -m toonic.server \
  --source file:./src/ \
  --source log:./logs/app.log \
  --source rtsp://admin:123456@192.168.188.146:554/h264Preview_01_main \
  --goal "code quality + log anomalies + video monitoring" \
  --interval 30

# Monitoring WWW + API
python -m toonic.server \
  --source http://example.com \
  --source http://api.example.com/health \
  --goal "monitor website availability and content changes"

# Monitoring procesów i usług
python -m toonic.server \
  --source proc:nginx \
  --source port:5432 \
  --source service:postgresql \
  --goal "monitor service health"

# Monitoring Docker + baza danych
python -m toonic.server \
  --source docker:* \
  --source db:production.db \
  --goal "monitor containers and database changes"

# Monitoring sieci
python -m toonic.server \
  --source net:8.8.8.8,1.1.1.1 \
  --source tcp:db-server:5432 \
  --goal "network connectivity monitoring"

# Monitoring struktury katalogów
python -m toonic.server \
  --source dir:/var/data/uploads \
  --goal "detect new files and structural changes"

# Z konfiguracją YAML
python -m toonic.server --config toonic-server.yaml
```

→ Dokumentacja: [docs/server.md](docs/server.md)

## ⚡ Trigger System — Event-Driven LLM Dispatch

Zamiast wysyłać dane co N sekund, definiuj **kiedy** dane mają trafić do LLM:

```bash
# NLP: natural language → YAML triggers automatycznie
python -m toonic.server \
  --source "rtsp://admin:123456@192.168.188.146:554/h264Preview_01_main" \
  --goal "describe what you see in each video frame" \
  --when "the object person will be detected if exist min for 1 second, if not send frame min. every 1 minute"
```

```bash
# YAML: plik z regułami triggerów
python -m toonic.server \
  --source "rtsp://cam1:554/stream" \
  --triggers examples/video-captioning/triggers.yaml
```

Wspierane event types:

| Event | Opis | Przykład |
|-------|------|---------|
| `motion` | Ruch w klatce | `--when "when motion detected"` |
| `scene_change` | Duża zmiana sceny | `--when "on scene change"` |
| `object` | Obiekt: osoba, samochód | `--when "person detected for 2s"` |
| `pattern` | Regex w logach | `--when "error occurs 5 times in 60s"` |
| `speech` | Detekcja mowy | `--when "speech detected"` |
| `anomaly` | Odchylenie statystyczne | threshold z-score |

Tryby: **periodic** (co N s), **on_event** (na zdarzenie), **hybrid** (zdarzenie + fallback periodic)

**Generated `triggers.yaml`** zapisywany automatycznie w CWD:
```yaml
triggers:
  - name: object-person-hybrid
    mode: hybrid
    interval_s: 60.0
    source: video
    events:
      - type: object
        threshold: 0.3
        min_duration_s: 1.0
        label: person
    fallback:
      periodic_s: 60.0
    cooldown_s: 1.0
    goal: describe what you see in each video frame
```

→ Dokumentacja: [docs/triggers.md](docs/triggers.md)

## 📁 Data Directory — Persistent Logging

Wszystkie dane serwera zapisywane w `toonic_data/` (lub `$TOONIC_DATA_DIR`):

```bash
toonic_data/
├── events.jsonl          # Wszystkie eventy (context, trigger, action, status)
├── exchanges.jsonl       # LLM exchanges (subset of events)
├── history.db            # SQLite z pełną historią wymian
├── server.log            # Server logs (duplikat konsoli)
└── sources/              # Cached source data
```

**Przykład `events.jsonl`:**
```json
{"event":"context","data":{"source_id":"video:rtsp://...","category":"video","toon_spec":"..."},"timestamp":1772108742.92}
{"event":"trigger","data":{"rule":"object-person-hybrid","reason":"periodic","detections":[]},"timestamp":1772108742.92}
{"event":"action","data":{"action_type":"report","content":"The frame shows...","model_used":"google/gemini-3-flash-preview"},"timestamp":1772108749.22}
```

**Browsing via API:**
```bash
curl http://localhost:8900/api/events?limit=50
curl http://localhost:8900/api/data-dir
```

## 💻 CLI Shell

```bash
python -m toonic.server.client
toonic> status                           # status serwera
toonic> analyze find security issues     # trigger analizy
toonic> add ./new-project/ code          # dodaj źródło
toonic> add rtsp://cam1:554/stream video # dodaj kamerę
toonic> convert ./main.py toon           # konwersja pliku
toonic> history 10                       # ostatnie 10 wymian z LLM
toonic> query "errors from last hour"    # NLP query na historii
toonic> model google/gemini-3-flash-preview  # zmiana modelu
```

→ Dokumentacja: [docs/cli.md](docs/cli.md)

## 🌐 Web UI

Start: `make server` → otwórz http://localhost:8900

**Nowy tabbed layout z 6 zakładkami:**

| Tab | Funkcja |
|-----|---------|
| **Events** | Live event stream (context, trigger, action, error) z filtrowaniem |
| **LLM Actions** | Przeglądarka wymian z LLM (expandable, metadata) |
| **History** | SQLite conversation history + NLP query interface |
| **Triggers** | Trigger rules config + runtime stats |
| **Sources** | Active sources + dynamiczne dodawanie/usuwanie |
| **Overview** | Server stats: chunks, actions, events, tokens, uptime |

**Features:**
- WebSocket live updates
- Event filtering (all/context/trigger/action/status/error)
- Click to expand events/exchanges
- NLP query: `"errors from last hour"` → SQL → results
- Trigger stats: event_count, periodic_count, last_triggered

→ Dokumentacja: [docs/web-ui.md](docs/web-ui.md)

# Pełny stack: RTSP test streams + Toonic Server
cd docker/
cp ../.env.example ../.env    # uzupełnij LLM_API_KEY
docker compose up -d

# Logi
make docker-logs
```

Test streams w Docker:
- `rtsp://localhost:8554/test-cam1` — 640×480 test pattern + audio
- `rtsp://localhost:8554/test-cam2` — 320×240 SMPTE bars
- `rtsp://localhost:8554/test-audio` — audio-only sine wave

→ Dokumentacja: [docs/docker.md](docs/docker.md)

# Real camera
python -m toonic.server \
  --source "rtsp://admin:123456@192.168.188.146:554/h264Preview_01_main" \
  --goal "security monitoring: detect movement" \
  --interval 10

# Multiple cameras
python -m toonic.server \
  --source "rtsp://admin:pass@cam1:554/stream" \
  --source "rtsp://admin:pass@cam2:554/stream" \
  --goal "multi-camera monitoring"
```

StreamWatcher automatycznie:
- Łączy się z RTSP przez OpenCV
- Wykrywa zmiany sceny (scene detection, threshold 0.4)
- Wysyła keyframes jako base64 JPEG (160×120, Q=10, ~2.5kB)
- Bez OpenCV → mock mode do testowania pipeline

## 📜 Conversation History

Każda wymiana z LLM jest zapisywana w SQLite z pełnymi metadanymi:

```python
# Programmatic access
from toonic.server.core.history import ConversationHistory

history = ConversationHistory("./toonic_history.db")
records = history.search(category="video", since="1h")
for r in records:
    print(f"[{r.timestamp}] {r.model} → {r.action_type}: {r.content[:100]}")
```

```bash
# CLI
toonic> history 20                      # last 20 exchanges
toonic> history --category video        # only video-related
toonic> history --model gemini          # only gemini model
toonic> history --action code_fix       # only code fixes
```

→ Dokumentacja: [docs/history.md](docs/history.md)

## 🔍 NLP/SQL Query

Przeszukuj historię wymian z LLM za pomocą zapytań naturalnych lub SQL:

```bash
# NLP queries (przekształcane na SQL przez LLM)
toonic> query "show all errors from the last hour"
toonic> query "which files were fixed today?"
toonic> query "camera events with high confidence"

# Direct SQL
toonic> sql SELECT * FROM exchanges WHERE category='video' ORDER BY timestamp DESC LIMIT 10
```

→ Dokumentacja: [docs/query.md](docs/query.md)

## 🔀 LLM Router

Router automatycznie kieruje zapytania do odpowiedniego modelu:

| Kategoria | Model | Routing |
|-----------|-------|---------|
| code, config, database | `code` model | Gemini / Claude |
| logs, document, data | `text` model | Gemini Flash |
| video, audio | `multimodal` model | Gemini / GPT-4o |

Konfiguracja w `.env`:
```bash
LLM_API_KEY=sk-or-v1-...
LLM_MODEL=google/gemini-3-flash-preview
```

Lub w `toonic-server.yaml`:
```yaml
models:
  text:
    model: google/gemini-3-flash-preview
  code:
    model: google/gemini-3-flash-preview
  multimodal:
    model: google/gemini-3-flash-preview
    supports: [text, image, audio]
```

## 📂 Przykłady

| Przykład | Opis | Start |
|----------|------|-------|
| [code-analysis](examples/code-analysis/) | Analiza kodu, wykrywanie bugów | `make server-code` |
| [log-monitoring](examples/log-monitoring/) | Real-time monitoring logów | `make server-logs` |
| [video-monitoring](examples/video-monitoring/) | RTSP camera monitoring | `make server-camera` |
| [multi-source](examples/multi-source/) | Kod + logi + RTSP combined | `make server-multi` |
| [video-captioning](examples/video-captioning/) | Video captioning z LLM | [README](examples/video-captioning/) |
| [security-audit](examples/security-audit/) | Audyt bezpieczeństwa kodu | [README](examples/security-audit/) |

## 📡 API Reference

| Endpoint | Method | Opis |
|----------|--------|------|
| `/` | GET | Web UI (tabbed layout) |
| `/ws` | WS | WebSocket — live events |
| `/api/status` | GET | Server status + trigger stats |
| `/api/events` | GET | Event log (limit, event_type filter) |
| `/api/triggers` | GET | Trigger config + runtime stats |
| `/api/data-dir` | GET | List files in data directory |
| `/api/actions` | GET | Recent LLM actions |
| `/api/analyze` | POST | Trigger analysis |
| `/api/sources` | POST | Add data source |
| `/api/sources/{id}` | DELETE | Remove source |
| `/api/convert` | POST | Convert file to TOON |
| `/api/formats` | GET | List supported formats |
| `/api/history` | GET | Conversation history (filters: category, model, action_type) |
| `/api/history/stats` | GET | History statistics |
| `/api/query` | POST | NLP query on history |
| `/api/sql` | POST | Direct SQL query on history |

→ Pełna dokumentacja: [docs/api.md](docs/api.md)

## 🧪 Testing

```bash
make test            # All tests (227 passed)
make test-server     # Server tests only
make test-triggers   # Trigger system tests
make test-watchers   # Watcher tests (9 types)
make test-cov        # With coverage report
```

**Test coverage:**
- Core pipeline: 14 file handlers
- Server: watchers (9 types), accumulator, router, history
- Watchers: File, Log, Stream, HTTP, Process, Directory, Docker, Database, Network
- Triggers: DSL, detectors (7 types), scheduler (3 modes), NLP2YAML
- Web UI: REST API, WebSocket, event broadcasting

## 📖 Dokumentacja

- [docs/architecture.md](docs/architecture.md) — Architektura systemu
- [docs/server.md](docs/server.md) — Toonic Server
- [docs/cli.md](docs/cli.md) — CLI Shell
- [docs/web-ui.md](docs/web-ui.md) — Web UI
- [docs/docker.md](docs/docker.md) — Docker setup
- [docs/api.md](docs/api.md) — REST API reference
- [docs/history.md](docs/history.md) — Conversation History
- [docs/query.md](docs/query.md) — NLP/SQL Query
- [docs/triggers.md](docs/triggers.md) — Trigger System (event-driven dispatch)
- [docs/plugins.md](docs/plugins.md) — Plugin system (watchers)
- [TODO/12-toonic-server-architecture.md](TODO/12-toonic-server-architecture.md) — Architecture proposal

## 🗺 Roadmap

- [x] TOON format — 14 file type handlers
- [x] Pipeline — spec / reproduce / batch
- [x] Evidence Graph — cross-reference analysis
- [x] Server — watchers + accumulator + LLM router
- [x] Web UI — real-time events + stats
- [x] Docker — RTSP test streams
- [x] Conversation History — SQLite logging
- [x] NLP/SQL Query — search history
- [x] Trigger System — event-driven LLM dispatch (YAML DSL + NLP2YAML)
- [x] Event Detectors — motion, scene_change, object, pattern, anomaly, speech
- [x] HttpWatcher — website/API monitoring (status, content, SSL, keywords)
- [x] ProcessWatcher — process/port/service monitoring
- [x] DirectoryWatcher — directory structure change detection
- [x] DockerWatcher — container monitoring (status, stats, logs)
- [x] DatabaseWatcher — database monitoring (SQLite, PostgreSQL)
- [x] NetworkWatcher — network monitoring (ping, DNS, TCP ports)
- [ ] gRPC transport (Phase 3)
- [ ] MCP Streamable HTTP bridge
- [ ] Rust port (tonic + prost)
- [ ] Audio VAD watcher (webrtcvad)
- [ ] Git diff watcher
- [ ] Plugin marketplace

## 📄 License

Apache-2.0 — see [LICENSE](LICENSE)

Created by **Tom Sapletta** — [tom@sapletta.com](mailto:tom@sapletta.com)

## License

Licensed under Apache-2.0.
## Author

Tom Sapletta
## Status

_Last updated by [taskill](https://github.com/oqlos/taskill) at 2026-04-25 13:48 UTC_

| Metric | Value |
|---|---|
| HEAD | `191f17d` |
| Coverage | — |
| Failing tests | — |
| Commits in last cycle | 33 |

> Introduced a CLI interface for toonic with supporting modules, added a deep code analysis engine and a configuration management system, and applied related docs/tests improvements and refactors.

<!-- taskill:status:end -->

## Dependency maintenance

See [internal dependency updates](docs/dependencies.md) for daily updates, locked tests and Python support.
