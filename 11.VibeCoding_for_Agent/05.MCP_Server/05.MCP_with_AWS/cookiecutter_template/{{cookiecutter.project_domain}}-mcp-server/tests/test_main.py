# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for main module."""

from awslabs.{{ cookiecutter.project_domain | lower | replace(' ', '_') | replace('-', '_') }}_mcp_server.server import mcp


def test_mcp_server_exists():
    """Test that MCP server instance exists."""
    assert mcp is not None
    assert mcp.name == "{{ cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') }}"
