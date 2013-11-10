#!/usr/bin/env python

import pytest


errno = pytest.main("--cov src/DataSounds --cov-report xml --cov-report term-missing --junitxml=tests.xml")
raise SystemExit(errno)
