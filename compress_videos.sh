#!/usr/bin/env bash

target_dir="content/post/2026/202601Travel"

for input_file in "$target_dir"/*.mov; do
    output_file="${input_file%.mov}.webm"

    ffmpeg -y -i "$input_file" \
        -c:v libvpx-vp9 -b:v 1M \
        -c:a libopus \
        "$output_file"
done