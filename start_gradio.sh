#!/bin/bash

# Wrapper script to launch Gradio interface
# This script is in the root, actual files are in gradio/ folder

cd "$(dirname "$0")"
./gradio/start_gradio.sh "$@"
