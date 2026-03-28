from mcp.server.fastmcp import FastMCP

# FastMCP is the high-level, decorator-based API
# (analogous to FastAPI for HTTP servers)
mcp = FastMCP("My First Server")


# ─── TOOL 1: Calculator ───────────────────────────────────────────────────────

@mcp.tool()
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.

    Args:
        expression: A mathematical expression like '2 + 2' or '(10 * 5) / 2'

    Returns:
        The result as a string, or an error message.
    """
    # Restrict to safe operations
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return "Error: Only basic arithmetic is allowed."
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: {str(e)}"


# ─── TOOL 2: Unit Converter ───────────────────────────────────────────────────

CONVERSIONS = {
    ("km", "miles"): 0.621371,
    ("miles", "km"): 1.60934,
    ("kg", "lbs"): 2.20462,
    ("lbs", "kg"): 0.453592,
    ("celsius", "fahrenheit"): None,  # special case
    ("fahrenheit", "celsius"): None,  # special case
}

@mcp.tool()
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert a value from one unit to another.

    Args:
        value: The numeric value to convert.
        from_unit: Source unit (km, miles, kg, lbs, celsius, fahrenheit).
        to_unit: Target unit (km, miles, kg, lbs, celsius, fahrenheit).

    Returns:
        Converted value with units.
    """
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    if from_unit == "celsius" and to_unit == "fahrenheit":
        result = (value * 9 / 5) + 32
    elif from_unit == "fahrenheit" and to_unit == "celsius":
        result = (value - 32) * 5 / 9
    elif (from_unit, to_unit) in CONVERSIONS:
        result = value * CONVERSIONS[(from_unit, to_unit)]
    else:
        return f"Error: Conversion from '{from_unit}' to '{to_unit}' not supported."

    return f"{value} {from_unit} = {result:.4f} {to_unit}"


# ─── RESOURCE: Supported Conversions List ────────────────────────────────────

@mcp.resource("info://supported-conversions")
def supported_conversions() -> str:
    """Lists all supported unit conversions."""
    pairs = [f"{a} ↔ {b}" for a, b in CONVERSIONS.keys()]
    return "Supported unit conversions:\n" + "\n".join(pairs)


if __name__ == "__main__":
    mcp.run()