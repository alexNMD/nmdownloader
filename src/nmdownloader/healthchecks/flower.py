import requests


def main() -> None:
    requests.get("http://localhost:5555/api/workers").raise_for_status()


if __name__ == "__main__":
    main()
