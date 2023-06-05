#! /usr/bin/env bash

alembic upgrade head

python -m fastipam.core.init_db