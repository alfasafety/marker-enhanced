from __future__ import annotations

from marker.sources.navi import _parse_cheat_file


def test_parse_simple(tmp_path):
    f = tmp_path / "test.cheat"
    f.write_text("% git\n# show log\ngit log --oneline\n")
    cmds = _parse_cheat_file(f)
    assert len(cmds) == 1
    assert cmds[0].cmd == "git log --oneline"
    assert cmds[0].alias == "show log"


def test_parse_converts_placeholders(tmp_path):
    f = tmp_path / "test.cheat"
    f.write_text("% kubectl\n# get pods in namespace\nkubectl get pods -n <namespace>\n")
    cmds = _parse_cheat_file(f)
    assert cmds[0].cmd == "kubectl get pods -n {{namespace}}"


def test_parse_skips_variable_definitions(tmp_path):
    f = tmp_path / "test.cheat"
    f.write_text("% kubectl\n$ namespace: kubectl get namespaces | awk '{print $1}'\n# get pods\nkubectl get pods\n")
    cmds = _parse_cheat_file(f)
    assert len(cmds) == 1
    assert cmds[0].cmd == "kubectl get pods"


def test_parse_multiple_commands(tmp_path):
    f = tmp_path / "test.cheat"
    f.write_text(
        "% docker\n# list containers\ndocker ps -a\n# remove image\ndocker rmi <image>\n"
    )
    cmds = _parse_cheat_file(f)
    assert len(cmds) == 2
    assert cmds[0].cmd == "docker ps -a"
    assert cmds[1].cmd == "docker rmi {{image}}"


def test_parse_missing_file(tmp_path):
    assert _parse_cheat_file(tmp_path / "missing.cheat") == []


def test_parse_empty_file(tmp_path):
    f = tmp_path / "empty.cheat"
    f.write_text("")
    assert _parse_cheat_file(f) == []
