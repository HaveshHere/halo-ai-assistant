from pathlib import Path


def load_notes(notes_file):
    path = Path(notes_file)

    if not path.exists():
        return []

    return [line for line in path.read_text().splitlines() if line.strip()]


def add_note(notes_file, note):
    path = Path(notes_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a") as file:
        file.write(note.strip() + "\n")

    return note.strip()
