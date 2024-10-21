set -e

rm -f test.out

run() {
    echo "$@"
    echo "------------------- $@ ----------------------" >> test.out
    "$@" >testcase.out 2>&1 || { echo "ERROR: nonzero exit code $? -- check testcase.out"; exit 1; }
    cat testcase.out >> test.out
}

run_expect_error() {
    echo "$@"
    echo "------------------- $@ ----------------------" >> test.out
    "$@" >testcase.out 2>&1 && { echo "ERROR: unexpected zero exit code (unreported error) -- check testcase.out"; exit 1; }
    cat testcase.out >> test.out
}

assert_contains() {
    grep -q "$*" testcase.out || { echo "ERROR: missing: \"$*\" -- check testcase.out"; exit 1; }
}

assert_contains_line() {
    grep -q "^$*$" testcase.out || { echo "ERROR: missing line: \"$*\" -- check testcase.out"; exit 1; }
}

assert_not_contains() {
    grep -q "$*" testcase.out && { echo "ERROR: unexpected: \"$*\" -- check testcase.out"; exit 1; } || :
}

assert_num_lines() {
    min="$1"
    max="${2:-$min}"
    count=$(wc -l testcase.out | awk '{print $1}')
    if [ "$count" -lt "$min" ] || [ "$count" -gt "$max" ]; then
        echo "ERROR: wrong number of lines: $* (got $count, expected $min-$max) -- check testcase.out"
        exit 1
    fi
}
