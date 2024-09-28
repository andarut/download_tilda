#!/bin/bash

if [ ! -d "./.venv" ]; then
	python3.11 -m venv .venv && .venv/bin/python3 -m pip install -r requirements.txt
fi

.venv/bin/python3 download.py
