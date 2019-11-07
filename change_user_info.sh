#!/bin/sh
# https://segmentfault.com/q/1010000006999861
# https://stackoverflow.com/questions/750172/how-to-change-the-author-and-committer-name-and-e-mail-of-multiple-commits-in-gi

git filter-branch --force --env-filter '
    if [ "$GIT_COMMITTER_NAME" = "masantu" ];
    then
        GIT_COMMITTER_NAME="imoyao";
        GIT_COMMITTER_EMAIL="immoyao@gmail.com";
        GIT_AUTHOR_NAME="imoyao";
        GIT_AUTHOR_EMAIL="immoyao@gmail.com";
    fi' -- --all