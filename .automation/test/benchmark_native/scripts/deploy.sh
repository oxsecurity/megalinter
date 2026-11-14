#!/bin/bash
TARGET_DIR=$1
FILES=$(ls $TARGET_DIR)
for file in $FILES; do
  cp $TARGET_DIR/$file /tmp/backup/$file
done
echo Deployed to $TARGET_DIR
