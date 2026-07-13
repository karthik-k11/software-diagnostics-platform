def calculate_health(statistics, results):

    documentation = 100
    maintainability = 100
    security = 100
    organization = 100
    dependencies = 100

    # Documentation

    if not statistics["readme_exists"]:
        documentation -= 50

    elif statistics["readme_status"] == "Empty":
        documentation -= 40

    elif statistics["readme_status"] == "Basic":
        documentation -= 20

    if not statistics["gitignore_exists"]:
        documentation -= 20

    if not statistics["requirements_exists"]:
        documentation -= 30

    # Maintainability

    maintainability -= len(results["long_functions"]) * 5
    maintainability -= len(results["long_classes"]) * 8
    maintainability -= len(results["duplicate_filenames"]) * 3

    # Security

    security -= len(results["secrets"]) * 10

    # Organization

    organization -= len(results["empty_files"]) * 3
    organization -= len(results["empty_folders"]) * 5

    # Dependencies

    if results["total_imports"] == 0:
        dependencies -= 30

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
        "overall": overall
    }