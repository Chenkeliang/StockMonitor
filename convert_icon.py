from PIL import Image
import os

def remove_white_background(image_path):
    """移除图片的白色背景"""
    img = Image.open(image_path)
    
    # 确保图片有 alpha 通道
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 获取图片数据
    datas = img.getdata()
    
    # 创建新的图片数据，将接近白色的像素设为透明
    new_data = []
    for item in datas:
        # 检查像素是否接近白色 (RGB 值都很高)
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            # 设置为完全透明
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    
    # 更新图片数据
    img.putdata(new_data)
    return img

def convert_to_icns():
    """将 PNG 转换为 Mac 图标"""
    # 确保 icons 目录存在
    if not os.path.exists('icons'):
        os.makedirs('icons')
    
    # 检查源文件是否存在
    if not os.path.exists('icons/icon.png'):
        print("错误: 请先将生成的图片重命名为 icon.png 并放到 icons 目录下")
        return
    
    # 移除白色背景并保存
    processed_img = remove_white_background('icons/icon.png')
    processed_path = 'icons/icon_processed.png'
    processed_img.save(processed_path)
    
    # 创建 iconset 目录
    os.system('mkdir icons/icon.iconset')
    
    # 生成不同尺寸的图标
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for size in sizes:
        os.system(f'sips -z {size} {size} {processed_path} --out icons/icon.iconset/icon_{size}x{size}.png')
        if size <= 512:
            os.system(f'sips -z {size*2} {size*2} {processed_path} --out icons/icon.iconset/icon_{size}x{size}@2x.png')
    
    # 转换为 icns
    os.system('iconutil -c icns icons/icon.iconset --output icons/icon.icns')
    
    # 清理临时文件
    os.system('rm -rf icons/icon.iconset')
    os.system(f'rm {processed_path}')
    print("转换完成！图标文件已保存为 icons/icon.icns")

if __name__ == '__main__':
    convert_to_icns() 