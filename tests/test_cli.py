import sys

import pytest

import regscope.cli as cli


@pytest.mark.parametrize("selected_exit_code", [0, 1])
def test_selected_only_cli_propagates_selected_test_exit_code(
    monkeypatch, selected_exit_code: int
):
    result = {
        "selection": {"strategy": "coverage-intersection", "selected_tests": ["tests/test_api.py::test_route"]},
        "evaluation": {"selected_run": {"exit_code": selected_exit_code}},
    }
    monkeypatch.setattr(cli, "run_pipeline", lambda *args, **kwargs: result)
    monkeypatch.setattr(
        sys,
        "argv",
        ["regscope", "run", "target", "base", "head", "--output", "out", "--selected-only"],
    )

    with pytest.raises(SystemExit) as raised:
        cli.main()

    assert raised.value.code == selected_exit_code


def test_collect_cli_writes_mapping_to_requested_path(tmp_path, monkeypatch):
    output = tmp_path / "artifacts" / "baseline.json"
    calls = {}

    def fake_collect(target, output_dir, **kwargs):
        calls.update(target=target, output_dir=output_dir, **kwargs)
        return {"mappings": [{"test_id": "tests/test_api.py::test_route"}]}

    monkeypatch.setattr(cli, "collect_test_function_mappings", fake_collect)
    monkeypatch.setattr(
        sys,
        "argv",
        ["regscope", "collect", "target", "--output", str(output), "--python", "target-python"],
    )

    cli.main()

    assert calls == {
        "target": "target",
        "output_dir": output.resolve().parent,
        "python_executable": "target-python",
        "mapping_path": str(output),
    }
