from app.tools.base import tool

_TERMINATE_DESCRIPTION = (
    "Terminate the interaction when the request is met OR if the assistant cannot proceed further with the task. "
    "When you have finished all the tasks, call this tool to end the work."
)

@tool(
    name="terminate",
    description=_TERMINATE_DESCRIPTION,
)
async def terminate(status: str) -> str:
    """
    Finish the current execution.

    Args:
        status: The finish status of the interaction. Must be 'success' or 'failure'.
    """
    allowed = {"success", "failure"}
    if status not in allowed:
        raise ValueError(f"status must be one of {sorted(allowed)}")

    return f"The interaction has been completed with status: {status}"
