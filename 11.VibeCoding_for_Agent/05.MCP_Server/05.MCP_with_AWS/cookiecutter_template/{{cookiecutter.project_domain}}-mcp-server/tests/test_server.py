# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for server tools."""

import pytest

from awslabs.{{ cookiecutter.project_domain | lower | replace(' ', '_') | replace('-', '_') }}_mcp_server.server import (
    example_tool,
    math_tool,
)


class TestExampleTool:
    """Tests for example_tool."""

    async def test_example_tool_returns_greeting(self):
        """Test that example_tool returns expected greeting."""
        result = example_tool("test query")
        assert result == "Hello! You asked: test query"

    async def test_example_tool_with_different_query(self):
        """Test example_tool with different query."""
        result = example_tool("another test")
        assert result == "Hello! You asked: another test"

    async def test_example_tool_not_equal_to_wrong_response(self):
        """Test that example_tool doesn't return incorrect response."""
        result = example_tool("test")
        assert result != "Wrong response"


class TestMathTool:
    """Tests for math_tool."""

    def test_add_integers(self):
        """Test addition with integers."""
        result = math_tool("add", 5, 3)
        assert result == 8

    def test_add_floats(self):
        """Test addition with floats."""
        result = math_tool("add", 5.5, 3.2)
        assert result == pytest.approx(8.7)

    def test_subtract_integers(self):
        """Test subtraction with integers."""
        result = math_tool("subtract", 10, 4)
        assert result == 6

    def test_subtract_floats(self):
        """Test subtraction with floats."""
        result = math_tool("subtract", 10.5, 4.2)
        assert result == pytest.approx(6.3)

    def test_multiply_integers(self):
        """Test multiplication with integers."""
        result = math_tool("multiply", 6, 7)
        assert result == 42

    def test_multiply_floats(self):
        """Test multiplication with floats."""
        result = math_tool("multiply", 2.5, 4.0)
        assert result == pytest.approx(10.0)

    def test_divide_integers(self):
        """Test division with integers."""
        result = math_tool("divide", 10, 2)
        assert result == 5.0

    def test_divide_floats(self):
        """Test division with floats."""
        result = math_tool("divide", 10.0, 4.0)
        assert result == pytest.approx(2.5)

    def test_divide_by_zero_raises_error(self):
        """Test that division by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            math_tool("divide", 10, 0)

    def test_invalid_operation_raises_error(self):
        """Test that invalid operation raises ValueError."""
        with pytest.raises(ValueError, match="Invalid operation"):
            math_tool("invalid", 5, 3)
