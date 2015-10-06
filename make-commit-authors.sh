DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

git log --format='%ct,%an' \
  | sort -t, -s -k 2 \
  | $DIR/make-author-stats.py \
  | sort -t, -nr > $DIR/author-stats.csv
