from pathlib import Path
import py_compile


def test_python_sources_compile() -> None:
    root = Path(__file__).parents[1]
    paths = list((root / "src").rglob("*.py")) + [root / "app.py"]
    for path in paths:
        py_compile.compile(str(path), doraise=True)
