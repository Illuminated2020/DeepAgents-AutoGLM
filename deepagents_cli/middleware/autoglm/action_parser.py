"""Action parser for AutoGLM phone agent responses.

This module provides functions to parse AI model responses and extract action commands.
The model outputs responses in a two-part format:
1. Thinking process (reasoning about what to do)
2. Action command (actual operation to execute)

Source: Adapted from Open-AutoGLM project
Original: https://github.com/zai-org/Open-AutoGLM
Files: phone_agent/model/client.py, phone_agent/actions/handler.py
"""

import ast
import re
from typing import Any


def parse_response(response: str) -> tuple[str, str]:
    """Parse model response into thinking and action parts.

    The model can output responses in multiple formats, handled by priority:
    1. Modern format with finish(message=...) - task completion
    2. Modern format with do(action=...) - execute action
    3. Legacy XML format with <think>...</think><answer>...</answer>
    4. Fallback: treat entire response as action

    Args:
        response: Raw response string from the vision-language model.

    Returns:
        Tuple of (thinking, action) where:
        - thinking: The model's reasoning process (may be empty)
        - action: The action command to execute

    Examples:
        >>> thinking, action = parse_response("Let me tap the button\\ndo(action=\"Tap\", element=[500, 300])")
        >>> print(thinking)
        "Let me tap the button"
        >>> print(action)
        "do(action=\"Tap\", element=[500, 300])"
    """
    # Rule 1: Check for finish(message=
    if "finish(message=" in response:
        parts = response.split("finish(message=", 1)
        thinking = parts[0].strip()
        action = "finish(message=" + parts[1]
        return thinking, action

    # Rule 2: Check for do(action=
    if "do(action=" in response:
        parts = response.split("do(action=", 1)
        thinking = parts[0].strip()
        action = "do(action=" + parts[1]
        return thinking, action

    # Rule 3: Fallback to legacy XML tag parsing
    if "<answer>" in response:
        parts = response.split("<answer>", 1)
        thinking = parts[0].replace("<think>", "").replace("</think>", "").strip()
        action = parts[1].replace("</answer>", "").strip()
        return thinking, action

    # Rule 4: No markers found, return entire response as action
    return "", response.strip()


def parse_action(action_str: str) -> dict[str, Any]:
    """Parse action string into a structured dictionary.

    Supports two main action formats:
    1. do(action="ActionName", param1=value1, param2=value2, ...)
    2. finish(message="Task completed")

    The function uses AST parsing for safety instead of eval().

    Args:
        action_str: Action command string from the model.

    Returns:
        Dictionary with action details. Always includes "_metadata" key:
        - For "do" actions: {"_metadata": "do", "action": "Tap", "element": [x, y], ...}
        - For "finish" actions: {"_metadata": "finish", "message": "..."}

    Raises:
        ValueError: If the action string cannot be parsed.

    Supported action types (18 total):
        - Launch: Launch an app
        - Tap: Single tap on element
        - Double Tap: Double tap on element
        - Long Press: Press and hold element
        - Type: Input text via keyboard
        - Type_Name: Alias for Type (name input)
        - Swipe: Swipe from start to end coordinates
        - Back: Press back button
        - Home: Press home button
        - Wait: Wait for specified duration
        - Take_over: Request human intervention
        - Note: Record page content (placeholder)
        - Call_API: Call API for summarization (placeholder)
        - Interact: Request user choice
        - Check: Verify element exists (placeholder)
        - Select: Select from options (placeholder)
        - Scroll: Scroll in direction (alias for Swipe)
        - Open: Open URL or deep link (placeholder)
    """
    try:
        action_str = action_str.strip()

        # Special handling for Type actions (text may contain quotes and commas)
        if action_str.startswith('do(action="Type"') or action_str.startswith(
            'do(action="Type_Name"'
        ):
            # Extract text parameter manually to avoid parsing issues
            text_match = re.search(r'text="([^"]*)"', action_str)
            if text_match:
                text = text_match.group(1)
                action = {"_metadata": "do", "action": "Type", "text": text}
                return action
            # Fallback: try to find text with single quotes
            text_match = re.search(r"text='([^']*)'", action_str)
            if text_match:
                text = text_match.group(1)
                action = {"_metadata": "do", "action": "Type", "text": text}
                return action
            msg = "Type action missing text parameter"
            raise ValueError(msg)

        # Handle do(...) actions using AST parsing
        if action_str.startswith("do("):
            try:
                # Parse the function call as an expression
                tree = ast.parse(action_str, mode="eval")
                if not isinstance(tree.body, ast.Call):
                    msg = "Expected a function call"
                    raise ValueError(msg)

                call = tree.body
                # Extract keyword arguments safely
                action: dict[str, Any] = {"_metadata": "do"}
                for keyword in call.keywords:
                    key = keyword.arg
                    # Use literal_eval to safely evaluate the value
                    value = ast.literal_eval(keyword.value)
                    action[key] = value

                return action
            except (SyntaxError, ValueError) as e:
                msg = f"Failed to parse do() action: {e}"
                raise ValueError(msg) from e

        # Handle finish(...) actions
        if action_str.startswith("finish("):
            # Strategy 1: Find ") at the end - handles messages with internal quotes
            # Look for finish(message="...") where ... can contain any characters including "
            # We find the LAST occurrence of ") to handle nested quotes
            if 'message="' in action_str:
                start_idx = action_str.index('message="') + len('message="')
                # Find the last ") in the string
                if '")' in action_str[start_idx:]:
                    end_idx = action_str.rindex('")')
                    message = action_str[start_idx:end_idx]
                    return {"_metadata": "finish", "message": message}

            # Strategy 2: Try single quotes
            if "message='" in action_str:
                start_idx = action_str.index("message='") + len("message='")
                if "')" in action_str[start_idx:]:
                    end_idx = action_str.rindex("')")
                    message = action_str[start_idx:end_idx]
                    return {"_metadata": "finish", "message": message}

            # Strategy 3: Fallback - extract everything after message= and clean it up
            if "message=" in action_str:
                message_raw = action_str.split("message=", 1)[1].strip()
                # Remove surrounding quotes and trailing )
                message = message_raw.strip('"').strip("'").rstrip(")")
                return {"_metadata": "finish", "message": message}

            msg = "finish action missing message parameter"
            raise ValueError(msg)

        # Unknown action format
        msg = f"Unknown action format: {action_str}"
        raise ValueError(msg)

    except Exception as e:
        msg = f"Failed to parse action '{action_str}': {e}"
        raise ValueError(msg) from e


