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
    - [Example Input File](#example-input-file)
    - [Planned Features](#planned-features)
  - [🇨🇿 Čeština](#-čeština)
    - [Přehled](#přehled)
    - [Funkce](#funkce)
    - [Instalace](#instalace)
    - [Použití](#použití)
    - [Příklad vstupního souboru](#příklad-vstupního-souboru)
    - [Plánované funkce](#plánované-funkce)

---

## 🇬🇧 English

### Overview
**Garmin Batch Uploader & Planner** is a Python CLI tool for power users who want to automate Garmin Connect workout management.  
You can import your training plan from a `.csv` or `.json` file and automatically upload + schedule all workouts at once.

Perfect for coaches, developers, or athletes automating their training pipeline.

### Features
✅ Bulk creation and scheduling of workouts  
✅ CSV / JSON input support  
✅ Login via Garmin Connect (via `python-garminconnect`)  
✅ Modular design — easily extend with new features  
✅ CLI-based workflow with logging and error handling  

### Installation
```bash
git clone https://github.com/stepanhendrych/garmin-batch-uploader-planner
cd garmin-batch-uploader-planner
pip install -r requirements.txt
cp .env.example .env
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

### Example Input File

```csv
date,start_time,title,sport_type,duration_minutes,segments
2026-03-05,18:00,Intervals 6x800,run,60,"[{""type"":""warmup"",""duration"":10},{""type"":""interval"",""reps"":6,""work"":3,""rest"":2}]"
2026-03-06,07:30,Easy Recovery Ride,bike,45,"[]"
```

### Planned Features

* 🕓 Official Garmin Training API support
* 🧠 AI-generated workouts → automatic planning
* ☁️ Cloud / Docker deployment

---

## 🇨🇿 Čeština

### Přehled

**Garmin Batch Uploader & Planner** je Python CLI nástroj, který automatizuje nahrávání a plánování tréninků do Garmin Connect.
Načteš svůj plán z `.csv` nebo `.json` souboru, přihlásíš se jednou a skript ti všechny tréninky nahraje i naplánuje automaticky.

Skvělý pro trenéry, vývojáře nebo sportovce, kteří chtějí mít celý plán pod kontrolou.

### Funkce

✅ Hromadné nahrávání a plánování tréninků
✅ Podpora formátů CSV / JSON
✅ Přihlášení přes Garmin Connect (přes `python-garminconnect`)
✅ Modulární struktura projektu
✅ Logování, ošetření chyb, CLI rozhraní

### Instalace

```bash
git clone https://github.com/<tvoje-jmeno>/garmin-batch-uploader-planner.git
cd garmin-batch-uploader-planner
pip install -r requirements.txt
cp .env.example .env
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

### Příklad vstupního souboru

```csv
date,start_time,title,sport_type,duration_minutes,segments
2026-03-05,18:00,Intervaly 6x800,run,60,"[{""type"":""warmup"",""duration"":10},{""type"":""interval"",""reps"":6,""work"":3,""rest"":2}]"
2026-03-06,07:30,Regenerační jízda,bike,45,"[]"
```

### Plánované funkce

* 🕓 Podpora oficiálního Garmin Training API
* 🧠 AI generování tréninků → automatické plánování
* ☁️ Nasazení do cloudu / Docker image