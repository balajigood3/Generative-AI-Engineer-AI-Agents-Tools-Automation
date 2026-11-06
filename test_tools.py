from app.tools import safe_calculate


def test_basic_arithmetic():
    assert safe_calculate("2 + 3 * 4") == "14"


def test_rejects_code_execution():
    result = safe_calculate("__import__('os').system('echo unsafe')")
    assert result.startswith("Calculation error:")
