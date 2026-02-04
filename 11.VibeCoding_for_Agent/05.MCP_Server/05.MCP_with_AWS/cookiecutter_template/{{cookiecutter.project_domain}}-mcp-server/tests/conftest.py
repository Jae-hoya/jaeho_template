# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_data():
    """Sample data fixture for tests."""
    return {"key": "value", "number": 42}
