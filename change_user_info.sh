#!/bin/sh
# https://segmentfault.com/q/1010000006999861
git filter-branch --env-filter '
an="$GIT_AUTHOR_NAME"
am="$GIT_AUTHOR_EMAIL"
cn="$GIT_COMMITTER_NAME"
cm="$GIT_COMMITTER_EMAIL"
if [ "$GIT_COMMITTER_EMAIL" = "imsantu.ma@gmail.com" ]
then
    cn="imoyao"
    cm="immoyao@gmail.com"
fi
if [ "$GIT_AUTHOR_EMAIL" = "imsantu.ma@gmail.com" ]
then
    an="imoyao"
    am="immoyao@gmail.com"
fi
    export GIT_AUTHOR_NAME="$an"
    export GIT_AUTHOR_EMAIL="$am"
    export GIT_COMMITTER_NAME="$cn"
    export GIT_COMMITTER_EMAIL="$cm" '
