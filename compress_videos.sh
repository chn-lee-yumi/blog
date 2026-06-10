#!/usr/bin/env bash
# 下面是示例，注意帧率要先用ffprobe看看原视频，然后再设置
input_file="content/post/2026/202601Travel/IMG_2156.mov"
output_file="content/post/2026/202601Travel/IMG_2156.webm"
ffmpeg -y -i "$input_file" -c:v libvpx-vp9 -b:v 1M -r 29.67 -c:a libopus "$output_file"
