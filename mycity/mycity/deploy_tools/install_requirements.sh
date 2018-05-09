#!/bin/bash

# load packages into a virtualenv from the requirements file

REQUIREMENTS_FILE="./requirements.txt"
REQUIREMENTS_NO_DEPS_FILE="./requirements_no_deps.txt"
TEMP_DIR_PATH="../../temp"

pip install -r $REQUIREMENTS_FILE -t $TEMP_DIR_PATH

pip install --no-deps -r $REQUIREMENTS_NO_DEPS_FILE -t $TEMP_DIR_PATH


