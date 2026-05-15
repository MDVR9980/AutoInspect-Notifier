from PIL import Image

def png_to_ico(png_path, ico_path):
    img = Image.open(png_path)

    # سایزهای استاندارد آیکون ویندوز
    sizes = [(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)]

    img.save(ico_path, sizes=sizes)

    print(f"Icon saved as {ico_path}")

# مثال استفاده
png_to_ico("AppIconVersion.png", "app_icon.ico")
