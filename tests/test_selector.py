from regscope.selector import select_tests


def test_selects_only_tests_covering_changed_function():
    mapping = {"mappings": [{"test_id": "a", "functions": ["app.s:f"]}, {"test_id": "b", "functions": ["app.s:g"]}]}
    result = select_tests(mapping, {"changed_functions": ["app.s:f"], "affected_endpoints": []})
    assert result["strategy"] == "coverage-intersection"
    assert result["selected_tests"] == ["a"]
    assert result["unselected_tests"] == ["b"]
    assert result["reasons"] == {"a": ["app.s:f"]}


def test_module_change_falls_back_to_all_tests():
    mapping = {"mappings": [{"test_id": "a", "functions": []}, {"test_id": "b", "functions": []}]}
    result = select_tests(mapping, {"module_level_changes": {"app/s.py": [1]}, "warnings": []})
    assert result["strategy"] == "conservative-fallback"
    assert result["selected_tests"] == ["a", "b"]
    assert result["unselected_tests"] == []


def test_selects_test_covering_affected_endpoint():
    mapping = {"mappings": [{"test_id": "a", "functions": ["app.api:create"]}]}
    result = select_tests(mapping, {"changed_functions": [], "affected_endpoints": [{"call_path": ["app.api:create", "app.s:f"]}]})
    assert result["selected_tests"] == ["a"]


def test_falls_back_to_all_tests_when_no_test_matches_change():
    mapping = {"mappings": [{"test_id": "a", "functions": ["app.s:f"]}, {"test_id": "b", "functions": ["app.s:g"]}]}
    result = select_tests(mapping, {"changed_files": ["app/service.py"], "changed_functions": ["app.s:unknown"], "affected_endpoints": []})
    assert result["strategy"] == "conservative-fallback"
    assert result["selected_tests"] == ["a", "b"]
    assert result["unselected_tests"] == []
    assert all("No tests matched" in reason[0] for reason in result["reasons"].values())
