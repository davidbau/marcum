#!/bin/sh

git --git-dir linux-history/.git log -p -U0 --date=raw | python collate-author-words.py > author_rank
