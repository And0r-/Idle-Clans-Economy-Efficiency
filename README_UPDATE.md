# API Update Fix - October 2025

## Problem
Nach dem Update der Idle Clans API konnten die Konfigurationsdaten nicht mehr importiert werden. Die API hat zwei wesentliche Änderungen eingeführt:

1. **MongoDB Export Format**: Die API gibt Daten im MongoDB-Format zurück mit `ObjectId("...")` Wrappern, die kein gültiges JSON sind
2. **Neue Datenstruktur**: Die `Tasks` Struktur wurde von einer Liste zu einem Dictionary geändert

## Lösung

### 1. Neues Import-Skript: `fetch_config.py`

Ein neues Python-Skript wurde erstellt, um die aktuellen Spieldaten von der API zu holen:

```bash
python3 fetch_config.py
```

Das Skript:
- Lädt Daten von `https://query.idleclans.com/api/Configuration/game-data`
- Bereinigt das MongoDB-Format (entfernt `ObjectId()` Wrapper und `_id` Felder)
- Erstellt automatisch Backups der alten Konfiguration
- Speichert die neuen Daten in `data/configData.json`

### 2. TaskService Update

Der `TaskService` wurde aktualisiert, um beide API-Strukturen zu unterstützen:

**Alte Struktur** (vor dem Update):
```json
{
  "Tasks": [
    {
      "Key": "Smithing",
      "Tasks": [{"Items": [...]}]
    }
  ]
}
```

**Neue Struktur** (nach dem Update):
```json
{
  "Tasks": {
    "Smithing": [
      {"CustomId": "steel", "Items": [...]},
      {"CustomId": "gold", "Items": [...]}
    ]
  }
}
```

Der Code erkennt automatisch, welche Struktur vorliegt und passt sich an.

## Neue Features

Nach dem Update wurden folgende neue Inhalte hinzugefügt:
- **937 Items** (vorher weniger)
- **337 Tasks** über 15 Kategorien
- **Neue Kategorie**: Carpentry (Zimmerei)

## Verwendung

### Erstmaliges Setup
```bash
# Abhängigkeiten installieren (falls noch nicht geschehen)
pip install -r requirements.txt

# Aktuelle Spieldaten holen
python3 fetch_config.py
```

### Regelmäßige Updates
Um die Daten nach zukünftigen Spiel-Updates zu aktualisieren:
```bash
python3 fetch_config.py
```

### Anwendung starten
```bash
python3 main.py
```

Die Anwendung lädt die Daten automatisch beim Start und aktualisiert sie alle 15 Minuten.

## Technische Details

### API Endpoint
- **URL**: `https://query.idleclans.com/api/Configuration/game-data`
- **Dokumentation**: https://query.idleclans.com/api-docs/index.html

### Dateistruktur
- `data/configData.json` - Aktuelle Spieldaten
- `data/configData.backup.*.json` - Automatische Backups
- `fetch_config.py` - Import-Skript
- `services/task_service.py` - Unterstützt beide API-Strukturen

## Fehlerbehebung

### Problem: "Expecting value" JSON Fehler
**Ursache**: API gibt MongoDB-Format zurück
**Lösung**: Verwenden Sie `fetch_config.py` statt direktem API-Aufruf

### Problem: Keine Tasks werden geladen
**Ursache**: Alte API-Struktur wird erwartet
**Lösung**: Stellen Sie sicher, dass Sie die neueste Version von `task_service.py` verwenden

### Problem: Module not found
**Ursache**: Python-Abhängigkeiten fehlen
**Lösung**:
```bash
pip install -r requirements.txt
```
