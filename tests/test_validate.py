from pathlib import Path


def test_required_repository_files_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    required = [
        "SKILL.md",
        "manifest.yaml",
        "schemas/domain-rules.schema.json",
        "schemas/qa-domain-scenarios.schema.json",
        "scripts/validate.py",
    ]
    for item in required:
        assert (root / item).is_file(), item
