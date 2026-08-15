def format_size(size_bytes: int) -> str:
    units = ("B", "KB", "MB", "GB", "TB", "PB")
    size = float(size_bytes)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.2f} {units[unit_index]}"
