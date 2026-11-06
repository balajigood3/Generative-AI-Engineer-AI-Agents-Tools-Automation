"""Agent tools. Calculator accepts only basic arithmetic expressions."""
import ast
import operator

_ALLOWED = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def safe_calculate(expression: str) -> str:
    if len(expression) > 100:
        return "Expression too long."
    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED:
            return _ALLOWED[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED:
            return _ALLOWED[type(node.op)](evaluate(node.operand))
        raise ValueError("Only basic arithmetic is allowed.")
    try:
        return str(evaluate(ast.parse(expression, mode="eval")))
    except Exception as exc:
        return f"Calculation error: {exc}"
