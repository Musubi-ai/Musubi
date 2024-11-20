#!/bin/bash

cd crawler
huggingface-cli upload $1 . . --repo-type dataset
echo "Finished uploading links to dataset!"