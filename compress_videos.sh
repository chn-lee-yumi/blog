#!/usr/bin/env bash
# 下面是示例，注意帧率要先用ffprobe看看原视频，然后再设置
input_file="content/post/2025/202412Travel/IMG_6334.MOV"
output_file="content/post/2025/202412Travel/IMG_6334.webm"
ffmpeg -i "$input_file" -c:v libvpx-vp9 -b:v 2M -r 29.58 -c:a libopus "$output_file"
