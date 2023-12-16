#!/bin/bash
export TZ=UTC
cd ToolWatch
$HOME/pyvenv/bin/python3 ./cron.py
cp tools.db ../www/python/src