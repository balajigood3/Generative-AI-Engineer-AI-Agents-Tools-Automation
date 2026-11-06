import ast
import operator
from .database import get_connection

# Safe arithmetic: only numeric constants and explicitly allowed operators.
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Mod: operator.mod,
}

def _safe_calculate(expression: str):
    if len(expression) > 100:
        raise ValueError("Expression is too long.")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
            left, right = evaluate(node.left), evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("Exponent is too large.")
            result = _OPERATORS[type(node.op)](left, right)
            if abs(result) > 1e100:
                raise ValueError("Result is too large.")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](evaluate(node.operand))
        raise ValueError("Only basic arithmetic is allowed.")

    return evaluate(ast.parse(expression, mode="eval"))

def calculate(expression: str):
    try:
        return {"success": True, "result": _safe_calculate(expression)}
    except (SyntaxError, ValueError, ZeroDivisionError, OverflowError) as exc:
        return {"success": False, "error": str(exc)}

def add_task(description: str):
    description = description.strip()
    if not description or len(description) > 300:
        return {"success": False, "error": "Task must contain 1–300 characters."}
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (description) VALUES (?)", (description,)
        )
        task_id = cursor.lastrowid
    return {"success": True, "task_id": task_id, "description": description}

def list_tasks():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, description, status, created_at FROM tasks ORDER BY id"
        ).fetchall()
    return {"success": True, "tasks": [dict(row) for row in rows]}

def complete_task(task_id: int):
    if not isinstance(task_id, int) or task_id < 1:
        return {"success": False, "error": "Task ID must be a positive integer."}
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET status = 'completed' WHERE id = ? AND status = 'pending'",
            (task_id,)
        )
        if cursor.rowcount == 0:
            exists = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if not exists:
                return {"success": False, "error": f"Task {task_id} was not found."}
            return {"success": False, "error": f"Task {task_id} is already completed."}
    return {"success": True, "task_id": task_id, "status": "completed"}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "calculate",
        "description": "Calculate a basic arithmetic expression.",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "add_task",
        "description": "Add a task to the user's persistent task list.",
        "parameters": {
            "type": "object",
            "properties": {"description": {"type": "string"}},
            "required": ["description"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "list_tasks",
        "description": "List all saved tasks and their statuses.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "complete_task",
        "description": "Mark a pending task as completed using its task ID.",
        "parameters": {
            "type": "object",
            "properties": {"task_id": {"type": "integer"}},
            "required": ["task_id"],
            "additionalProperties": False
        },
        "strict": True
    }
]

TOOL_FUNCTIONS = {
    "calculate": calculate,
    "add_task": add_task,
    "list_tasks": list_tasks,
    "complete_task": complete_task,
}
