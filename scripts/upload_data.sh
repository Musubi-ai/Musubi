#!/bin/bash

cd data
huggingface-cli upload $1 . . --repo-type dataset

echo "==================================================="
echo "Finished uploading data to $1!"
echo "==================================================="