from pathlib import Path

IGNORED_FOLDERS = {
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    "node_modules",
    "build",
    "dist"
}

IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg",
    ".gif", ".bmp", ".svg", ".webp"
}

IGNORED_SMALLEST_FILES = {
    ".env",
    ".gitkeep",
    "__init__.py"
}


def build_tree(path, prefix=""):
    lines = []

    entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))

    for index, entry in enumerate(entries):

        if entry.name in IGNORED_FOLDERS:
            continue

        connector = "└── " if index == len(entries) - 1 else "├── "

        lines.append(prefix + connector + entry.name)

        if entry.is_dir():
            extension = "    " if index == len(entries) - 1 else "│   "
            lines.extend(build_tree(entry, prefix + extension))

    return lines


def scan_project(project_path):

    statistics = {
        "total_files": 0,
        "total_folders": 0,
        "python_files": 0,
        "html_files": 0,
        "css_files": 0,
        "javascript_files": 0,
        "json_files": 0,
        "markdown_files": 0,
        "image_files": 0,
        "total_lines": 0,
        "largest_file": "",
        "largest_lines": 0,
        "smallest_file": "",
        "smallest_lines": None,
        "readme_exists": False,
        "readme_lines": 0,
        "readme_status": "",

        "gitignore_exists": False,
        "gitignore_entries": 0,

        "requirements_exists": False,
        "package_count": 0,
        "packages": [],
        "files": [],
        "project_tree": []
    }

    root = Path(project_path)

    children = [item for item in root.iterdir()]

    if (
        len(children) == 1
        and children[0].is_dir()
    ):
        root = children[0]

    for item in root.rglob("*"):

        if any(folder in item.parts for folder in IGNORED_FOLDERS):
            continue

        if item.is_dir():
            statistics["total_folders"] += 1
            continue

        statistics["total_files"] += 1

        suffix = item.suffix.lower()

        if suffix == ".py":
            statistics["python_files"] += 1

        elif suffix == ".html":
            statistics["html_files"] += 1

        elif suffix == ".css":
            statistics["css_files"] += 1

        elif suffix == ".js":
            statistics["javascript_files"] += 1

        elif suffix == ".json":
            statistics["json_files"] += 1

        elif suffix == ".md":
            statistics["markdown_files"] += 1

        elif suffix in IMAGE_EXTENSIONS:
            statistics["image_files"] += 1

        try:
            with open(item, "r", encoding="utf-8", errors="ignore") as file:
                line_count = sum(1 for _ in file)
        except Exception:
            line_count = 0

        statistics["total_lines"] += line_count

        relative_name = str(item.relative_to(root))
        statistics["files"].append({
            "name": item.name,
            "path": relative_name,
            "extension": suffix,
            "lines": line_count,
            "size": item.stat().st_size
        })

        if line_count > statistics["largest_lines"]:
            statistics["largest_lines"] = line_count
            statistics["largest_file"] = relative_name

        if (
            line_count > 0
            and item.name not in IGNORED_SMALLEST_FILES
        ):

            if (
                statistics["smallest_lines"] is None
                or line_count < statistics["smallest_lines"]
            ):
                statistics["smallest_lines"] = line_count
                statistics["smallest_file"] = relative_name
    readme = root / "README.md"

    if readme.exists():

        statistics["readme_exists"] = True

        with open(readme, "r", encoding="utf-8", errors="ignore") as file:
            readme_lines = sum(1 for _ in file)

            statistics["readme_lines"] = readme_lines

            if readme_lines == 0:
                statistics["readme_status"] = "Empty"
            elif readme_lines < 15:
                statistics["readme_status"] = "Basic"
            else:
                statistics["readme_status"] = "Good"


    gitignore = root / ".gitignore"

    if gitignore.exists():

        statistics["gitignore_exists"] = True

        with open(gitignore, "r", encoding="utf-8", errors="ignore") as file:

            statistics["gitignore_entries"] = len([
                line
                for line in file
                if line.strip()
                and not line.startswith("#")
            ])


    requirements = root / "requirements.txt"

    if requirements.exists():

        statistics["requirements_exists"] = True

        packages = []

        packages = []

        encodings = [
            "utf-8",
            "utf-8-sig",
            "utf-16",
            "latin-1"
        ]

        for encoding in encodings:

            try:

                with open(
                    requirements,
                    "r",
                    encoding=encoding
                ) as file:

                    packages = []

                    for line in file:

                        line = line.strip()

                        if line:
                            packages.append(line)

                break

            except UnicodeError:

                continue

        packages = [
            package.replace("\x00", "")
            for package in packages
        ]

        statistics["package_count"] = len(packages)
        statistics["packages"] = packages[:10]
        
    statistics["project_tree"] = build_tree(root)

    return statistics