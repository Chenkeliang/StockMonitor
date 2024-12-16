from PIL import Image, ImageDraw
import os

def create_icon():
    # 创建基础图像
    size = 1024
    image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # 定义颜色
    black = (40, 40, 40)
    white = (255, 255, 255)
    pink = (255, 182, 193)
    light_pink = (255, 218, 224)
    grey = (150, 150, 150)
    
    # 画熊猫头部（白色圆形，稍微偏上）
    center = size // 2
    radius = size // 2.2
    draw.ellipse([
        center - radius,
        center - radius - size//10,  # 向上偏移
        center + radius,
        center + radius - size//10
    ], fill=white)
    
    # 画大圆耳朵底色（灰色）
    ear_radius = radius // 2
    # 左耳
    draw.ellipse([
        center - radius - ear_radius//2,
        center - radius - size//8,
        center - radius//1.5,
        center - radius//1.5 - size//8
    ], fill=grey)
    # 右耳
    draw.ellipse([
        center + radius//1.5,
        center - radius - size//8,
        center + radius + ear_radius//2,
        center - radius//1.5 - size//8
    ], fill=grey)
    
    # 画内耳（黑色，稍小）
    inner_ear_radius = ear_radius // 1.3
    # 左耳
    draw.ellipse([
        center - radius - ear_radius//2 + 20,
        center - radius - size//8 + 20,
        center - radius//1.5 - 20,
        center - radius//1.5 - size//8 - 20
    ], fill=black)
    # 右耳
    draw.ellipse([
        center + radius//1.5 + 20,
        center - radius - size//8 + 20,
        center + radius + ear_radius//2 - 20,
        center - radius//1.5 - size//8 - 20
    ], fill=black)
    
    # 画眼睛周围的黑圈
    eye_patch_width = radius // 1.8
    eye_patch_height = radius // 1.5
    # 左眼圈
    draw.ellipse([
        center - radius//1.2,
        center - radius//4,
        center - radius//1.2 + eye_patch_width,
        center - radius//4 + eye_patch_height
    ], fill=black)
    # 右眼圈
    draw.ellipse([
        center + radius//1.2 - eye_patch_width,
        center - radius//4,
        center + radius//1.2,
        center - radius//4 + eye_patch_height
    ], fill=black)
    
    # 画眼睛（白色大眼睛）
    eye_width = radius // 2.5
    eye_height = radius // 2
    # 左眼
    draw.ellipse([
        center - radius//1.2 + 30,
        center - radius//4 + 30,
        center - radius//1.2 + eye_patch_width - 30,
        center - radius//4 + eye_patch_height - 30
    ], fill=white)
    # 右眼
    draw.ellipse([
        center + radius//1.2 - eye_patch_width + 30,
        center - radius//4 + 30,
        center + radius//1.2 - 30,
        center - radius//4 + eye_patch_height - 30
    ], fill=white)
    
    # 画眼珠（黑色，偏上）
    pupil_size = eye_width // 2
    # 左眼珠
    draw.ellipse([
        center - radius//1.2 + eye_patch_width//2 - pupil_size//2,
        center - radius//4 + eye_patch_height//3,
        center - radius//1.2 + eye_patch_width//2 + pupil_size//2,
        center - radius//4 + eye_patch_height//3 + pupil_size
    ], fill=black)
    # 右眼珠
    draw.ellipse([
        center + radius//1.2 - eye_patch_width//2 - pupil_size//2,
        center - radius//4 + eye_patch_height//3,
        center + radius//1.2 - eye_patch_width//2 + pupil_size//2,
        center - radius//4 + eye_patch_height//3 + pupil_size
    ], fill=black)
    
    # 画眼睛高光（白色小圆点）
    highlight_size = pupil_size // 2
    # 左眼高光
    draw.ellipse([
        center - radius//1.2 + eye_patch_width//2 - highlight_size//2,
        center - radius//4 + eye_patch_height//3 + highlight_size//2,
        center - radius//1.2 + eye_patch_width//2 + highlight_size//2,
        center - radius//4 + eye_patch_height//3 + highlight_size//2 + highlight_size
    ], fill=white)
    # 右眼高光
    draw.ellipse([
        center + radius//1.2 - eye_patch_width//2 - highlight_size//2,
        center - radius//4 + eye_patch_height//3 + highlight_size//2,
        center + radius//1.2 - eye_patch_width//2 + highlight_size//2,
        center - radius//4 + eye_patch_height//3 + highlight_size//2 + highlight_size
    ], fill=white)
    
    # 画鼻子（粉色爱心形状）
    nose_size = radius // 5
    nose_center_y = center + radius//6
    # 左半边心形
    draw.ellipse([
        center - nose_size,
        nose_center_y - nose_size,
        center,
        nose_center_y + nose_size
    ], fill=pink)
    # 右半边心形
    draw.ellipse([
        center,
        nose_center_y - nose_size,
        center + nose_size,
        nose_center_y + nose_size
    ], fill=pink)
    
    # 画嘴（简单的弧线）
    mouth_start = center - nose_size//1.5
    mouth_end = center + nose_size//1.5
    mouth_y = nose_center_y + nose_size + 20
    draw.arc([mouth_start, mouth_y, mouth_end, mouth_y + 40], 0, 180, fill=black, width=5)
    
    # 画腮红（浅粉色圆形）
    blush_radius = radius // 5
    # 左腮红
    draw.ellipse([
        center - radius//1.1,
        center + radius//8,
        center - radius//1.1 + blush_radius,
        center + radius//8 + blush_radius
    ], fill=light_pink)
    # 右腮红
    draw.ellipse([
        center + radius//1.1 - blush_radius,
        center + radius//8,
        center + radius//1.1,
        center + radius//8 + blush_radius
    ], fill=light_pink)
    
    # 创建icons目录
    if not os.path.exists('icons'):
        os.makedirs('icons')
    
    # 保存为PNG
    image.save('icons/icon.png')
    
    # 创建icns文件
    os.system('mkdir icons/icon.iconset')
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for size in sizes:
        os.system(f'sips -z {size} {size} icons/icon.png --out icons/icon.iconset/icon_{size}x{size}.png')
        if size <= 512:
            os.system(f'sips -z {size*2} {size*2} icons/icon.png --out icons/icon.iconset/icon_{size}x{size}@2x.png')
    
    os.system('iconutil -c icns icons/icon.iconset --output icons/icon.icns')
    os.system('rm -rf icons/icon.iconset')

if __name__ == '__main__':
    create_icon() 