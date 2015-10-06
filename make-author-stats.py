#!/usr/bin/env python

import csv, sys

reader = len(sys.argv) >= 2 and open(sys.argv[1]) or sys.stdin

current_person = None
current_latest_commit = 0
current_commit_count = 0
for line in reader:
  [time, person] = line.strip().split(',', 1)
  if current_person != person:
    if current_person is not None:
      print "%d,%d,%s" % (
        current_commit_count,
        current_latest_commit - current_earliest_commit,
        current_person)
    current_person = person
    current_latest_commit = int(time)
    current_commit_count = 0
  current_commit_count += 1
  current_earliest_commit = int(time)

print "%d,%d,%s" % (
  current_commit_count,
  current_latest_commit - current_earliest_commit,
  current_person)
