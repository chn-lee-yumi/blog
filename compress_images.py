import os
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

ZOOM_RATIO = 1  # 缩放比例

def compress_images(input_dir, output_dir):
    # 创建输出目录，如果不存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历输入目录
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            # 检查文件后缀
            if file.lower().endswith((".jpeg", ".jpg", ".heic")):
                input_path = os.path.join(root, file)

                try:
                    # 打开图片
                    with Image.open(input_path) as img:
                        # 获取原始尺寸
                        original_width, original_height = img.size

                        # 尝试读取EXIF信息
                        exif_data = img.info.get("exif")

                        # 缩小长宽为原来的1/4
                        new_width = original_width // ZOOM_RATIO
                        new_height = original_height // ZOOM_RATIO

                        # 调整图片大小
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                        # 保存为WebP并保留EXIF信息 https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#webp-saving
                        output_path = os.path.join(output_dir, os.path.splitext(file)[0] + ".webp")
                        if exif_data:
                            img.save(output_path, format="WEBP", quality=10, method=6, exif=exif_data)
                        else:
                            img.save(output_path, format="WEBP", quality=10, method=6)

                        print(f"Compressed and saved: {output_path}")
                except Exception as e:
                    print(f"Failed to process {input_path}: {e}")

# 输入与输出文件夹
input_folder = "content/post/2025/202412Travel"
# output_folder = input_folder + "_compressed"
output_folder = input_folder

compress_images(input_folder, output_folder)
