import json

from cutoffguard.demo import run_demo
from cutoffguard.report import render_html, render_json


def test_json(): assert json.loads(render_json(run_demo()))["status"]=="fail"
def test_html():
    h=render_html(run_demo())
    assert "CutoffGuard" in h and "Assurance boundary" in h and "POST_CUTOFF_AVAILABILITY" in h
