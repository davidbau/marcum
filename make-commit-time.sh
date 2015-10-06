DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

git log --format="%ct" > $DIR/commit-time.csv
