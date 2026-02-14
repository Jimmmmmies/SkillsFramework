import asyncio
import os
import shutil
import sys
import json
import time
from typing import Optional

from app.context import ToolContext
from app.exceptions import ToolException
from app.tools.base import tool

def _resolve_executable() -> Optional[str]:
    if sys.platform.startswith("win"):
        return os.environ.get("COMSPEC") or "cmd.exe"
    return shutil.which("bash") or os.environ.get("SHELL")

def _decode_output(data: Optional[bytes]) -> str:
    if not data:
        return ""
    return data.decode("utf-8", errors="replace")
    
@tool
async def bash(command: str, context: ToolContext) -> str:
    """
    Execute a bash command asynchronously and return the result as a JSON string.
    It supports different operating systems(bash on Unix-like systems, cmd.exe on Windows).
    
    Use this for:
    - Running scripts in skill file (e.g. `uv run -m scripts.script_name [args]`)
    - Installing dependencies
    - File operations
    - Reading directory structure (e.g. `ls -la` or `dir`)
    - Any shell command

    Important for Skills:
    - Script code does NOT enter the context, only the output does
    - Follow the skill's instructions for exact command syntax
    
    Args:
        command (str): The bash command to execute.
        context: (ToolContext) The shared runtime container when executing tools.
                 It provides common dependencies (e.g. SkillLoader, working_dir) 
                 that tools stay focused on logic without managing global resources.
    Returns:
        str: A JSON string containing stdout, stderr, exit_code, and duration_ms.
    """
    if not command or not command.strip():
        raise ToolException("command must be a non-empty string")

    working_dir = None
    if context and context.working_dir:
        working_dir = str(context.working_dir)

    executable = _resolve_executable()
    start_time = time.monotonic()

    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_dir,
            executable=executable,
        )
    except FileNotFoundError as exc:
        raise ToolException(str(exc))
    except Exception as exc:
        raise ToolException(f"Failed to start command: {exc}")

    try:
        stdout_data, stderr_data = await asyncio.wait_for(
            process.communicate(), 
            timeout=300,
        )
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        duration_ms = int((time.monotonic() - start_time) * 1000)
        result = {
            "stdout": "",
            "stderr": "Command timed out after 300 seconds.",
            "exit_code": process.returncode,
            "duration_ms": duration_ms,
        }
        return json.dumps(result, ensure_ascii=False)
    
    duration_ms = int((time.monotonic() - start_time) * 1000)
    result = {
        "stdout": _decode_output(stdout_data),
        "stderr": _decode_output(stderr_data),
        "exit_code": process.returncode,
        "duration_ms": duration_ms,
    }
    return json.dumps(result, ensure_ascii=False)
