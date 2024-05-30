#!/usr/bin/env bash
toolforge build start https://github.com/gopavasanth/ToolWatch
toolforge webservice restart
toolforge jobs load jobs.yaml
