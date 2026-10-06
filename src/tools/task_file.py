from pathlib import Path


def load_tasks(tasks_file):
    path = Path(tasks_file)

    if not path.exists():
        return []

    return [line for line in path.read_text().splitlines() if line.strip()]


def complete_task(tasks_file, completed_file, task_number):
    tasks_path = Path(tasks_file)
    completed_path = Path(completed_file)
    tasks = load_tasks(tasks_path)

    if task_number < 1 or task_number > len(tasks):
        return None

    completed_task = tasks.pop(task_number - 1)

    tasks_path.write_text("\n".join(tasks) + ("\n" if tasks else ""))
    completed_path.parent.mkdir(parents=True, exist_ok=True)

    with completed_path.open("a") as file:
        file.write(completed_task + "\n")

    return completed_task