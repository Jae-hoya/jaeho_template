# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test package initialization."""

from awslabs.seoul_opendata_mcp_server import __version__


def test_version():
    """Test version is defined."""
    assert __version__ == "0.0.0"
