from pathlib import Path

from regscope.static_analysis import build_direct_call_graph, discover_fastapi_endpoints, find_affected_endpoints


def test_discovers_routes_and_direct_calls(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    (app / "api.py").write_text(
        "from app.service import Service\nrouter = object()\n@router.post('/items')\ndef create(service: Service):\n    return service.run()\n",
        encoding="utf-8",
    )
    (app / "service.py").write_text(
        "class Service:\n    def run(self):\n        return self.helper()\n    def helper(self):\n        return 1\n",
        encoding="utf-8",
    )

    assert discover_fastapi_endpoints(tmp_path) == [
        {"function_id": "app.api:create", "method": "POST", "path": "/items"}
    ]
    assert build_direct_call_graph(tmp_path) == {
        "app.api:create": ["app.service:Service.run"],
        "app.service:Service.helper": [],
        "app.service:Service.run": ["app.service:Service.helper"],
    }
    assert find_affected_endpoints(tmp_path, ["app.service:Service.helper"]) == [
        {
            "changed_function": "app.service:Service.helper",
            "method": "POST",
            "path": "/items",
            "call_path": ["app.api:create", "app.service:Service.run", "app.service:Service.helper"],
        }
    ]
