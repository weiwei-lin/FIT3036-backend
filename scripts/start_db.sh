#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DB_DIR="$(dirname $SCRIPT_DIR)/data"
mkdir -p $DB_DIR
mongod --dbpath $DB_DIR
