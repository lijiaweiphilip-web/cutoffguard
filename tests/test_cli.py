from pathlib import Path

from cutoffguard.cli import main


def test_demo_exit_fail(tmp_path):
    p = tmp_path / "r.json"
    assert main(["demo", "--output", str(p)]) == 2
    assert p.exists()


def test_explain_list_covers_core_codes(capsys):
    assert main(["explain", "--list"]) == 0
    output = capsys.readouterr().out
    assert "EMPTY_INPUT" in output
    assert "POST_CUTOFF_AVAILABILITY" in output


def test_explain_unknown_code_is_an_input_error(capsys):
    assert main(["explain", "NOT_A_FINDING"]) == 4
    assert "unknown finding code" in capsys.readouterr().err


def test_explain_json_contains_contract_fields(capsys):
    assert main(["explain", "EMPTY_INPUT", "--format", "json"]) == 0
    output = capsys.readouterr().out
    assert '"remediation"' in output
    assert '"applies_to"' in output


def test_documented_contaminated_fixture_is_a_failure(tmp_path):
    fixture = (
        Path(__file__).parents[1] / "examples" / "availability" / "contaminated.jsonl"
    )
    report = tmp_path / "contaminated.json"
    assert (
        main(
            [
                "audit",
                str(fixture),
                "--cutoff",
                "2024-04-15T00:00:00Z",
                "--output",
                str(report),
            ]
        )
        == 2
    )
