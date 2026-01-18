import re
from pathlib import Path

SERIE_REGEX = r"^(?P<name>.+?)[\s._]*[Ss](?P<season>\d+)(?:[Ee](?P<episode>\d+))?"


def _extract_serie_info(filename: str) -> dict | None:
    if not (match := re.search(SERIE_REGEX, filename)):
        return None

    return match.groupdict()


def get_relative_directory(filename: str) -> Path | None:
    if not (serie_info := _extract_serie_info(filename)):
        return None

    serie_name = Path(serie_info["name"])

    return serie_name / f"Saison.{serie_info.get('season', '1')}"
