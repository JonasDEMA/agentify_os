# 🚀 Nächste Schritte - CPA Scheduler

**Status**: ✅ Projekt-Setup abgeschlossen  
**Nächste Phase**: Phase 1.2 - LAM Protocol Implementation  
**Datum**: 2025-11-03

---

## ✅ Was wurde bereits erledigt?

1. ✅ Vollständige Projekt-Struktur erstellt
2. ✅ Dependencies definiert (`pyproject.toml`)
3. ✅ Docker Setup (Redis, Jaeger, Prometheus, Grafana)
4. ✅ Umfassende Dokumentation:
   - `README.md` - Quick Start Guide
   - `docs/ARCHITECTURE.md` - System-Architektur
   - `docs/TODO.md` - Detaillierter Umsetzungsplan (8 Phasen, ~200 Tasks)
   - `docs/PROJECT_STATUS.md` - Projekt-Status Tracking
   - `docs/PROJECT_STRUCTURE.md` - Verzeichnis-Übersicht & Diagramme
5. ✅ Konfigurationsdateien (`.env.example`, `.gitignore`)
6. ✅ Python Package-Struktur (`__init__.py` Dateien)

---

## 🎯 Sofort zu erledigen (Phase 1.2)

### 1. LAM Protocol Implementation

**Datei**: `scheduler/core/lam_protocol.py`

**Aufgaben**:
- [ ] Pydantic BaseMessage Model erstellen
  - Felder: id, ts, type, sender, to, intent, task, payload, context, correlation, expected, status, security
- [ ] Message Type Enum (request, inform, propose, agree, refuse, confirm, failure, done, discover, offer, assign)
- [ ] Spezialisierte Message Models:
  - [ ] RequestMessage
  - [ ] InformMessage
  - [ ] ProposeMessage, AgreeMessage, RefuseMessage
  - [ ] ConfirmMessage, FailureMessage, DoneMessage
  - [ ] DiscoverMessage, OfferMessage, AssignMessage
- [ ] Validation (Pydantic validators für required fields)
- [ ] Serialization Methods (to_dict, from_dict, to_json, from_json)
- [ ] Message Factory/Builder Pattern

**Test-Datei**: `tests/core/test_lam_protocol.py`

**Tests**:
- [ ] Test Message Creation (alle Typen)
- [ ] Test Required Fields Validation
- [ ] Test Serialization/Deserialization (JSON)
- [ ] Test Invalid Messages (error handling)
- [ ] Test Correlation ID Tracking
- [ ] Test Message Factory

**Geschätzte Zeit**: 4-6 Stunden

---

### 2. ToDo-Schema & Task Graph Implementation

**Datei**: `scheduler/core/task_graph.py`

**Aufgaben**:
- [ ] ToDo Pydantic Model
  - Felder: action, selector, text, timeout, depends_on
- [ ] ActionType Enum (open_app, click, type, wait_for, playwright, uia, send_mail)
- [ ] TaskGraph Class
  - [ ] `add_task(todo: ToDo)` Method
  - [ ] `build_graph()` Method (Dependency Graph erstellen)
  - [ ] `topological_sort()` Method (Dependency Resolution)
  - [ ] `get_parallel_batches()` Method (Parallel Execution Groups)
  - [ ] `detect_cycles()` Method (Zyklus-Erkennung)
  - [ ] `validate()` Method (Graph Validation)

**Datei**: `scheduler/core/task_executor_interface.py`

**Aufgaben**:
- [ ] Abstract BaseExecutor Class
- [ ] `execute(todo: ToDo)` Abstract Method
- [ ] `verify(todo: ToDo)` Abstract Method
- [ ] ExecutionResult Model (success, result, error, duration, screenshot_path)

**Test-Datei**: `tests/core/test_task_graph.py`

**Tests**:
- [ ] Test Sequential Tasks (A → B → C)
- [ ] Test Parallel Tasks (A, B, C gleichzeitig)
- [ ] Test Mixed Dependencies (A → B, A → C, B+C → D)
- [ ] Test Cycle Detection (A → B → C → A sollte Error werfen)
- [ ] Test Empty Graph
- [ ] Test Single Task
- [ ] Test Invalid Dependencies (depends_on non-existent task)

**Geschätzte Zeit**: 6-8 Stunden

---

### 3. Intent Router (Rule-based V1)

**Datei**: `scheduler/core/intent_router.py`

**Aufgaben**:
- [ ] IntentRouter Class
- [ ] `route(message: str)` Method → Intent
- [ ] Regex/Keyword Matching
- [ ] Intent Registry laden (YAML)
- [ ] Fallback Intent ("unknown")
- [ ] Intent Model (Pydantic)
  - Felder: name, patterns, task_template, confidence

