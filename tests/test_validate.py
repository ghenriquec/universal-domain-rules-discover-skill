"""Behavior tests for the domain-discovery output validator."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate.py"
REQUIRED = (
    "domain-overview.md",
    "domain-rules.json",
    "business-rules-matrix.md",
    "state-transition-matrix.md",
    "permission-matrix.md",
    "calculation-rules.md",
    "domain-conflicts.md",
    "domain-gaps.md",
    "domain-risks.md",
    "qa-domain-scenarios.json",
    "traceability-matrix.md",
    "sources/source-index.md",
)


def test_required_repository_files_exist() -> None:
    required = (
        "SKILL.md",
        "manifest.yaml",
        "schemas/domain-rules.schema.json",
        "schemas/qa-domain-scenarios.schema.json",
        "scripts/validate.py",
    )
    for item in required:
        assert (ROOT / item).is_file(), item


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    for relative in REQUIRED:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Example artifact\n", encoding="utf-8")

    rules = {
        "project": {"name": "Example"},
        "analysis": {
            "status": "partial",
            "mode": "full",
            "generatedAt": "2026-01-01",
            "scope": ["example"],
            "limitations": [],
        },
        "actors": [],
        "entities": [],
        "modules": [],
        "rules": [{
            "id": "BR-001",
            "name": "Sample rule",
            "module": "example",
            "type": "validation",
            "description": "A testable rule",
            "actors": [],
            "sources": [{"id": "SRC-001", "type": "source", "location": "example"}],
            "status": "confirmed",
            "confidence": "high",
            "risk": "critical",
            "qaScenarios": ["QA-001"],
        }],
        "stateMachines": [],
        "permissionMatrix": [],
        "calculations": [],
        "conflicts": [],
        "gaps": [],
        "domainRisks": [],
        "qaScenarios": ["QA-001"],
    }
    scenarios = {
        "project": {"name": "Example"},
        "scenarios": [{
            "id": "QA-001",
            "ruleId": "BR-001",
            "module": "example",
            "title": "Sample scenario",
            "priority": "P0",
            "risk": "critical",
            "actor": "user",
            "preconditions": [],
            "steps": ["Perform action"],
            "expectedResults": ["Rule enforced"],
            "layers": ["service"],
        }],
    }
    write_doc(tmp_path, "domain-rules.json", rules)
    write_doc(tmp_path, "qa-domain-scenarios.json", scenarios)
    return tmp_path


def write_doc(output: Path, filename: str, data: dict) -> None:
    (output / filename).write_text(json.dumps(data), encoding="utf-8")


def read_doc(output: Path, filename: str) -> dict:
    return json.loads((output / filename).read_text(encoding="utf-8"))


def validate(output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(output)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_valid_output_passes(output_dir: Path) -> None:
    result = validate(output_dir)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "VALID: 1 rules and 1 scenarios" in result.stdout


def test_missing_artifact_fails(output_dir: Path) -> None:
    (output_dir / "permission-matrix.md").unlink()
    result = validate(output_dir)
    assert result.returncode == 1
    assert "Missing required artifact: permission-matrix.md" in result.stdout


def test_duplicate_rule_id_fails(output_dir: Path) -> None:
    rules = read_doc(output_dir, "domain-rules.json")
    rules["rules"].append(dict(rules["rules"][0]))
    write_doc(output_dir, "domain-rules.json", rules)
    result = validate(output_dir)
    assert result.returncode == 1
    assert "Duplicate rule id: BR-001" in result.stdout


def test_unknown_rule_reference_fails(output_dir: Path) -> None:
    scenarios = read_doc(output_dir, "qa-domain-scenarios.json")
    scenarios["scenarios"][0]["ruleId"] = "BR-999"
    write_doc(output_dir, "qa-domain-scenarios.json", scenarios)
    result = validate(output_dir)
    assert result.returncode == 1
    assert "references unknown rule BR-999" in result.stdout


def test_critical_rule_without_qa_scenario_fails(output_dir: Path) -> None:
    rules = read_doc(output_dir, "domain-rules.json")
    rules["rules"][0]["qaScenarios"] = []
    write_doc(output_dir, "domain-rules.json", rules)
    result = validate(output_dir)
    assert result.returncode == 1
    assert "Critical rule BR-001 has no QA scenario" in result.stdout


def test_schema_error_fails_without_traceback(output_dir: Path) -> None:
    rules = read_doc(output_dir, "domain-rules.json")
    rules["rules"][0]["risk"] = "urgent"
    write_doc(output_dir, "domain-rules.json", rules)
    result = validate(output_dir)
    assert result.returncode == 1
    assert "domain-rules.json schema error" in result.stdout
    assert "Traceback" not in result.stderr


def test_invalid_json_fails_without_traceback(output_dir: Path) -> None:
    (output_dir / "domain-rules.json").write_text("{invalid", encoding="utf-8")
    result = validate(output_dir)
    assert result.returncode == 1
    assert "ERROR: Could not read JSON document" in result.stdout
    assert "Traceback" not in result.stderr
