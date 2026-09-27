from pathlib import Path

from regscope.change_mapper import map_changed_lines_to_functions


def test_maps_definition_and_body_changes_and_keeps_module_lines_separate(tmp_path: Path):
    source = tmp_path / "app" / "service.py"
    source.parent.mkdir()
    source.write_text(
        "LIMIT = 10\n\nclass Service:\n    def run(self):\n        return LIMIT\n\ndef helper():\n    return 1\n",
        encoding="utf-8",
    )

    result = map_changed_lines_to_functions(source, [1, 4, 8], project_root=tmp_path)

    assert result == {
        "functions": ["app.service:Service.run", "app.service:helper"],
        "module_level_lines": [1],
    }
