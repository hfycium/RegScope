
from pathlib import Path

from regscope.function_mapper import map_executed_lines_to_functions


def write_source(tmp_path: Path, code: str) -> Path:
    source_file = tmp_path / "sample.py"
    source_file.write_text(code, encoding="utf-8")
    return source_file
#辅助函数而已，为了避免重复写这部分代码

def test_top_level_function_hit_and_miss(tmp_path: Path):
    source_file = write_source(
        tmp_path,
        """\
def hit():
    return 1

def miss():
    return 2
""",
    )

    result = map_executed_lines_to_functions(
        source_file,
        [2],
        project_root=tmp_path,
    )

    assert result == ["sample:hit"]


def test_class_method_uses_qualified_name(tmp_path: Path):
    source_file = write_source(
        tmp_path,
        """\
class OrderService:
    def create_order(self):
        return 1
""",
    )

    result = map_executed_lines_to_functions(
        source_file,
        [3],
        project_root=tmp_path,
    )

    assert result == ["sample:OrderService.create_order"]


def test_nested_function(tmp_path: Path):
    source_file = write_source(
        tmp_path,
        """\
def outer():
    def inner():
        return 1

    return inner()
""",
    )

    result = map_executed_lines_to_functions(
        source_file,
        [3],
        project_root=tmp_path,
    )

    assert result == [
        "sample:outer",
        "sample:outer.inner",
    ]


def test_same_function_multiple_executed_lines_only_once(tmp_path: Path):
    source_file = write_source(
        tmp_path,
        """\
def calculate():
    x = 1
    y = 2
    return x + y
""",
    )

    result = map_executed_lines_to_functions(
        source_file,
        [2, 3, 4],
        project_root=tmp_path,
    )

    assert result == ["sample:calculate"]


def test_output_order_is_stable(tmp_path: Path):
    source_file = write_source(
        tmp_path,
        """\
def zebra():
    return 1

def apple():
    return 2
""",
    )

    result = map_executed_lines_to_functions(
        source_file,
        [2, 5],
        project_root=tmp_path,
    )

    assert result == [
        "sample:apple",
        "sample:zebra",
    ]


def test_empty_executed_lines_returns_empty_list(tmp_path: Path):
    source_file = write_source(
        tmp_path,
        """\
def hello():
    return "hello"
""",
    )

    result = map_executed_lines_to_functions(
        source_file,
        [],
        project_root=tmp_path,
    )

    assert result == []
