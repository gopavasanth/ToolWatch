#!/bin/bash
export TZ=UTC
cd ToolWatch
ENV=production $HOME/pyvenv/bin/python3 ./cron.py