#!/usr/bin/env fish

function foo
    if test 1 = 2
        echo "not sure how we got here"
        exit 0
    else
        exit 1
    end
end
