#!/bin/sh
BASE_DIR=`dirname $0`
cd $BASE_DIR

set -e  # failed commands will trigger exit w/ same status
set -x
FUNKLOAD_OPENERP_DB=$2
export FUNKLOAD_OPENERP_DB

../bin/fl-run-test --url=http://localhost:$1 cron.py CronWorkerTestCase
