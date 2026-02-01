#!/usr/bin/env bash
# 下面是示例，注意帧率要先用ffprobe看看原视频，然后再设置
input_file="content/post/2026/ANU-Quantum-Science-Open-Day/IMG_1534.MOV"
output_file="content/post/2026/ANU-Quantum-Science-Open-Day/IMG_1534_2.webm"
ffmpeg -i "$input_file" -c:v libvpx-vp9 -b:v 1M -r 29.57 -c:a libopus "$output_file"
