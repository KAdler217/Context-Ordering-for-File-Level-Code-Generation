from PIL import Image
import os


def process_image(input_path, output_folder):
    # 获取原文件名（不含扩展名）
    filename = os.path.splitext(os.path.basename(input_path))[0]
    # 构建输出路径（保持原名称，使用PNG格式）
    output_path = os.path.join(output_folder, f"{filename}.png")

    try:
        # 读取图片
        with Image.open(input_path) as img:
            # 调整尺寸为32x32像素
            img = img.resize((32, 32))

            # 转换为灰度图（单通道）
            img = img.convert('L')  # 'L'模式表示灰度

            # 保存为PNG格式
            img.save(output_path, 'PNG')
            print(f"处理完成: {input_path} -> {output_path}")

    except Exception as e:
        print(f"处理失败 {input_path}: {str(e)}")


# 批量处理文件夹中的所有图片
input_folder = "input_images/"  # 输入图片所在文件夹
output_folder = "processed_images/"  # 处理后图片保存文件夹

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 支持的图片格式
supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')

# 遍历输入文件夹中的所有文件
for filename in os.listdir(input_folder):
    # 检查文件是否为图片
    if filename.lower().endswith(supported_formats):
        input_path = os.path.join(input_folder, filename)
        process_image(input_path, output_folder)
    else:
        print(f"跳过非图片文件: {filename}")
