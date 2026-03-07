import re
from pathlib import Path

SERIE_REGEX = r"^(?P<name>.+?)[\s._]*[Ss](?P<season>\d+)(?:[Ee](?P<episode>\d+))?"
SERIE_REGEX_FALLBACK = r"^(?P<name>(?:[A-Z][a-z]*\.?)+[A-Z][a-z]*)"


def _extract_serie_info(filename: str) -> dict:
    if match := re.search(SERIE_REGEX, filename):
        return match.groupdict()
    if fallback_match := re.search(SERIE_REGEX_FALLBACK, filename):
        return fallback_match.groupdict()

    return {"name": Path(filename).stem}


def get_relative_directory(filename: str) -> Path:
    serie_info = _extract_serie_info(filename)
    serie_name = Path(serie_info["name"])

    if season := serie_info.get("season"):
        return serie_name / f"Saison.{season}"

    return serie_name
