#!/usr/bin/env bash
toolforge build start https://github.com/gopavasanth/ToolWatch
toolforge webservice python3.11 restart
toolforge jobs load jobs.yaml
