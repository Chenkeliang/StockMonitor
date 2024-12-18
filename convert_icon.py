import os


def convert_icon():
    # 确保 icons 目录存在
    if not os.path.exists("icons"):
        os.makedirs("icons")

    # 创建临时 iconset 目录
    os.system("mkdir -p icons/icon.iconset")

    # 定义需要的尺寸
    sizes = [16, 32, 64, 128, 256, 512]

    # 生成不同尺寸的图标
    for size in sizes:
        os.system(
            f"sips -z {size} {size} icons/icon.png --out icons/icon.iconset/icon_{size}x{size}.png"
        )
        if size <= 512:
            os.system(
                f"sips -z {size*2} {size*2} icons/icon.png --out icons/icon.iconset/icon_{size}x{size}@2x.png"
            )

    # 转换为 icns 文件
    os.system("iconutil -c icns icons/icon.iconset --output icons/icon.icns")

    # 清理临时文件
    os.system("rm -rf icons/icon.iconset")


if __name__ == "__main__":
    convert_icon()
