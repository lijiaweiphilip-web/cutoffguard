from cutoffguard import TemporalRecord, audit_records
from cutoffguard.records import parse_ts


def R(i, o, a=None, label=None, r=None):
    return TemporalRecord(i, parse_ts(o), parse_ts(a), parse_ts(label), parse_ts(r))


def codes(rep):
    return {f.code for f in rep.findings}


def test_pass():
    assert (
        audit_records(
            [R("a", "2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z")],
            "2024-01-03T00:00:00Z",
        ).status
        == "pass"
    )


def test_future_observation():
    assert "FUTURE_OBSERVATION" in codes(
        audit_records(
            [R("a", "2024-01-04T00:00:00Z", "2024-01-02T00:00:00Z")],
            "2024-01-03T00:00:00Z",
        )
    )


def test_post_cutoff_availability():
    assert "POST_CUTOFF_AVAILABILITY" in codes(
        audit_records(
            [R("a", "2024-01-01T00:00:00Z", "2024-01-04T00:00:00Z")],
            "2024-01-03T00:00:00Z",
        )
    )


def test_immature_label():
    assert "IMMATURE_LABEL" in codes(
        audit_records(
            [
                R(
                    "a",
                    "2024-01-01T00:00:00Z",
                    "2024-01-01T00:00:00Z",
                    "2024-01-05T00:00:00Z",
                )
            ],
            "2024-01-03T00:00:00Z",
        )
    )


def test_revision_warns():
    rep = audit_records(
        [
            R(
                "a",
                "2024-01-01T00:00:00Z",
                "2024-01-01T00:00:00Z",
                None,
                "2024-02-01T00:00:00Z",
            )
        ],
        "2024-01-03T00:00:00Z",
    )
    assert rep.status == "review" and "POST_CUTOFF_REVISION" in codes(rep)


def test_missing_availability_warns():
    assert (
        audit_records([R("a", "2024-01-01T00:00:00Z")], "2024-01-03T00:00:00Z").status
        == "review"
    )


def test_missing_availability_can_be_allowed():
    assert (
        audit_records(
            [R("a", "2024-01-01T00:00:00Z")],
            "2024-01-03T00:00:00Z",
            require_availability=False,
        ).status
        == "pass"
    )


def test_duplicate_id_fails():
    assert "DUPLICATE_ID" in codes(
        audit_records(
            [
                R("a", "2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z"),
                R("a", "2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z"),
            ],
            "2024-01-03T00:00:00Z",
        )
    )
