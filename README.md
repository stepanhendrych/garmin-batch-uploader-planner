# 🏃‍♂️ Garmin Batch Uploader & Planner

Automate bulk upload and scheduling of workouts to Garmin Connect using Python.  
Import your entire training plan (CSV / JSON), authenticate once, and push workouts directly into your Garmin calendar — fully automated and ready to sync.

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
    - [Example Input File](#example-input-file)
    - [Planned Features](#planned-features)
  - [🇨🇿 Čeština](#-čeština)
    - [Funkce](#funkce)
    - [Instalace](#instalace)
    - [Použití](#použití)
    - [Dvoufázové ověření (MFA / 2FA)](#dvoufázové-ověření-mfa--2fa)
    - [Příklad vstupního souboru](#příklad-vstupního-souboru)
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

2. Prepare your `workouts.csv` file (see example below).

3. Run the script:

   ```bash
   python cli.py --file workouts.csv
   ```

   or, for JSON input:

   ```bash
   python cli.py --file workouts.json
   ```

4. Recommended first run:

   ```bash
   python cli.py --file workouts.csv --dry-run --verbose
   ```

### Multi-Factor Authentication (MFA / 2FA)

If your Garmin account has 2FA enabled, the script will automatically prompt for your MFA code during the first login:

```bash
python cli.py --file workouts.csv
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

### Example Input File

```csv
date,start_time,title,sport_type,duration_minutes,segments
2026-03-05,18:00,Intervals 6x800,run,60,"[{""type"":""warmup"",""duration"":10},{""type"":""interval"",""reps"":6,""work"":3,""rest"":2}]"
2026-03-06,07:30,Easy Recovery Ride,bike,45,"[]"
```

### Planned Features

* 🕓 Official Garmin Training API support
* ✅/🔜 Duplicate protection (skip already existing workouts by name/date)
* 🧠 AI-generated workouts → automtic planning
* ☁️ Cloud / Docker deployment

---

## 🇨🇿 Čeština

z### Přehled

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

2. Připrav `workouts.csv` (viz níže).

3. Spusť skript:

   ```bash
   python cli.py --file workouts.csv
   ```

   nebo pro JSON vstup:

   ```bash
   python cli.py --file workouts.json
   ```

4. Doporučené první spuštění:

   ```bash
   python cli.py --file workouts.csv --dry-run --verbose
   ```

### Dvoufázové ověření (MFA / 2FA)

Pokud máš na Garmin účtu zapnuté 2FA, skript tě automaticky vyzve k zadání ověřovacího kódu během prvního přihlášení:

```bash
python cli.py --file workouts.csv
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

### Příklad vstupního souboru

```csv
date,start_time,title,sport_type,duration_minutes,segments
2026-03-05,18:00,Intervaly 6x800,run,60,"[{""type"":""warmup"",""duration"":10},{""type"":""interval"",""reps"":6,""work"":3,""rest"":2}]"
2026-03-06,07:30,Regenerační jízda,bike,45,"[]"
```

### Plánované funkce

* 🕓 Podpora oficiálního Garmin Training API
* ✅/🔜 Ochrana proti duplicitám (přeskočení již existujících tréninků podle názvu/data)
* 🧠 AI generování tréninků → automatické plánování
* ☁️ Nasazení do cloudu / Docker image