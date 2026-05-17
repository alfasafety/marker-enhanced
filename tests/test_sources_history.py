from __future__ import annotations

import json

from marker.sources.history import _parse_bash, _parse_zsh, load, update


def test_parse_zsh_plain_lines(tmp_path):
    hist = tmp_path / "hist"
    hist.write_text("git status\nkubectl get pods\n")
    assert _parse_zsh(hist) == ["git status", "kubectl get pods"]


def test_parse_zsh_extended_format(tmp_path):
    hist = tmp_path / "hist"
    hist.write_text(": 1700000000:0;git status\n: 1700000001:0;kubectl get pods\n")
    assert _parse_zsh(hist) == ["git status", "kubectl get pods"]


def test_parse_zsh_skips_empty(tmp_path):
    hist = tmp_path / "hist"
    hist.write_text("\n\ngit status\n\n")
    assert _parse_zsh(hist) == ["git status"]


def test_parse_bash(tmp_path):
    hist = tmp_path / "hist"
    hist.write_text("# timestamp\ngit log --oneline\n")
    assert _parse_bash(hist) == ["git log --oneline"]


def test_load_always_empty(tmp_path):
    assert load(tmp_path) == []


def test_update_writes_usage_json(tmp_path, monkeypatch):
    hist = tmp_path / ".zsh_history"
    # 6 runs of one command (short ones are filtered)
    hist.write_text(": 0:0;terraform plan -out tfplan\n" * 6)
    monkeypatch.setenv("HISTFILE", str(hist))
    count = update(tmp_path)
    assert count == 1
    data = json.loads((tmp_path / "usage.json").read_text())
    assert "terraform plan -out tfplan" in data


def test_update_filters_noise(tmp_path, monkeypatch):
    hist = tmp_path / ".zsh_history"
    hist.write_text(": 0:0;ls\n: 0:0;cd /tmp\n: 0:0;kubectl get pods\n")
    monkeypatch.setenv("HISTFILE", str(hist))
    update(tmp_path)
    data = json.loads((tmp_path / "usage.json").read_text())
    assert "ls" not in data
    assert "cd /tmp" not in data
    assert "kubectl get pods" in data


def test_update_merges_existing(tmp_path, monkeypatch):
    hist = tmp_path / ".zsh_history"
    hist.write_text(": 0:0;git diff --stat\n" * 10)
    monkeypatch.setenv("HISTFILE", str(hist))
    (tmp_path / "usage.json").write_text(json.dumps({"git diff --stat": 5}))
    update(tmp_path)
    data = json.loads((tmp_path / "usage.json").read_text())
    assert data["git diff --stat"] > 5


def test_update_no_history_returns_zero(tmp_path, monkeypatch):
    monkeypatch.setenv("HISTFILE", str(tmp_path / "nonexistent"))
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    assert update(tmp_path) == 0
