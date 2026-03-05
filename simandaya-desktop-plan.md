# Simandaya Desktop - Architecture Plan

## Overview

A Flutter Windows desktop app running on a dedicated gate PC that:
1. Listens to Hikvision RFID reader via ISAPI `alertStream`
2. Shows a popup for the operator to choose: Absen Masuk / Absen Keluar / Izin
3. Stores records locally in SQLite
4. Syncs to the existing FastAPI backend via WebSocket



## Part 1: Backend Changes (FastAPI) — DONE

> Desktop app handles `card_no → user_id` mapping locally. Backend only knows `user_id`.

### 1a. Settings & Auth — DONE

- Added `DESKTOP_API_KEY` to `app/config/settings.py` and `.env.example`
- Added `verify_desktop_api_key` dependency in `app/dependencies.py` (X-API-Key header)

### 1b. DesktopSettings Model — DONE

- `app/models/desktop_settings.py` — singleton row (id=1) with `late_cutoff_time` (default 07:15)
- Registered in `app/config/database.py` `init_db()`

### 1c. DTOs — DONE

- `app/dto/desktop/desktop_request.py` — `AttendanceEventDTO`, `UpdateDesktopSettingsDTO`
- `app/dto/desktop/desktop_response.py` — `StudentSyncDTO`, `AttendanceAckDTO`, `DesktopSettingsDTO`

### 1d. DesktopService — DONE

- `app/services/desktop_service.py`
- `list_students()` — all active siswa with profile info
- `process_attendance_event()` — handles absen_masuk (Hadir/Terlambat based on cutoff), absen_keluar, izin
- `get_settings()` / `update_settings()` — singleton CRUD

### 1e. Desktop Router — DONE

- `app/routers/desktop.py`, registered in `app/main.py`

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/desktop/students` | API Key | Student list for RFID mapping |
| `GET` | `/api/desktop/settings` | API Key | Get late cutoff config |
| `PUT` | `/api/desktop/settings` | JWT (Admin) | Update cutoff time |
| `WS` | `/api/desktop/ws?api_key=<key>` | Query param | Attendance events (bidirectional) |

### WebSocket Protocol

- Desktop sends: `{record_id, user_id, event_type, device_time, reason?}`
- Server replies: `{record_id, status: "ok"|"error", published_at, detail?}`

---

## Part 2: Flutter Desktop App

### Project Structure

```
simandaya_desktop/
├── lib/
│   ├── main.dart
│   ├── config/
│   │   └── app_config.dart           # Hikvision IP/creds, server URL, API key
│   ├── data/
│   │   ├── local/
│   │   │   ├── database.dart         # Drift DB definition
│   │   │   ├── tables/
│   │   │   │   ├── students.dart     # card_no, name, nis, kelas
│   │   │   │   └── tap_records.dart  # local attendance queue
│   │   ├── hikvision/
│   │   │   ├── isapi_client.dart     # Dio + Digest auth
│   │   │   ├── alert_stream.dart     # Long-lived GET /alertStream
│   │   │   └── event_poller.dart     # POST /AcsEvent polling catch-up
│   │   └── remote/
│   │       ├── api_client.dart       # REST calls to FastAPI
│   │       └── ws_sync.dart          # WebSocket sync
│   ├── services/
│   │   ├── hikvision_service.dart    # Stream + polling orchestration
│   │   ├── attendance_service.dart   # Tap -> decision -> save
│   │   └── sync_service.dart         # Background queue -> server
│   ├── ui/
│   │   ├── screens/
│   │   │   ├── dashboard.dart        # Main screen: status + recent events
│   │   │   ├── settings.dart         # Config page
│   │   │   └── tap_popup.dart        # THE popup on RFID tap
│   │   └── widgets/
│   └── providers/                    # Riverpod
├── pubspec.yaml
```

### Key Packages

| Package | Purpose |
|---|---|
| `drift` + `sqlite3_flutter_libs` | Local SQLite |
| `dio` + digest auth | Hikvision ISAPI |
| `web_socket_channel` | Sync to FastAPI |
| `window_manager` | Window control (always-on-top popup) |
| `riverpod` | State management |

---

## Part 3: Core Flows

### 3a. Hikvision alertStream Listener

```
1. Open GET /ISAPI/Event/notification/alertStream (Digest auth, keep-alive)
2. Parse multipart/mixed chunks
3. Filter for AccessControllerEvent with cardNo
4. On event -> trigger tap_popup
5. On disconnect -> reconnect loop (2-3s retry)
6. On reconnect -> poll AcsEvent with beginSerialNo > last known to catch gaps
```

### 3b. Tap Popup Flow

```
1. Lookup card_no in local SQLite -> get student (name, NIS, kelas)
2. Check today's records for this card_no:
   - No record today -> default suggest "Absen Masuk"
   - Has Absen Masuk, no Keluar -> default suggest "Absen Keluar"
   - Otherwise -> no default
