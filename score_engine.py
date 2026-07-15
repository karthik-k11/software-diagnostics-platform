def calculate_health(statistics, results):

    documentation = 100
    maintainability = 100
    security = 100
    organization = 100
    dependencies = 100

    reasons = {
        "documentation": [],
        "maintainability": [],
        "security": [],
        "organization": [],
        "dependencies": []
    }

    # Documentation

    if not statistics["readme_exists"]:

        documentation -= 50

        reasons["documentation"].append(
            "README file is missing."
        )

    elif statistics["readme_status"] == "Empty":

        documentation -= 40

        reasons["documentation"].append(
            "README file is empty."
        )

    elif statistics["readme_status"] == "Basic":

        documentation -= 20

        reasons["documentation"].append(
            "README contains limited documentation."
        )

    if not statistics["gitignore_exists"]:

        documentation -= 20

        reasons["documentation"].append(
            ".gitignore file is missing."
        )

    if not statistics["requirements_exists"]:

        documentation -= 30

        reasons["documentation"].append(
            "requirements.txt file is missing."
        )

    # Maintainability

    if len(results["long_functions"]) > 0:

        maintainability -= len(results["long_functions"]) * 5

        reasons["maintainability"].append(
            f"{len(results['long_functions'])} long function(s) detected."
        )

    if len(results["long_classes"]) > 0:

        maintainability -= len(results["long_classes"]) * 8

        reasons["maintainability"].append(
            f"{len(results['long_classes'])} long class(es) detected."
        )

    if len(results["duplicate_filenames"]) > 0:

        maintainability -= len(results["duplicate_filenames"]) * 3

        reasons["maintainability"].append(
            "Duplicate filenames detected."
        )

    # Security

    if len(results["secrets"]) > 0:

        security -= len(results["secrets"]) * 10

        reasons["security"].append(
            f"{len(results['secrets'])} possible secret(s) detected."
        )

    # Organization

    if len(results["empty_files"]) > 0:

        organization -= len(results["empty_files"]) * 3

        reasons["organization"].append(
            f"{len(results['empty_files'])} empty file(s) detected."
        )

    if len(results["empty_folders"]) > 0:

        organization -= len(results["empty_folders"]) * 5

        reasons["organization"].append(
            f"{len(results['empty_folders'])} empty folder(s) detected."
        )

    # Dependencies

    if results["total_imports"] == 0:

        dependencies -= 30

        reasons["dependencies"].append(
            "No imports detected."
        )

    documentation = max(0, documentation)
    maintainability = max(0, maintainability)
    security = max(0, security)
    organization = max(0, organization)
    dependencies = max(0, dependencies)

    overall = round(
        (
            documentation +
            maintainability +
            security +
            organization +
            dependencies
        ) / 5
    )

    return {

        "documentation": documentation,
        "maintainability": maintainability,
        "security": security,
        "organization": organization,
        "dependencies": dependencies,
        "overall": overall,

        "reasons": reasons
    }