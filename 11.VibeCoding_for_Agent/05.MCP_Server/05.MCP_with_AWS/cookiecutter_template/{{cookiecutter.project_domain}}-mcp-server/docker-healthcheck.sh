#!/bin/sh
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

SERVER="{{ cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') }}"

if pgrep -f "/app/.venv/bin/awslabs.$SERVER" > /dev/null; then
    echo "Server $SERVER is running"
    exit 0
else
    exit 1
fi