3. Show popup: Student info + 3 buttons:
   [Absen Masuk]  [Absen Keluar]  [Izin]
   - If "Izin" selected -> show text field for keterangan
4. Save to local SQLite tap_records
5. Queue for WebSocket sync
```

### 3c. Background Sync

```
1. On startup: connect WebSocket to FastAPI
2. Worker loop: query tap_records WHERE published_at IS NULL
3. Send each record via WebSocket
4. On server ack -> update published_at locally
5. On disconnect -> queue keeps growing, retry connection
6. On reconnect -> flush entire queue
```

### 3d. Student Sync

```
1. On startup: GET /api/desktop/students from FastAPI
2. Upsert into local SQLite students table
3. Periodic refresh (every 30 min or on-demand button)
```

---

## Part 4: Local SQLite Schema

### students

| Column | Type | Notes |
|---|---|---|
| card_no | TEXT | PK |
| user_id | TEXT | UUID from server |
| nama | TEXT | Student name |
| nis | TEXT | Student ID number |
| kelas | TEXT | Class/jurusan |
| synced_at | INTEGER | Epoch timestamp |

### tap_records

| Column | Type | Notes |
|---|---|---|
| id | TEXT | UUID PK |
| card_no | TEXT | RFID card number |
| event_type | TEXT | absen_masuk / absen_keluar / izin |
| device_time | INTEGER | Epoch from Hikvision |
| reason | TEXT | Nullable, for izin keterangan |
| hik_serial_no | INTEGER | Hikvision event serial |
| created_at | INTEGER | Epoch |
| published_at | INTEGER | Nullable, set on server ack |

**Unique constraint:** `(card_no, device_time)` — prevents duplicate events from alertStream + polling overlap

---

## Part 5: Hikvision ISAPI Reference

### Authentication
- HTTP Digest auth
- Credentials: configured in app settings

### Key Endpoints Used

| Endpoint | Method | Purpose |
|---|---|---|
| `/ISAPI/Event/notification/alertStream` | GET | Real-time event stream (primary) |
| `/ISAPI/AccessControl/AcsEvent?format=json` | POST | Poll events by serial number (catch-up) |
| `/ISAPI/System/deviceInfo` | GET | Verify connection to device |
| `/ISAPI/AccessControl/AcsEvent/capabilities?format=json` | GET | Check event capabilities |

### alertStream Response Format

The stream returns `multipart/mixed` with boundary. Each part contains:
- `Content-Type: application/xml` or `application/json`
- `<EventNotificationAlert/>` with event data including `cardNo`, `employeeNo`, timestamp

### AcsEvent Polling (catch-up)

```json
{
  "AcsEventCond": {
    "searchID": "poll",
    "searchResultPosition": 0,
    "maxResults": 30,
    "major": 5,
    "minor": 0,
    "beginSerialNo": LAST_KNOWN + 1
  }
}
```

---

## Part 6: Reliability Design

| Concern | Solution |
|---|---|
| alertStream drops | Auto-reconnect loop (2-3s retry) |
| Missed events during gap | AcsEvent polling catch-up on reconnect |
| Hikvision device reboot | Same reconnect loop handles it |
| App crash | Windows Task Scheduler auto-restart |
| Internet down | Local SQLite queues everything |
| FastAPI server down | WebSocket reconnect + queue flush on recovery |
| Duplicate events | UNIQUE(card_no, device_time) in SQLite |

---

## Part 7: Execution Order

1. ~~**Backend changes**~~ — DONE (Part 1)
2. **Flutter scaffold**: project init, Drift DB, config screen
3. **Hikvision integration**: ISAPI client, alertStream, event poller
4. **UI**: dashboard + tap popup
5. **Sync**: WebSocket client, background queue worker
6. **Hardening**: auto-reconnect, auto-start on boot, error handling

---

## Existing Backend Models (Reference)

### Absensi (absensi table)
- `absensi_id` UUID PK
- `user_id` FK -> users (CASCADE)
- `tanggal` Date
- `time_in` DateTime nullable
- `time_out` DateTime nullable
- `status` Enum: Hadir, Terlambat, Alfa, Sakit, Izin
- `marked_by` FK -> users (SET NULL)
- **UNIQUE:** `(user_id, tanggal)` — one record per student per day

### IzinKeluar (izin_keluar table)
- `izin_id` UUID PK
- `user_id` FK -> users (CASCADE)
- `created_at` DateTime
- `keterangan` String (reason)
- `waktu_kembali` DateTime nullable
- No unique constraint — multiple izin per day allowed

### SiswaProfile (siswa_profiles table)
- `siswa_id` UUID PK
- `user_id` FK -> users (CASCADE)
- `nis` String(50) unique nullable
- `nama_lengkap` String(225)
- `kelas_jurusan` String(100) nullable
- Note: `card_no` mapping lives in desktop app's local SQLite, not on the server
