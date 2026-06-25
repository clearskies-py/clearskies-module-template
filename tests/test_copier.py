import subprocess
from pathlib import Path

import pytest

# The root directory of your template project
TEMPLATE_DIR = Path(__file__).parent.parent


def test_template_dir():
    assert TEMPLATE_DIR.is_dir(), "TEMPLATE_DIR must be a local directory for testing"


def test_template_generation_scratch(tmp_path: Path):
    """
    Test the template by calling the 'copier' command directly.

    and inspecting the generated output.
    """
    # 1. Define the destination directory for the new project
    project_destination = tmp_path / "my-test-project"

    # 2. Build and run the 'copier copy' command
    #    --force: Run non-interactively, accepting defaults
    #    --data: Pass specific answers as key=value pairs
    command = [
        "copier",
        "copy",
        "--force",
        "--trust",
        "--skip-tasks",
        "--vcs-ref",
        "HEAD",
        "--data",
        "module_name=test-service",
        "--data",
        "module_display_name='Test Service'",
        "--data",
        "create_backends=True",
        str(TEMPLATE_DIR),
        str(project_destination),
    ]

    # Execute the command from within Python
    # 'check=True' will raise an error if the command fails
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        # If copier fails, print its output for easier debugging
        print("Copier command failed.")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        pytest.fail("The 'copier copy' command failed.")

    # 3. Assert that the generated project is correct
    assert project_destination.is_dir()

    # Check for a specific file
    pyproject_toml_path = project_destination / "pyproject.toml"
    assert pyproject_toml_path.is_file()

    # Check for specific content within the file
    pyproject_toml_content = pyproject_toml_path.read_text()
    assert 'name = "clear-skies-test-service"' in pyproject_toml_content

    # Check for specific content within the file
    licence_path = project_destination / "LICENSE"
    assert licence_path.is_file()

    backend_init = project_destination / "src" / "clearskies_test_service" / "backends" / "__init__.py"
    assert backend_init.is_file()

    license_content = licence_path.read_text()
    from datetime import datetime

    current_year = str(datetime.now().year)
    assert f"Copyright (c) {current_year}" in license_content

    answers_file_path = project_destination / ".copier-answers.yml"
    assert answers_file_path.is_file()

    # Check the generated directory or import path:
    expected_package_dir = project_destination / "src" / "clearskies_test-service"
    assert not expected_package_dir.is_dir()

    # Check the generated directory or import path:
    expected_package_dir = project_destination / "src" / "clearskies_test_service"
    assert expected_package_dir.is_dir()

    # Check for specific files
    expected_files = [
        "README.md",
        "src/clearskies_test_service/__init__.py",
    ]
    for file in expected_files:
        assert (project_destination / file).is_file()

    pre_commit_path = project_destination / ".pre-commit-config.yaml"
    assert pre_commit_path.is_file()
    pre_commit_content = pre_commit_path.read_text()
    assert "- id: ruff-check" in pre_commit_content
    assert "uv run ty check src" in pre_commit_content
    assert "args: [-d, relaxed]" in pre_commit_content
    assert "args: [--assume-in-merge]" in pre_commit_content

    ruff_config_path = project_destination / "ruff.toml"
    assert ruff_config_path.is_file()
    ruff_config_content = ruff_config_path.read_text()
    assert 'select = ["I", "D", "F401"]' in ruff_config_content
    assert '"**/__init__.py" = ["I001"]' in ruff_config_content

    run_tests_workflow_path = project_destination / ".github" / "workflows" / "run-tests.yml"
    assert run_tests_workflow_path.is_file()
    run_tests_workflow_content = run_tests_workflow_path.read_text()
    assert "run-ty:" in run_tests_workflow_content
    assert "run-mypy" not in run_tests_workflow_content

    tests_matrix_workflow_path = project_destination / ".github" / "workflows" / "tests-matrix.yaml"
    assert tests_matrix_workflow_path.is_file()
    tests_matrix_workflow_content = tests_matrix_workflow_path.read_text()
    assert "jobs:\n  ty:" in tests_matrix_workflow_content
    assert "uv run ty check src" in tests_matrix_workflow_content
