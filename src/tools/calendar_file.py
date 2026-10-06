from pathlib import Path


def load_events(events_file):
    path = Path(events_file)

    if not path.exists():
        return []

    return [line for line in path.read_text().splitlines() if line.strip()]
