import json
import subprocess
from pathlib import Path

from regscope.impact_analysis import analyse_impact, write_impact


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _target_repo(root: Path) -> None:
    _git(root, "init")
    _git(root, "config", "user.email", "regscope@example.test")
    _git(root, "config", "user.name", "RegScope Test")
    app = root / "app"
    app.mkdir()
    (app / "api.py").write_text(
        "from app.service import Service\n"
        "router = object()\n"
        "class Dependency: pass\n"
        "@router.get('/items')\n"
        "async def list_items(service: Service):\n"
        "    return service.list_items()\n",
        encoding="utf-8",
    )
    (app / "service.py").write_text(
        "class Service:\n"
        "    def list_items(self):\n"
        "        return 1\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text("baseline\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "baseline")


def test_write_impact_creates_json_artifact(tmp_path: Path):
    result = {"schema_version": 1, "changed_functions": [], "warnings": []}
    path = write_impact(result, tmp_path / "nested" / "impact.json")

    assert path == tmp_path / "nested" / "impact.json"
    assert json.loads(path.read_text(encoding="utf-8")) == result


def test_changed_service_function_traces_to_async_endpoint(tmp_path: Path):
    _target_repo(tmp_path)
    base = _git(tmp_path, "rev-parse", "HEAD")
    service = tmp_path / "app" / "service.py"
    service.write_text(
        "class Service:\n"
        "    def list_items(self):\n"
        "        return 2\n",
        encoding="utf-8",
    )
    _git(tmp_path, "add", "app/service.py")
    _git(tmp_path, "commit", "-m", "change service behavior")

    result = analyse_impact(tmp_path, base, "HEAD")

    assert result["changed_functions"] == ["app.service:Service.list_items"]
    assert result["affected_endpoints"] == [
        {
            "changed_function": "app.service:Service.list_items",
            "method": "GET",
            "path": "/items",
            "call_path": ["app.api:list_items", "app.service:Service.list_items"],
        }
    ]


def test_non_app_change_has_no_business_impact(tmp_path: Path):
    _target_repo(tmp_path)
    base = _git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "README.md").write_text("documentation only\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "update documentation")

    result = analyse_impact(tmp_path, base, "HEAD")

    assert result["changed_files"] == ["README.md"]
    assert result["changed_functions"] == []
    assert result["affected_endpoints"] == []
    assert result["warnings"] == []
