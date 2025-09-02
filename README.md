# Clearskies General Module Template

This template allows you to quickly scaffold a new Clearskies module for any third-party API or integration. It is designed for general-purpose module development and follows the architecture and patterns used by the Clearskies ecosystem.

## Prerequisites

- Python 3.11+
- [Copier](https://copier.readthedocs.io/en/stable/) for template generation

## Installation

First, install Copier:

```bash
pip install copier
```

## Usage

To create a new Clearskies module, run:

```bash
copier copy https://github.com/clearskies-py/clearskies-module-template my-module --trust
```

**Note:** The `--trust` flag is required because the template includes automated setup tasks (git init, dependency installation, and pre-commit hook setup).

This will prompt you for the necessary information to configure your module:

- `module_name`: The name of the module (e.g., gitlab, snyk, wiz)
- `service_display_name`: Display name of the module (e.g., GitLab, Snyk, Wiz)
- `author_name`: Your name
- `author_email`: Your email
- `create_backends`: Does this module need backends?
- `create_columns`: Does this module need columns?
- `create_configs`: Does this module need configs?
- `create_endpoints`: Does this module need endpoints?
- `create_models`: Does this module need models?

## Project Structure

After generation, your project will have the following structure:

```bash
my-module/
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── MANIFEST.in
├── README.md
├── uv.lock  (will be generated when you run uv sync)
├── pyproject.toml
├── ruff.toml
└── src/
    └── clearskies_{{ module_name|replace('-', '_') }}/
        ├── __init__.py
        ├── backends/        (if enabled)
        ├── columns/         (if enabled)
        ├── configs/         (if enabled)
        ├── endpoints/       (if enabled)
        ├── models/          (if enabled)
        └── ...
```


## Implementation

After generating your project, you'll need to customize the module logic and implement the API-specific or integration-specific functionality. The template provides structure and examples for:

- Defining schemas and columns (if enabled)
- Implementing backends, configs, endpoints, and models (if enabled)
- Using type hints and clear parameter documentation
- Following best practices for Python packaging and Clearskies modules

## Development

To set up your development environment with pre-commit hooks:

```bash
cd my-module
# Install uv if not already installed
pip install uv

# Install all dependencies (including dev dependencies)
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Optionally, run pre-commit on all files to check everything is working
uv run pre-commit run --all-files
```

The generated project includes a `.pre-commit-config.yaml` file with the following tools:

- **black**: Code formatting
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checking
- **yamllint**: YAML file linting
- **Standard hooks**: trailing whitespace, end-of-file-fixer, etc.


## Updating Existing Projects

If you have an existing project created from this template and want to update it with template changes:

```bash
cd your-existing-project
copier update --trust
```

**Requirements for updates:**

- Your project must be in a git repository with all changes committed
- The project must have been created using the GitHub template URL (`gh:clearskies-module-template`), not a local path
- The `.copier-answers.yml` file must be present (automatically created during initial generation)

**Important:** Updates only work when the original template was accessed via git (GitHub/GitLab URL). If you created your project from a local template path, updates won't work due to missing git reference tracking.

**Note:** Updates will merge template changes with your custom implementation. Review the changes carefully before committing.


## Testing Your Implementation

Testing will depend on your module's purpose and enabled features. For API modules, you can use direct HTTP calls or integration tests. For general modules, follow Clearskies documentation and best practices for testing and validation.


## License

MIT License - see the LICENSE file for details
