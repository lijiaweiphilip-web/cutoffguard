from pathlib import Path

from cutoffguard.cli import main


def test_demo_exit_fail(tmp_path):
    p = tmp_path / "r.json"
    assert main(["demo", "--output", str(p)]) == 2
    assert p.exists()


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
