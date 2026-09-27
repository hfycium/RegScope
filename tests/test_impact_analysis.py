import json
from pathlib import Path

from regscope.impact_analysis import write_impact


def test_write_impact_creates_json_artifact(tmp_path: Path):
    result = {"schema_version": 1, "changed_functions": [], "warnings": []}
    path = write_impact(result, tmp_path / "nested" / "impact.json")

    assert path == tmp_path / "nested" / "impact.json"
    assert json.loads(path.read_text(encoding="utf-8")) == result
