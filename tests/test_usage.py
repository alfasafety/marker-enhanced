from __future__ import annotations

import json
import math

import pytest

from marker.command import Command
from marker.usage import boost, load, record


def _cmd(cmd: str, alias: str = "") -> Command:
    return Command(cmd, alias)


def test_load_empty_dir(tmp_path):
    assert load(tmp_path) == {}


def test_load_invalid_json(tmp_path):
    (tmp_path / "usage.json").write_text("not json")
    assert load(tmp_path) == {}


def test_record_creates_entry(tmp_path):
    record(tmp_path, _cmd("git status"))
    usage = load(tmp_path)
    assert usage["git status"] == 1


def test_record_increments(tmp_path):
    record(tmp_path, _cmd("git status"))
    record(tmp_path, _cmd("git status"))
    assert load(tmp_path)["git status"] == 2


def test_record_with_alias(tmp_path):
    record(tmp_path, _cmd("kubectl get pods", "k get pods"))
    usage = load(tmp_path)
    assert "kubectl get pods##k get pods" in usage


def test_boost_zero_count():
    assert boost({}, _cmd("kubectl")) == 0.0


def test_boost_nonzero():
    usage = {"git status": 10}
    b = boost(usage, _cmd("git status"))
    assert b == pytest.approx(math.log1p(10) * 0.3)


def test_boost_caps_logarithmically():
    # boost at 100 uses should not be drastically higher than at 10
    usage_10 = {"cmd": 10}
    usage_100 = {"cmd": 100}
    b10 = boost(usage_10, _cmd("cmd"))
    b100 = boost(usage_100, _cmd("cmd"))
    assert b100 < b10 * 3  # log scale, not linear
