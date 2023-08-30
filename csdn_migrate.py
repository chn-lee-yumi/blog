"""
本代码大部分由ChatGPT完成 https://chat.openai.com/share/ffc3c3dd-f115-45e0-bbfc-7c1ec9fb2f78
"""
import os
import re

import requests

# 定义正则表达式模式
url_pattern = r'\(https://img-blog\.csdnimg\.cn/.*\.png.*\)'


# 遍历目录下的所有markdown文件
def process_markdown_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                process_single_file(file_path)


# 处理单个markdown文件
def process_single_file(file_path):
    print("Process:", file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    matches = re.findall(url_pattern, content)
    for match in matches:
        download_and_replace(file_path, match)


# 下载图片并替换内容
def download_and_replace(file_path, url):
    print("Download:", file_path, url)
    response = requests.get(url.strip("()").split('?')[0], headers={
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Chromium\";v=\"104\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"104\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    })
    if response.status_code == 200:
        image_filename = url.strip("()").split('?')[0].split('/')[-1]
        image_path = os.path.join(os.path.dirname(file_path), image_filename)

        with open(image_path, 'wb') as f:
            f.write(response.content)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # print(url, "=>", image_filename)
        new_content = content.replace(f'{url}', f'({image_filename})')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        print("下载失败", response.status_code)


# 主函数
if __name__ == '__main__':
    content_directory = 'content'  # 替换为你的目录路径
    process_markdown_files(content_directory)
