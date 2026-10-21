#!/usr/bin/env python3
"""Validate Universal Domain Rules Discovery output.

Usage:
    python scripts/validate.py /path/to/domain-discovery
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError as exc:
    raise SystemExit("Missing dependency: pip install jsonschema") from exc

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
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
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_unique(items: list[dict], field: str, label: str) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        value = item.get(field)
        if not value:
            errors.append(f"{label}[{index}] missing {field}")
        elif value in seen:
            errors.append(f"Duplicate {label} {field}: {value}")
        else:
            seen.add(value)
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate.py <domain-discovery-directory>")
        return 2

    output = Path(sys.argv[1]).resolve()
    errors: list[str] = []

    for relative in REQUIRED:
        if not (output / relative).is_file():
            errors.append(f"Missing required artifact: {relative}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    try:
        rules_doc = load_json(output / "domain-rules.json")
        scenarios_doc = load_json(output / "qa-domain-scenarios.json")
        rules_schema = load_json(ROOT / "schemas/domain-rules.schema.json")
        scenarios_schema = load_json(ROOT / "schemas/qa-domain-scenarios.schema.json")
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: Could not read JSON document: {exc}")
        return 1

    for filename, document, schema in (
        ("domain-rules.json", rules_doc, rules_schema),
        ("qa-domain-scenarios.json", scenarios_doc, scenarios_schema),
    ):
        try:
            jsonschema.validate(document, schema)
        except jsonschema.ValidationError as exc:
            errors.append(f"{filename} schema error: {exc.message}")

    # Don't traverse invalid documents: schemas guarantee the structure used below.
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    rules = rules_doc.get("rules", [])
    scenarios = scenarios_doc.get("scenarios", [])
    errors.extend(validate_unique(rules, "id", "rule"))
    errors.extend(validate_unique(scenarios, "id", "scenario"))

    rules_by_id = {item["id"]: item for item in rules}
    scenarios_by_id = {item["id"]: item for item in scenarios}

    for scenario in scenarios:
        linked_rule = rules_by_id.get(scenario["ruleId"])
        if linked_rule is None:
            errors.append(f"Scenario {scenario['id']} references unknown rule {scenario['ruleId']}")
        elif scenario["id"] not in linked_rule["qaScenarios"]:
            errors.append(
                f"Scenario {scenario['id']} is not listed by its linked rule {scenario['ruleId']}"
            )

    for rule in rules:
        for scenario_id in rule.get("qaScenarios", []):
            linked_scenario = scenarios_by_id.get(scenario_id)
            if linked_scenario is None:
                errors.append(f"Rule {rule['id']} references unknown scenario {scenario_id}")
            elif linked_scenario["ruleId"] != rule["id"]:
                errors.append(
                    f"Rule {rule['id']} references scenario {scenario_id} "
                    f"owned by {linked_scenario['ruleId']}"
                )
        if rule.get("risk") == "critical" and not rule.get("qaScenarios"):
            errors.append(f"Critical rule {rule.get('id')} has no QA scenario")
        if not rule.get("sources"):
            errors.append(f"Rule {rule.get('id')} has no source")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"VALID: {len(rules)} rules and {len(scenarios)} scenarios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
