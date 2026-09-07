from cutoffguard.cli import main


def test_demo_exit_fail(tmp_path):
    p=tmp_path/"r.json"
    assert main(["demo","--output",str(p)])==2
    assert p.exists()
