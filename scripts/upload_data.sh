#!/bin/bash

cd data
huggingface-cli upload $1 . . --repo-type dataset
echo "Finished uploading data to dataset!"