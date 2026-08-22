import re
from pathlib import Path

from .constants import ShowType

SERIE_REGEX = r"^(?P<name>.+?)[\s._]*[Ss](?P<season>\d+)(?:[Ee](?P<episode>\d+))?"
SERIE_REGEX_FALLBACK = r"^(?P<name>(?:[A-Z][a-z]*\.?)+[A-Z][a-z]*)"

MOVIE_REGEX = r"^(?P<name>.+?)[\s._]*[\[\(]?(?P<year>19\d{2}|20\d{2})[\]\)]?[\s._]"
MOVIE_REGEX_FALLBACK = r"^(?P<name>(?:[A-Z][a-z]*\.?)+[A-Z][a-z]*)"


def _extract_info(filename: str, regex: str, fallback_regex: str) -> dict[str, str]:
    if match := re.search(regex, filename):
        return match.groupdict()
    if fallback_match := re.search(fallback_regex, filename):
        return fallback_match.groupdict()
    return {"name": Path(filename).stem}


def extract_serie_info(filename: str) -> dict[str, str]:
    return _extract_info(filename, SERIE_REGEX, SERIE_REGEX_FALLBACK)


def extract_film_info(filename: str) -> dict[str, str]:
    return _extract_info(filename, MOVIE_REGEX, MOVIE_REGEX_FALLBACK)


def get_relative_directory(filename: str) -> Path:
    serie_info = extract_serie_info(filename)
    serie_name = Path(serie_info["name"])

    if season := serie_info.get("season"):
        return serie_name / f"Saison.{season}"

    return serie_name


def get_media_name(filename: str, type_dl: str) -> str:
    media_data = (
        extract_serie_info(filename=filename)
        if type_dl in [ShowType.SERIES.value, ShowType.ANIMES.value]
        else extract_film_info(filename=filename)
    )

    return media_data["name"]
