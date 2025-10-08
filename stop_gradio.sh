#!/bin/bash

# Wrapper script to stop Gradio interface
# This script is in the root, actual files are in gradio/ folder

cd "$(dirname "$0")"
./gradio/stop_gradio.sh "$@"
