#!/usr/bin/env bash
toolforge build start https://github.com/gopavasanth/ToolWatch
toolforge webservice --mount=none buildservice start
toolforge jobs load jobs.yaml
