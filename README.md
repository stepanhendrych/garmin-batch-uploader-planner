# 🏃‍♂️ Garmin Batch Uploader & Planner

Automate bulk upload of workouts to Garmin Connect using Python.  
Import your entire training plan (CSV / JSON), authenticate once, and push workouts directly into your Garmin workout library.

---

## 📑 Table of Contents
- [🏃‍♂️ Garmin Batch Uploader \& Planner](#️-garmin-batch-uploader--planner)
  - [📑 Table of Contents](#-table-of-contents)
  - [🇬🇧 English](#-english)
    - [Overview](#overview)
    - [Features](#features)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Multi-Factor Authentication (MFA / 2FA)](#multi-factor-authentication-mfa--2fa)
    - [Workout File Format (JSON / CSV)](#workout-file-format-json--csv)
      - [JSON Format (Recommended)](#json-format-recommended)
      - [Segment Types](#segment-types)
      - [Duration / End Condition Options](#duration--end-condition-options)
      - [Repeat / Cycle Groups](#repeat--cycle-groups)
      - [Target Types](#target-types)
      - [CSV Format (Alternative)](#csv-format-alternative)
    - [Planned Features](#planned-features)
  - [🇨🇿 Čeština](#-čeština)
    - [Přehled](#přehled)
    - [Funkce](#funkce)
    - [Instalace](#instalace)
    - [Použití](#použití)
    - [Dvoufázové ověření (MFA / 2FA)](#dvoufázové-ověření-mfa--2fa)
    - [Formát vstupního souboru (JSON / CSV)](#formát-vstupního-souboru-json--csv)
      - [JSON formát (doporučeno)](#json-formát-doporučeno)
      - [Typy segmentů](#typy-segmentů)
      - [Možnosti ukončení segmentu / End condition](#možnosti-ukončení-segmentu--end-condition)
      - [Opakující se skupiny / Cykly](#opakující-se-skupiny--cykly)
      - [Typy cílů](#typy-cílů)
      - [CSV formát (Alternativa)](#csv-formát-alternativa)
    - [Plánované funkce](#plánované-funkce)

---

## 🇬🇧 English

### Overview
**Garmin Batch Uploader & Planner** is a Python CLI tool for power users who want to automate Garmin Connect workout management.  
You can import your training plan from a `.csv` or `.json` file and automatically upload all workouts to your Garmin Connect library.

**Note:** Workout scheduling (assigning workouts to specific calendar dates) must be done manually in the Garmin Connect web/mobile app, as this functionality is not available via API.

Perfect for coaches, developers, or athletes automating their training pipeline.

### Features
✅ Bulk creation of workouts in Garmin Connect library  
✅ CSV / JSON input support  
✅ Login via Garmin Connect (via `python-garminconnect`)  
✅ **Multi-Factor Authentication (MFA/2FA) support with token persistence**  
✅ Modular design — easily extend with new features  
✅ CLI-based workflow with logging and error handling  
✅ Safe `--dry-run` mode for validation before real upload  
⚠️ Calendar scheduling done manually in Garmin Connect UI (API limitation)  

### Installation
```bash
git clone https://github.com/stepanhendrych/garmin-batch-uploader-planner
cd garmin-batch-uploader-planner
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
```

### Usage

1. Fill in your `.env` file with Garmin credentials:

   ```env
   GARMIN_USER=your.email@example.com
   GARMIN_PASS=your_password
   ```

2. Prepare your `workouts.json` file (see example below).

3. Run the script:


   ```bash
   python cli.py --file workouts.json
   ```

4. Recommended first run:

   ```bash
   python cli.py --file workouts.json --dry-run --verbose
   ```

### Multi-Factor Authentication (MFA / 2FA)

If your Garmin account has 2FA enabled, the script will automatically prompt for your MFA code during the first login:

```bash
python cli.py --file workouts.json
# Will prompt: "Enter your MFA code: "
```

After successful authentication, session tokens are saved to `~/.garminconnect` (or the path in `GARMIN_TOKENSTORE`). Future runs will use these tokens automatically — **no password or MFA needed again** (tokens are valid for ~1 year).

**To customize token storage location:**

```env
GARMIN_TOKENSTORE=C:\Users\YourName\.garmin_tokens
```

**Security tip:** Ensure restrictive permissions on the token directory:

```bash
# Linux/macOS
chmod 700 ~/.garminconnect
chmod 600 ~/.garminconnect/*
```

### Workout File Format (JSON / CSV)

The tool supports both **JSON** and **CSV** input formats. JSON is recommended for complex workouts with targets, repeats, and various end conditions.

#### JSON Format (Recommended)

```json
[
  {
    "start_time": "2026-03-10T18:00:00Z",
    "title": "Easy Steady Run",
    "sport_type": "running",
    "duration_minutes": 42,
    "description": "Comfortable pace run",
    "segments": [
      {
        "type": "warmup",
        "duration": 7
      },
      {
        "type": "steady",
        "duration": 28,
        "target": {
          "type": "heart.rate.zone",
          "zoneNumber": 2
        }
      },
      {
        "type": "cooldown",
        "duration": 7
      }
    ]
  },
  {
    "start_time": "2026-03-12T18:00:00Z",
    "title": "Repeating Intervals",
    "sport_type": "running",
    "duration_minutes": 45,
    "segments": [
      {
        "type": "warmup",
        "duration": 10
      },
      {
        "type": "repeat",
        "reps": 5,
        "description": "5x (2min hard + 2min recovery)",
        "segments": [
          {
            "type": "interval",
            "work": 2,
            "target": {"type": "heart.rate.zone", "zoneNumber": 4}
          },
          {
            "type": "recovery",
            "rest": 2
          }
        ]
      },
      {
        "type": "cooldown",
        "duration": 5
      }
    ]
  }
]
```

#### Segment Types

- `warmup` — Easy effort to start *(can use duration)*
- `steady` — Constant moderate effort *(can use duration; uploaded as Garmin `interval` step type for API compatibility)*
- `cooldown` — Easy effort to finish *(can use duration)*
- `interval` — Hard effort *(can use work duration or end condition)*
- `recovery` — Easy recovery *(can use rest duration or end condition)*
- `other` — Custom segment type *(can use duration)*
- `repeat` — Repeating cycle of nested segments *(requires reps and nested segments)*

#### Duration / End Condition Options

**Time-based (default):**
```json
{
  "type": "interval",
  "duration": 3,
  "description": "3 minutes hard"
}
```

**Distance-based:**
```json
{
  "type": "interval",
  "description": "400m sprint",
  "end_condition": {
    "type": "distance",
    "value": 0.4,
    "unit": "km"
  }
}
```

**Calorie-based:**
```json
{
  "type": "interval",
  "description": "Burn 100 calories",
  "end_condition": {
    "type": "calories",
    "value": 100
  }
}
```

**Heart Rate-based (less than):**
```json
{
  "type": "recovery",
  "description": "Recover until HR drops to 120 bpm",
  "end_condition": {
    "type": "heart.rate",
    "value": 120,
    "operator": "lt",
    "unit": "bpm"
  }
}
```

**Heart Rate-based (greater than):**
```json
{
  "type": "interval",
  "description": "Continue until HR reaches 160 bpm",
  "end_condition": {
    "type": "heart.rate",
    "value": 160,
    "operator": "gt",
    "unit": "bpm"
  }
}
```

**Manual LAP button:**
```json
{
  "type": "recovery",
  "description": "Easy jog - press LAP when ready",
  "end_condition": {
    "type": "lap.button",
    "value": 1
  }
}
```

#### Repeat / Cycle Groups

Create repeating structures with nested segments:

```json
{
  "type": "repeat",
  "reps": 3,
  "description": "3 rounds of: hard + recovery",
  "segments": [
    {
      "type": "interval",
      "work": 3,
      "description": "Hard 3min"
    },
    {
      "type": "recovery",
      "rest": 2,
      "description": "Easy 2min recovery"
    }
  ]
}
```

Uploads as a single Garmin `RepeatGroupDTO` step with nested `workoutSteps` (not expanded into repeated top-level steps).

#### Target Types

**Heart Rate Zones (1-5):**
```json
"target": {
  "type": "heart.rate.zone",
  "zoneNumber": 3
}
```

**Pace Range (min/km):**
```json
"target": {
  "type": "pace.zone",
  "valueOne": 4.5,
  "valueTwo": 5.0
}
```

**Cadence (steps/min or rpm):**
```json
"target": {
  "type": "cadence",
  "valueOne": 175,
  "valueTwo": 185
}
```

#### CSV Format (Alternative)

If you prefer CSV, segments must be JSON-encoded:

```csv
start_time,title,sport_type,duration_minutes,description,segments
2026-03-10T18:00:00Z,Easy Run,running,42,"Base building","[{\"type\":\"warmup\",\"duration\":7},{\"type\":\"steady\",\"duration\":28}]"
```

**⚠️ Note:** CSV segment encoding is complex. **Use JSON format** for better readability and full feature support.

### Planned Features

* 🕓 Official Garmin Training API support
* ✅/🔜 Duplicate protection (skip already existing workouts by name/date)
* 🧠 AI-generated workouts → automtic planning
* ☁️ Cloud / Docker deployment

---

## 🇨🇿 Čeština

### Přehled

**Garmin Batch Uploader & Planner** je Python CLI nástroj, který automatizuje nahrávání tréninků do Garmin Connect.
Načteš svůj plán z `.csv` nebo `.json` souboru, přihlásíš se jednou a skript ti všechny tréninky nahraje automaticky do knihovny.

**Poznámka:** Plánování tréninků (přiřazení na konkrétní datum v kalendáři) se musí udělat ručně v Garmin Connect web/mobilní aplikaci, protože tato funkce není dostupná přes API.

Skvělý pro trenéry, vývojáře nebo sportovce, kteří chtějí mít celý plán pod kontrolou.

### Funkce

✅ Hromadné nahrávání tréninků do knihovny Garmin Connect  
✅ Podpora formátů CSV / JSON  
✅ Přihlášení přes Garmin Connect (přes `python-garminconnect`)  
✅ **Podpora dvoufázového ověření (MFA/2FA) s trvalými tokeny**  
✅ Modulární struktura projektu  
✅ Logování, ošetření chyb, CLI rozhraní  
✅ Bezpečný `--dry-run` režim před ostrým nahráním  
⚠️ Plánování do kalendáře se dělá ručně v Garmin Connect UI (omezení API)

### Instalace

```bash
git clone https://github.com/<tvoje-jmeno>/garmin-batch-uploader-planner.git
cd garmin-batch-uploader-planner
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
```

### Použití

1. Vyplň `.env` soubor svými Garmin údaji:

   ```env
   GARMIN_USER=tvuj.email@example.com
   GARMIN_PASS=tvé_heslo
   ```

2. Připrav `workouts.json` (viz níže).

3. Spusť skript:

   ```bash
   python cli.py --file workouts.json
   ```

4. Doporučené první spuštění:

   ```bash
   python cli.py --file workouts.json --dry-run --verbose
   ```



### Dvoufázové ověření (MFA / 2FA)

Pokud máš na Garmin účtu zapnuté 2FA, skript tě automaticky vyzve k zadání ověřovacího kódu během prvního přihlášení:

```bash
python cli.py --file workouts.json
# Zobrazí se: "Enter your MFA code: "
```

Po úspěšné autentizaci se session tokeny uloží do `~/.garminconnect` (nebo cesty v `GARMIN_TOKENSTORE`). Další spuštění už budou používat tyto tokeny automaticky — **nepotřebuješ už heslo ani MFA** (tokeny jsou platné ~1 rok).

**Vlastní umístění tokenů:**

```env
GARMIN_TOKENSTORE=C:\Users\TvojeJmeno\.garmin_tokens
```

**Bezpečnostní tip:** Nastav restriktivní oprávnění na adresář s tokeny:

```bash
# Linux/macOS
chmod 700 ~/.garminconnect
chmod 600 ~/.garminconnect/*
```

### Formát vstupního souboru (JSON / CSV)

Nástroj podporuje formáty **JSON** i **CSV**. JSON je doporučen pro komplexnější tréninky s cíly, opakovacími skupinami a různými podmínkami ukončení.

#### JSON formát (doporučeno)

```json
[
  {
    "start_time": "2026-03-10T18:00:00Z",
    "title": "Klidný běh - 6 km",
    "sport_type": "running",
    "duration_minutes": 42,
    "segments": [
      {
        "type": "warmup",
        "duration": 7
      },
      {
        "type": "steady",
        "duration": 28,
        "target": {
          "type": "heart.rate.zone",
          "zoneNumber": 2
        }
      },
      {
        "type": "cooldown",
        "duration": 7
      }
    ]
  },
  {
    "start_time": "2026-03-12T18:00:00Z",
    "title": "Intervaly - 5x (tvrdě + obnova)",
    "sport_type": "running",
    "duration_minutes": 45,
    "segments": [
      {
        "type": "warmup",
        "duration": 10
      },
      {
        "type": "repeat",
        "reps": 5,
        "segments": [
          {
            "type": "interval",
            "work": 2,
            "target": {"type": "heart.rate.zone", "zoneNumber": 4}
          },
          {
            "type": "recovery",
            "rest": 2
          }
        ]
      },
      {
        "type": "cooldown",
        "duration": 5
      }
    ]
  }
]
```

#### Typy segmentů

- `warmup` — Lehký úsek na začátek *(lze duration)*
- `steady` — Stabilní úsek *(lze duration; kvůli kompatibilitě API se nahrává jako Garmin `interval` step type)*  
- `cooldown` — Lehký úsek na konec *(lze duration)*
- `interval` — Tvrdý úsek *(lze work nebo end_condition)*
- `recovery` — Zotavovací úsek *(lze rest nebo end_condition)*
- `other` — Vlastní typ *(lze duration)*
- `repeat` — Cyklus s vnořenými segmenty *(vyžaduje reps a segments)*

#### Možnosti ukončení segmentu / End condition

**Časové (výchozí):**
```json
{"type": "interval", "duration": 3}
```

**Vzdálenost:**
```json
{"type": "interval", "end_condition": {"type": "distance", "value": 0.4, "unit": "km"}}
```

**Kalorie:**
```json
{"type": "interval", "end_condition": {"type": "calories", "value": 100}}
```

**Srdeční tep (méně než):**
```json
{"type": "recovery", "end_condition": {"type": "heart.rate", "value": 120, "operator": "lt", "unit": "bpm"}}
```

**Srdeční tep (více než):**
```json
{"type": "interval", "end_condition": {"type": "heart.rate", "value": 160, "operator": "gt", "unit": "bpm"}}
```

**Stisk LAP:**
```json
{"type": "recovery", "end_condition": {"type": "lap.button", "value": 1}}
```

#### Opakující se skupiny / Cykly

```json
{
  "type": "repeat",
  "reps": 3,
  "segments": [
    {"type": "interval", "work": 3},
    {"type": "recovery", "rest": 2}
  ]
}
```

Nahrává se jako jeden Garmin `RepeatGroupDTO` krok s vnořenými `workoutSteps` (neexpanduje se na opakované vrchní/top-level kroky).

#### Typy cílů

**Srdeční frekvence - Zóny:**
```json
"target": {"type": "heart.rate.zone", "zoneNumber": 3}
```

**Tempo - Rozsah:**
```json
"target": {"type": "pace.zone", "valueOne": 4.5, "valueTwo": 5.0}
```

**Kadence:**
```json
"target": {"type": "cadence", "valueOne": 175, "valueTwo": 185}
```

#### CSV formát (Alternativa)

```csv
start_time,title,sport_type,duration_minutes,segments
2026-03-10T18:00:00Z,Run,running,42,"[{\"type\":\"warmup\",\"duration\":7}]"
```

**⚠️ Poznámka:** **Použij JSON formát** pro plnou podporu všech funkcí.

### Plánované funkce

* 🕓 Podpora oficiálního Garmin Training API
* ✅/🔜 Ochrana proti duplicitám (přeskočení již existujících tréninků podle názvu/data)
* 🧠 AI generování tréninků → automatické plánování
* ☁️ Nasazení do cloudu / Docker image