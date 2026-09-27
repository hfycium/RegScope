from __future__ import annotations

import ast
from pathlib import Path


_HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


def discover_fastapi_endpoints(project_root: str | Path) -> list[dict[str, str]]:
    """Discover directly decorated FastAPI endpoint functions in ``app/``."""
    endpoints: list[dict[str, str]] = []
    for path in _app_python_files(project_root):
        module = _module_name(path, project_root)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                route = _route_decorator(decorator)
                if route is not None:
                    method, path_value = route
                    endpoints.append({"function_id": f"{module}:{node.name}", "method": method, "path": path_value})
    return sorted(endpoints, key=lambda endpoint: (endpoint["method"], endpoint["path"], endpoint["function_id"]))


def build_direct_call_graph(project_root: str | Path) -> dict[str, list[str]]:
    """Build a bounded direct-call graph for functions defined under ``app/``."""
    root = Path(project_root).resolve()
    modules = _load_modules(root)
    defined = {
        function[0]
        for module in modules.values()
        for function in module["functions"].values()
    }
    graph: dict[str, list[str]] = {}
    for module_name, module in modules.items():
        imports = module["imports"]
        for function_id, node, class_name in module["functions"].values():
            parameter_types = {
                argument.arg: _annotation_to_symbol(argument.annotation, module_name, imports)
                for argument in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
                if argument.annotation is not None
            }
            callees = {
                callee
                for call in ast.walk(node)
                if isinstance(call, ast.Call)
                if (callee := _resolve_call(call.func, module_name, class_name, imports, parameter_types, defined))
                is not None
            }
            graph[function_id] = sorted(callees)
    return dict(sorted(graph.items()))


def find_affected_endpoints(project_root: str | Path, changed_functions: list[str]) -> list[dict[str, object]]:
    """Return reverse call paths from changed functions to FastAPI endpoints."""
    graph = build_direct_call_graph(project_root)
    endpoints = discover_fastapi_endpoints(project_root)
    reverse: dict[str, set[str]] = {}
    for caller, callees in graph.items():
        for callee in callees:
            reverse.setdefault(callee, set()).add(caller)

    endpoint_by_function = {endpoint["function_id"]: endpoint for endpoint in endpoints}
    affected: list[dict[str, object]] = []
    for changed in sorted(set(changed_functions)):
        pending: list[tuple[str, list[str]]] = [(changed, [changed])]
        seen = {changed}
        while pending:
            current, path = pending.pop(0)
            if current in endpoint_by_function:
                endpoint = endpoint_by_function[current]
                affected.append({
                    "changed_function": changed,
                    "method": endpoint["method"],
                    "path": endpoint["path"],
                    "call_path": list(reversed(path)),
                })
            for caller in sorted(reverse.get(current, ())):
                if caller not in seen:
                    seen.add(caller)
                    pending.append((caller, [*path, caller]))
    return sorted(affected, key=lambda item: (str(item["method"]), str(item["path"]), str(item["changed_function"])))


def _app_python_files(project_root: str | Path) -> list[Path]:
    root = Path(project_root).resolve()
    return sorted((root / "app").rglob("*.py"))


def _module_name(path: Path, project_root: str | Path) -> str:
    return ".".join(path.resolve().relative_to(Path(project_root).resolve()).with_suffix("").parts)


def _route_decorator(node: ast.AST) -> tuple[str, str] | None:
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
        return None
    if node.func.attr.lower() not in _HTTP_METHODS or not node.args:
        return None
    if not isinstance(node.func.value, ast.Name) or node.func.value.id not in {"app", "router"}:
        return None
    if not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
        return None
    return node.func.attr.upper(), node.args[0].value


def _load_modules(root: Path) -> dict[str, dict]:
    modules: dict[str, dict] = {}
    for path in _app_python_files(root):
        module_name = _module_name(path, root)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports: dict[str, str] = {}
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module:
                for imported in node.names:
                    imports[imported.asname or imported.name] = f"{node.module}:{imported.name}"
        functions: dict[str, tuple[str, ast.FunctionDef | ast.AsyncFunctionDef, str | None]] = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions[node.name] = (f"{module_name}:{node.name}", node, None)
            elif isinstance(node, ast.ClassDef):
                for member in node.body:
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        functions[f"{node.name}.{member.name}"] = (f"{module_name}:{node.name}.{member.name}", member, node.name)
        modules[module_name] = {"imports": imports, "functions": functions}
    return modules


def _annotation_to_symbol(annotation: ast.AST, module: str, imports: dict[str, str]) -> str | None:
    if isinstance(annotation, ast.Name):
        return imports.get(annotation.id, f"{module}:{annotation.id}")
    return None


def _resolve_call(node: ast.AST, module: str, class_name: str | None, imports: dict[str, str], parameter_types: dict[str, str | None], defined: set[str]) -> str | None:
    candidate: str | None = None
    if isinstance(node, ast.Name):
        candidate = imports.get(node.id, f"{module}:{node.id}")
    elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        if node.value.id == "self" and class_name:
            candidate = f"{module}:{class_name}.{node.attr}"
        elif parameter_types.get(node.value.id):
            candidate = f"{parameter_types[node.value.id]}.{node.attr}"
    return candidate if candidate in defined else None
