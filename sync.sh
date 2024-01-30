#!/bin/bash
export TZ=UTC
cd ToolWatch
MODE=production $HOME/pyvenv/bin/python3 ./cron.py