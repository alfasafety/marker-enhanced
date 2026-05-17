from __future__ import annotations

from marker.context import boosted_prefixes, detect


def test_detect_terraform(tmp_path):
    (tmp_path / "main.tf").write_text("")
    assert "terraform" in detect(tmp_path)


def test_detect_docker_compose(tmp_path):
    (tmp_path / "docker-compose.yml").write_text("")
    assert "docker-compose" in detect(tmp_path)


def test_detect_git(tmp_path):
    (tmp_path / ".git").mkdir()
    assert "git" in detect(tmp_path)


def test_detect_makefile(tmp_path):
    (tmp_path / "Makefile").write_text("")
    assert "make" in detect(tmp_path)


def test_detect_python(tmp_path):
    (tmp_path / "pyproject.toml").write_text("")
    assert "python" in detect(tmp_path)


def test_detect_empty_dir(tmp_path):
    assert detect(tmp_path) == set()


def test_detect_multiple(tmp_path):
    (tmp_path / "main.tf").write_text("")
    (tmp_path / ".git").mkdir()
    contexts = detect(tmp_path)
    assert "terraform" in contexts
    assert "git" in contexts


def test_boosted_prefixes_terraform():
    prefixes = boosted_prefixes({"terraform"})
    assert "terraform" in prefixes
    assert "tf" in prefixes
    assert "tfa" in prefixes


def test_boosted_prefixes_kubernetes():
    prefixes = boosted_prefixes({"kubernetes"})
    assert "kubectl" in prefixes
    assert "k" in prefixes
    assert "helm" in prefixes


def test_boosted_prefixes_empty():
    assert boosted_prefixes(set()) == frozenset()


def test_boosted_prefixes_multiple():
    prefixes = boosted_prefixes({"git", "docker"})
    assert "git" in prefixes
    assert "docker" in prefixes
    assert "gh" in prefixes
