#!/bin/bash

TABLE=$1
TS_COLUMN=$2
BATCH=$3

if [ -z "$TABLE" ] || [ -z "$TS_COLUMN" ] || [ -z "$BATCH" ]; then
  echo "Usage: $0 <table> <ts_column> <batch_size>"
  exit 1
fi

JOB_START=$(date +%s)
MOVED=1
MOVED_TOTAL=0

echo "$(date) -> Starting job for table '$TABLE', column '$TS_COLUMN', batch size $BATCH..." >> sql/casino_partitioning/$TABLE/$TABLE.log

while [ "$MOVED" -ne 0 ]; do
  BATCH_START=$(date +%s)
  MOVED=$(psql -Atq -d bet_fanatics -c "SELECT move_batch('$TABLE', '$TS_COLUMN', $BATCH);")
  END=$(date +%s)
  BATCH_ELAPSED=$((END-BATCH_START))
  JOB_ELAPSED=$((END-JOB_START))
  MOVED_TOTAL=$((MOVED_TOTAL+MOVED))
  echo "$(date) -> Batch moved $MOVED rows in ${BATCH_ELAPSED}s | Total moved: $MOVED_TOTAL rows | Job elapsed: ${JOB_ELAPSED}s" >> sql/casino_partitioning/$TABLE/$TABLE.log
  sleep 0.5
done

echo "$(date) -> Done!" >> sql/casino_partitioning/$TABLE/$TABLE.log