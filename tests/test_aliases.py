from __future__ import annotations

import pytest

from marker.aliases import DEFAULT_ALIASES, abbreviate, expand, load


def test_expand_known_alias():
    assert expand("k get pods", DEFAULT_ALIASES) == "kubectl get pods"


def test_expand_single_token():
    assert expand("tf", DEFAULT_ALIASES) == "terraform"


def test_expand_multi_word_alias():
    assert expand("tfa --plan", DEFAULT_ALIASES) == "terraform apply --plan"


def test_expand_unknown_passthrough():
    assert expand("docker ps", DEFAULT_ALIASES) == "docker ps"


def test_expand_empty():
    assert expand("", DEFAULT_ALIASES) == ""


def test_abbreviate_single_word():
    assert abbreviate("terraform", DEFAULT_ALIASES) == "tf"


def test_abbreviate_most_specific_wins():
    # "tfa" matches "terraform apply" which is longer than "tf" → "terraform"
    assert abbreviate("terraform apply --auto-approve", DEFAULT_ALIASES) == "tfa --auto-approve"


def test_abbreviate_fallback_to_shorter():
    assert abbreviate("terraform plan -out foo", DEFAULT_ALIASES) == "tfp -out foo"


def test_abbreviate_unknown_passthrough():
    assert abbreviate("helm upgrade", DEFAULT_ALIASES) == "helm upgrade"


def test_load_defaults_no_file(tmp_path):
    aliases = load(tmp_path)
    assert aliases == DEFAULT_ALIASES


def test_load_adds_entry(tmp_path):
    (tmp_path / "aliases.txt").write_text("kns=kubectl -n kube-system\n")
    aliases = load(tmp_path)
    assert aliases["kns"] == "kubectl -n kube-system"
    assert "k" in aliases  # defaults preserved


def test_load_removes_entry(tmp_path):
    (tmp_path / "aliases.txt").write_text("-d\n")
    aliases = load(tmp_path)
    assert "d" not in aliases
    assert "k" in aliases


def test_load_ignores_comments(tmp_path):
    (tmp_path / "aliases.txt").write_text("# this is a comment\n")
    aliases = load(tmp_path)
    assert aliases == DEFAULT_ALIASES