**Datei**: `scheduler/config/intents.yaml`

**Aufgaben**:
- [ ] Sample Intents definieren:
  - `send_mail` - "sende mail", "email an", "schreibe an"
  - `search_document` - "finde dokument", "suche datei", "wo ist"
  - `export_pdf` - "exportiere pdf", "speichere als pdf"
  - `open_app` - "öffne", "starte", "launch"
  - `fill_form` - "fülle formular", "trage ein"

**Test-Datei**: `tests/core/test_intent_router.py`

**Tests**:
- [ ] Test Known Intents (verschiedene Patterns)
- [ ] Test Unknown Intent (fallback)
- [ ] Test Case Insensitivity
- [ ] Test Multiple Patterns per Intent
- [ ] Test Intent Confidence Scoring

**Geschätzte Zeit**: 4-5 Stunden

---

## 📦 Dependencies installieren

Bevor du mit der Implementierung startest:

```bash
# Poetry installieren (falls noch nicht vorhanden)
# Windows PowerShell:
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Dependencies installieren
poetry install

# Pre-commit hooks installieren
poetry run pre-commit install

# Redis starten (Docker)
docker-compose up redis -d
```

---

## 🧪 Test-Driven Development (TDD)

**Empfohlener Workflow**:

1. **Test zuerst schreiben** (Red)
   ```bash
   # Test erstellen
   # tests/core/test_lam_protocol.py
   
   def test_create_request_message():
       msg = RequestMessage(
           sender="agent://test",
           to=["agent://worker"],
           intent="test",
           task="Test task"
       )
       assert msg.type == "request"
       assert msg.sender == "agent://test"
   ```

2. **Implementierung** (Green)
   ```bash
   # scheduler/core/lam_protocol.py implementieren
   # bis Test grün wird
   ```

3. **Test ausführen**
   ```bash
   poetry run pytest tests/core/test_lam_protocol.py -v
   ```

4. **Refactoring** (Refactor)
   ```bash
   # Code verbessern, Tests bleiben grün
   ```

5. **Wiederholen** für nächste Funktion

---

## 📊 Definition of Done (DoD)

Eine Aufgabe ist erst "Done", wenn:

- [ ] Code implementiert
- [ ] Unit Tests geschrieben (Coverage > 80%)
- [ ] Tests laufen grün (`pytest`)
- [ ] Linting OK (`ruff check`)
- [ ] Type Checking OK (`mypy`)
- [ ] Dokumentation (Docstrings)
- [ ] Code Review (Self-Review)
- [ ] Commit mit klarer Message
- [ ] TODO.md aktualisiert (Task abgehakt)

---

## 🎯 Ziel für diese Woche

**Bis 2025-11-10**:
- ✅ LAM Protocol vollständig implementiert & getestet
- ✅ Task Graph vollständig implementiert & getestet
- ✅ Intent Router (Rule-based) vollständig implementiert & getestet

**Deliverables**:
- 3 neue Module (`lam_protocol.py`, `task_graph.py`, `intent_router.py`)
- 3 Test-Suites (mit >80% Coverage)
- 1 Config-Datei (`intents.yaml`)
- Aktualisierte Dokumentation

---

## 💡 Tipps

1. **Klein anfangen**: Starte mit dem einfachsten Test
2. **Inkrementell**: Baue Feature für Feature auf
3. **Tests zuerst**: TDD hilft, klare Interfaces zu definieren
4. **Dokumentieren**: Schreibe Docstrings während du codest
5. **Committen**: Kleine, atomare Commits (nicht alles auf einmal)
6. **Fragen**: Bei Unklarheiten → nachfragen!

---

## 📞 Bei Problemen

**Häufige Probleme**:

1. **Poetry Installation schlägt fehl**
   - Lösung: Python 3.11+ installiert? `python --version`

2. **Redis Connection Error**
   - Lösung: `docker-compose up redis -d` ausgeführt?

3. **Import Errors**
   - Lösung: `poetry install` ausgeführt?

4. **Tests finden Module nicht**
   - Lösung: `__init__.py` Dateien vorhanden?

---

## 🚀 Los geht's!

**Nächster Schritt**: LAM Protocol Implementation starten

```bash
# Neuen Branch erstellen
git checkout -b feature/lam-protocol

# Editor öffnen
code scheduler/core/lam_protocol.py

# Test-Datei öffnen
code tests/core/test_lam_protocol.py

# Let's go! 🚀
```

---

**Viel Erfolg!** 💪

Bei Fragen oder Problemen einfach melden. Wir arbeiten das Schritt für Schritt durch!

