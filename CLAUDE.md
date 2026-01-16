# CLAUDE.md

Guidelines for AI assistants working on this Python project.

## Project Context

This is a Python project. Before making changes:
- Review the existing codebase structure
- Check `pyproject.toml` for dependencies
- Understand the project's purpose and architecture

## Code Standards

- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Write clear, self-documenting code with meaningful variable names
- Add docstrings for modules, classes, and public functions
- Keep functions focused and under 50 lines when possible

## Development Workflow

1. **Reading First**: Always examine existing files before suggesting changes
2. **Testing**: Write or update tests when modifying functionality
3. **Dependencies**: Add new dependencies to the appropriate file with pinned versions
4. **Error Handling**: Use appropriate exception handling, don't silence errors
5. **Documentation**: Update README.md when adding features or changing usage

## Best Practices

- Use `uv` for package management 
- Use virtual environments (`venv` or `virtualenv`)
- Prefer standard library solutions over external dependencies
- Use `pathlib` for file operations instead of `os.path`
- Apply list/dict comprehensions where they improve readability
- Use context managers (`with` statements) for resource management
- Write idiomatic Python (don't translate from other languages)

## Common Patterns

```python
# Good: Type hints and docstrings
def process_data(items: list[str], threshold: int = 10) -> dict[str, int]:
    """Process items and return counts above threshold.
    
    Args:
        items: List of strings to process
        threshold: Minimum count to include (default: 10)
        
    Returns:
        Dictionary mapping items to their counts
    """
    ...

# Good: Context managers
with open('file.txt') as f:
    data = f.read()

# Good: Pathlib usage
from pathlib import Path
config_path = Path(__file__).parent / 'config.json'
```

## What to Avoid

- Global variables (use classes or function parameters)
- Bare `except:` clauses (catch specific exceptions)
- Mutable default arguments (`def func(items=[]):`)
- Hardcoded file paths (use relative paths or configuration)
- Print statements for logging (use the `logging` module)

## File Organization

```
project/
├── src/              # Source code
├── tests/            # Test files
├── docs/             # Documentation
├── pyproject.toml    # Dependencies
├── README.md         # Project overview
└── .gitignore        # Git exclusions
```

## When Proposing Changes

- Explain the reasoning behind significant changes
- Highlight any breaking changes or migration steps
- Suggest test cases for new functionality
- Consider backward compatibility