def is_finish_action(action: dict[str, Any]) -> bool:
    """Check if an action indicates task completion.

    Args:
        action: Parsed action dictionary from parse_action().

    Returns:
        True if the action is a finish action, False otherwise.

    Examples:
        >>> action = {"_metadata": "finish", "message": "Task done"}
        >>> is_finish_action(action)
        True
        >>> action = {"_metadata": "do", "action": "Tap", "element": [500, 300]}
        >>> is_finish_action(action)
        False
    """
    return action.get("_metadata") == "finish"


def get_action_name(action: dict[str, Any]) -> str | None:
    """Extract the action name from a parsed action dictionary.

    Args:
        action: Parsed action dictionary from parse_action().

    Returns:
        Action name string (e.g., "Tap", "Swipe", "Launch") or None for finish actions.

    Examples:
        >>> action = {"_metadata": "do", "action": "Tap", "element": [500, 300]}
        >>> get_action_name(action)
        "Tap"
        >>> action = {"_metadata": "finish", "message": "Done"}
        >>> get_action_name(action)
        None
    """
    if action.get("_metadata") == "do":
        return action.get("action")
    return None


def validate_action(action: dict[str, Any]) -> tuple[bool, str | None]:
    """Validate that a parsed action has required parameters.

    Args:
        action: Parsed action dictionary from parse_action().

    Returns:
        Tuple of (is_valid, error_message).
        - is_valid: True if action is valid, False otherwise
        - error_message: None if valid, error description if invalid

    Examples:
        >>> action = {"_metadata": "do", "action": "Tap", "element": [500, 300]}
        >>> valid, error = validate_action(action)
        >>> print(valid)
        True
    """
    metadata = action.get("_metadata")

    # Validate finish actions
    if metadata == "finish":
        if "message" not in action:
            return False, "finish action missing 'message' parameter"
        return True, None

    # Validate do actions
    if metadata == "do":
        action_name = action.get("action")
        if not action_name:
            return False, "do action missing 'action' parameter"

        # Validate parameters based on action type
        if action_name in ["Tap", "Double Tap", "Long Press"]:
            if "element" not in action:
                return False, f"{action_name} action missing 'element' parameter"
            element = action.get("element")
            if not isinstance(element, list) or len(element) != 2:
                return False, f"{action_name} action 'element' must be [x, y] coordinates"

        elif action_name == "Swipe":
            if "start" not in action or "end" not in action:
                return False, "Swipe action missing 'start' or 'end' parameter"
            start = action.get("start")
            end = action.get("end")
            if not isinstance(start, list) or len(start) != 2:
                return False, "Swipe action 'start' must be [x, y] coordinates"
            if not isinstance(end, list) or len(end) != 2:
                return False, "Swipe action 'end' must be [x, y] coordinates"

        elif action_name in ["Type", "Type_Name"]:
            if "text" not in action:
                return False, f"{action_name} action missing 'text' parameter"

        elif action_name == "Launch":
            if "app" not in action:
                return False, "Launch action missing 'app' parameter"

        elif action_name in [
            "Back",
            "Home",
            "Wait",
            "Take_over",
            "Note",
            "Call_API",
            "Interact",
        ]:
            # These actions don't require additional parameters
            pass

        else:
            # Unknown action type, but don't fail validation
            # (allows for extension without code changes)
            pass

        return True, None

    # Unknown metadata type
    return False, f"Unknown action metadata: {metadata}"
