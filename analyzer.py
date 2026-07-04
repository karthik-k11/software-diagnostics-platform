from pathlib import Path
import ast
import re

from score_engine import calculate_health

LARGE_FILE_THRESHOLD = 500
LONG_FUNCTION_THRESHOLD = 40
LONG_CLASS_THRESHOLD = 150

IGNORED_FOLDERS = {
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    "node_modules",
    "build",
    "dist"
}

IGNORED_EMPTY_FILES = {
    ".gitkeep"
}

COMMENT_TAGS = ("TODO", "FIXME", "HACK", "NOTE")

SECRET_PATTERNS = [
    ("API Key", re.compile(r"api[_-]?key\s*=", re.IGNORECASE)),
    ("Secret Key", re.compile(r"secret[_-]?key\s*=", re.IGNORECASE)),
    ("Password", re.compile(r"password\s*=", re.IGNORECASE)),
    ("Token", re.compile(r"token\s*=", re.IGNORECASE)),
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
]


def analyze_project(project_path, statistics):

    results = {
        "empty_files": [],
        "empty_folders": [],
        "large_files": [],
        "long_functions": [],
        "long_classes": [],
        "duplicate_filenames": [],
        "todos": [],
        "fixmes": [],
        "hacks": [],
        "notes": [],
        "secrets": [],

        "standard_imports": {},
        "third_party_imports": {},
        "total_imports": 0,

        "health": {},
        "suggestions": []
    }

    root = Path(project_path)

    children = [item for item in root.iterdir()]

    if len(children) == 1 and children[0].is_dir():
        root = children[0]

    filename_count = {}

    for file in statistics["files"]:

        filename_count[file["name"]] = filename_count.get(file["name"], 0) + 1

        if (
            file["lines"] == 0
            and file["name"] not in IGNORED_EMPTY_FILES
        ):
            results["empty_files"].append(file["path"])

        if file["lines"] >= LARGE_FILE_THRESHOLD:
            results["large_files"].append({
                "path": file["path"],
                "lines": file["lines"]
            })

    for name, count in filename_count.items():
        if count > 1:
            results["duplicate_filenames"].append(name)

    for folder in root.rglob("*"):

        if any(part in IGNORED_FOLDERS for part in folder.parts):
            continue

        if folder.is_dir() and not any(folder.iterdir()):
            results["empty_folders"].append(
                str(folder.relative_to(root))
            )

    for py_file in root.rglob("*.py"):

        if any(part in IGNORED_FOLDERS for part in py_file.parts):
            continue

        try:

            source = py_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            lines = source.splitlines()

            tree = ast.parse(source)
            
            for node in ast.walk(tree):

                module_name = None

                if isinstance(node, ast.Import):

                    for alias in node.names:

                        module_name = alias.name.split(".")[0]

                        results["total_imports"] += 1

                        if module_name in {
                            "os", "sys", "json", "re",
                            "pathlib", "collections",
                            "hashlib", "zipfile",
                            "ast", "tokenize"
                        }:

                            results["standard_imports"][module_name] = (
                                results["standard_imports"].get(module_name, 0) + 1
                            )

                        else:

                            results["third_party_imports"][module_name] = (
                                results["third_party_imports"].get(module_name, 0) + 1
                            )           

                elif isinstance(node, ast.ImportFrom):

                    if node.module:

                        module_name = node.module.split(".")[0]

                        results["total_imports"] += 1

                        if module_name in {
                            "os", "sys", "json", "re",
                            "pathlib", "collections",
                            "hashlib", "zipfile",
                            "ast", "tokenize"
                        }:

                            results["standard_imports"][module_name] = (
                                results["standard_imports"].get(module_name, 0) + 1
                            )

                        else:

                            results["third_party_imports"][module_name] = (
                                results["third_party_imports"].get(module_name, 0) + 1
                            )
            for node in ast.walk(tree):

                if isinstance(node, ast.FunctionDef):

                    end_line = getattr(node, "end_lineno", node.lineno)
                    length = end_line - node.lineno + 1

                    if length >= LONG_FUNCTION_THRESHOLD:
                        results["long_functions"].append({
                            "file": str(py_file.relative_to(root)),
                            "function": node.name,
                            "lines": length
                        })

                elif isinstance(node, ast.ClassDef):

                    end_line = getattr(node, "end_lineno", node.lineno)
                    length = end_line - node.lineno + 1

                    if length >= LONG_CLASS_THRESHOLD:
                        results["long_classes"].append({
                            "file": str(py_file.relative_to(root)),
                            "class": node.name,
                            "lines": length
                        })

            # TODO / FIXME / HACK / NOTE / Secrets
            for line_number, line in enumerate(lines, start=1):

                upper = line.upper()

                if "TODO" in upper:
                    results["todos"].append({
                        "file": str(py_file.relative_to(root)),
                        "line": line_number,
                        "text": line.strip()
                    })

                if "FIXME" in upper:
                    results["fixmes"].append({
                        "file": str(py_file.relative_to(root)),
                        "line": line_number,
                        "text": line.strip()
                    })

                if "HACK" in upper:
                    results["hacks"].append({
                        "file": str(py_file.relative_to(root)),
                        "line": line_number,
                        "text": line.strip()
                    })

                if "NOTE" in upper:
                    results["notes"].append({
                        "file": str(py_file.relative_to(root)),
                        "line": line_number,
                        "text": line.strip()
                    })

                for secret_type, pattern in SECRET_PATTERNS:

                    if pattern.search(line):

                        results["secrets"].append({
                            "file": str(py_file.relative_to(root)),
                            "line": line_number,
                            "type": secret_type
                        })

        except Exception:
            pass

    results["health"] = calculate_health(
        statistics,
        results
    )
    

    if statistics["readme_exists"]:

        if statistics["readme_status"] == "Empty":
            results["suggestions"].append(
                "README is empty. Add project overview and setup instructions."
            )

    elif not statistics["readme_exists"]:

        results["suggestions"].append(
            "Create a README.md file."
        )

    if len(results["long_functions"]) > 0:

        results["suggestions"].append(
            f"{len(results['long_functions'])} long function(s) detected. Consider splitting them."
        )

    if len(results["long_classes"]) > 0:

        results["suggestions"].append(
            f"{len(results['long_classes'])} long class(es) detected."
        )

    if len(results["empty_files"]) > 0:

        results["suggestions"].append(
            f"{len(results['empty_files'])} empty file(s) detected."
        )

    if len(results["empty_folders"]) > 0:

        results["suggestions"].append(
            f"{len(results['empty_folders'])} empty folder(s) detected."
        )

    if len(results["secrets"]) > 0:

        results["suggestions"].append(
            f"{len(results['secrets'])} possible secret(s) detected. Move them to environment variables."
        )

    if len(results["large_files"]) > 0:

        results["suggestions"].append(
            f"{len(results['large_files'])} large file(s) detected. Consider splitting them."
        )

    if len(results["duplicate_filenames"]) > 0:

        results["suggestions"].append(
            "Duplicate filenames detected. Consider renaming them."
        )

    return results