# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for package initialization."""

import awslabs.{{ cookiecutter.project_domain | lower | replace(' ', '_') | replace('-', '_') }}_mcp_server


def test_version():
    """Test that version is defined."""
    assert hasattr(
        awslabs.{{ cookiecutter.project_domain | lower | replace(' ', '_') | replace('-', '_') }}_mcp_server,
        "__version__",
    )
    assert isinstance(
        awslabs.{{ cookiecutter.project_domain | lower | replace(' ', '_') | replace('-', '_') }}_mcp_server.__version__,
        str,
    )
