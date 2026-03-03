from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    garmin_user: str
    garmin_pass: str
    tokenstore: str


def load_settings() -> Settings:
    load_dotenv()

    garmin_user = os.getenv("GARMIN_USER", "").strip()
    garmin_pass = os.getenv("GARMIN_PASS", "").strip()
    tokenstore = os.getenv("GARMIN_TOKENSTORE", "~/.garminconnect").strip()

    if not garmin_user or not garmin_pass:
        raise ValueError("Missing GARMIN_USER or GARMIN_PASS in environment (.env).")

    return Settings(
        garmin_user=garmin_user,
        garmin_pass=garmin_pass,
        tokenstore=tokenstore,
    )
