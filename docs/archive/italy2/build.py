from pathlib import Path
import re
import shutil

SOURCE = Path(".")
OUTPUT = Path("site")

INCLUDE_PATTERN = re.compile(
    r'<!--\s*INCLUDE:\s*([^>]+?)\s*-->'
)


def process_file(path, stack=None):
    if stack is None:
        stack = []

    if path in stack:
        chain = " -> ".join(str(p) for p in stack + [path])
        raise RuntimeError(f"Circular include detected: {chain}")

    text = path.read_text(encoding="utf-8")

    def replace_include(match):
        include_name = match.group(1).strip()
        include_path = SOURCE / include_name

        if not include_path.exists():
            raise FileNotFoundError(
                f"Include not found: {include_path}"
            )

        return process_file(include_path, stack + [path])

    return INCLUDE_PATTERN.sub(replace_include, text)


def main():
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)

    OUTPUT.mkdir(parents=True)

    for source_file in SOURCE.rglob("*"):
        if source_file.is_dir():
            continue

        relative = source_file.relative_to(SOURCE)
        destination = OUTPUT / relative

        # HTML files get their INCLUDE statements processed.
        if source_file.suffix.lower() in (".html", ".htm"):
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                process_file(source_file),
                encoding="utf-8"
            )

        # Everything else is copied unchanged.
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, destination)

    print(f"Built website in {OUTPUT}/")


if __name__ == "__main__":
    main()
    