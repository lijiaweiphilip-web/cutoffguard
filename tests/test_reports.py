import json
import xml.etree.ElementTree as ET

from cutoffguard import TemporalRecord, audit_records
from cutoffguard.cli import main
from cutoffguard.records import parse_ts
from cutoffguard.report import render_junit, render_sarif


def _report(status: str = "fail"):
    if status == "pass":
        records = [
            TemporalRecord(
                "r1",
                parse_ts("2024-01-01T00:00:00Z"),
                parse_ts("2024-01-01T01:00:00Z"),
            )
        ]
    else:
        records = [
            TemporalRecord(
                "r1",
                parse_ts("2024-01-03T00:00:00Z"),
                parse_ts("2024-01-03T01:00:00Z"),
            )
        ]
    return audit_records(records, "2024-01-02T00:00:00Z")


def test_sarif_contains_rules_results_and_boundary():
    data = json.loads(render_sarif(_report()))
    assert data["version"] == "2.1.0"
    run = data["runs"][0]
    assert run["tool"]["driver"]["name"] == "CutoffGuard"
    assert run["results"][0]["ruleId"] == "FUTURE_OBSERVATION"
    assert run["results"][0]["properties"]["record_id"] == "r1"
    assert "assurance_boundary" in run["properties"]


def test_junit_is_parseable_and_marks_errors():
    root = ET.fromstring(render_junit(_report()))
    assert root.tag == "testsuite"
    assert root.attrib["tests"] == "2"
    assert root.attrib["failures"] == "2"
    assert len(root.findall("testcase/failure")) == 2


def test_junit_pass_has_one_conformance_case():
    root = ET.fromstring(render_junit(_report("pass")))
    assert root.attrib == {
        "name": "cutoffguard",
        "tests": "1",
        "failures": "0",
        "skipped": "0",
    }
    assert root.find("testcase").attrib["name"] == "temporal_conformance"


def test_cli_can_write_sarif_and_junit(tmp_path):
    source = tmp_path / "records.jsonl"
    source.write_text(
        '{"id":"r1","observed_at":"2024-01-03T00:00:00Z",'
        '"available_at":"2024-01-03T01:00:00Z"}\n',
        encoding="utf-8",
    )
    sarif = tmp_path / "result.sarif"
    junit = tmp_path / "result.xml"
    assert (
        main(
            [
                "audit",
                str(source),
                "--cutoff",
                "2024-01-02T00:00:00Z",
                "--format",
                "sarif",
                "--output",
                str(sarif),
            ]
        )
        == 2
    )
    assert (
        main(
            [
                "audit",
                str(source),
                "--cutoff",
                "2024-01-02T00:00:00Z",
                "--format",
                "junit",
                "--output",
                str(junit),
            ]
        )
        == 2
    )
    assert json.loads(sarif.read_text(encoding="utf-8"))["version"] == "2.1.0"
    assert ET.parse(junit).getroot().tag == "testsuite"
