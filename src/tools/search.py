def search_items(query, sources):
    query = query.lower().strip()

    if not query:
        return []

    matches = []

    for source_name, items in sources.items():
        for item in items:
            text = _item_text(item)

            if query in text.lower():
                matches.append((source_name, text))

    return matches


def _item_text(item):
    if isinstance(item, dict):
        return " | ".join(str(value) for value in item.values())

    return str(item)
