import json
from pathlib import Path
from typing import Optional, Literal

from app.context import ToolContext
from app.exceptions import ToolException
from app.tools.base import tool

def _resolve_path(path: str, context: Optional[ToolContext]) -> Path:
    if not path or not path.strip():
        raise ToolException("path must be a non-empty string")

    candidate = Path(path)
    if candidate.is_absolute():
        return candidate

    base_dir = context.working_dir if context and context.working_dir else Path.cwd()
    return (base_dir / candidate).resolve()

@tool
async def file_edit(
    action: Literal["read", "write", "edit"],
    path: str,
    content: Optional[str] = None,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    encoding: str = "utf-8",
    context: Optional[ToolContext] = None,
) -> str:
    """
    Read, write, or edit a text file on disk.

    Note for LLM callers: when writing or editing, you MUST provide `content`
    as a valid JSON string value inside the tool arguments. Do not send raw,
    unescaped text.

    Use this tool to:
    - Read a file's content.
    - Write (overwrite) a file with new content.
    - Edit a file by replacing a line range with new content.

    Args:
        action: The operation to perform: "read", "write", or "edit".
        path: Absolute or relative path to the file.
        content: Content to write or to replace the specified line range with.
        start_line: 1-based start line for "edit" action (inclusive).
        end_line: 1-based end line for "edit" action (inclusive).
        encoding: Text encoding to use when reading/writing.
        context: ToolContext providing working_dir for relative paths.

    Returns:
        A JSON string describing the operation result, including path and content/summary.
    """
    file_path = _resolve_path(path, context)

    if action == "read":
        if not file_path.exists() or not file_path.is_file():
            raise ToolException(f"File not found: {file_path}")
        try:
            text = file_path.read_text(encoding=encoding)
        except Exception as exc:
            raise ToolException(f"Failed to read file: {exc}")

        line_count = text.count("\n") + (1 if text else 0)
        return json.dumps(
            {
                "action": action,
                "path": str(file_path),
                "encoding": encoding,
                "line_count": line_count,
                "content": text,
            },
            ensure_ascii=False,
        )

    if action == "write":
        if content is None:
            raise ToolException("content is required for write action")

        parent_dir = file_path.parent
        if not parent_dir.exists():
            raise ToolException(f"Parent directory does not exist: {parent_dir}")

        try:
            file_path.write_text(content, encoding=encoding)
        except Exception as exc:
            raise ToolException(f"Failed to write file: {exc}")

        line_count = content.count("\n") + (1 if content else 0)
        return json.dumps(
            {
                "action": action,
                "path": str(file_path),
                "encoding": encoding,
                "line_count": line_count,
            },
            ensure_ascii=False,
        )

    if action == "edit":
        if content is None:
            raise ToolException("content is required for edit action")
        if start_line is None or end_line is None:
            raise ToolException("start_line and end_line are required for edit action")
        if start_line < 1 or end_line < 1 or end_line < start_line:
            raise ToolException(
                "start_line/end_line must be positive and end_line >= start_line"
            )

        if not file_path.exists() or not file_path.is_file():
            raise ToolException(f"File not found: {file_path}")

        try:
            lines = file_path.read_text(encoding=encoding).splitlines(keepends=True)
        except Exception as exc:
            raise ToolException(f"Failed to read file: {exc}")

        if end_line > len(lines):
            raise ToolException(
                f"end_line {end_line} exceeds total lines {len(lines)} for file {file_path}"
            )

        replacement_lines = content.splitlines(keepends=True)
        if content and not content.endswith(("\n", "\r")):
            replacement_lines = [content]

        start_index = start_line - 1
        end_index = end_line
        new_lines = lines[:start_index] + replacement_lines + lines[end_index:]

        try:
            file_path.write_text("".join(new_lines), encoding=encoding)
        except Exception as exc:
            raise ToolException(f"Failed to write file: {exc}")

        return json.dumps(
            {
                "action": action,
                "path": str(file_path),
                "encoding": encoding,
                "line_count": len(new_lines),
                "replaced_range": [start_line, end_line],
            },
            ensure_ascii=False,
        )

    raise ToolException(f"Unsupported action: {action}")
