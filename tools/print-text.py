#! /usr/bin/python3
# sudo rfcomm connect 0 F4:D7:32:46:5D:2C
import sys, os

from PIL import Image, ImageFont, ImageDraw

def print_header():
    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        stdout.write(b'\x1b\x40\x1b\x61\x01\x1f\x11\x02\x04')
    return

def print_marker(lines=0x100):
    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        stdout.write(0x761d.to_bytes(2, 'little'))
        stdout.write(0x0030.to_bytes(2, 'little'))
        stdout.write(0x0030.to_bytes(2, 'little'))
        stdout.write((lines - 1).to_bytes(2, 'little'))
    return

def print_footer():
    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        stdout.write(b'\x1b\x64\x02')
        stdout.write(b'\x1b\x64\x02')
        stdout.write(b'\x1f\x11\x08')
        stdout.write(b'\x1f\x11\x0e')
        stdout.write(b'\x1f\x11\x07')
        stdout.write(b'\x1f\x11\x09')
    return

def print_line(image, line):
    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        for x in range(int(image.width / 8)):
            byte = 0
            for bit in range(8):
                if image.getpixel((x * 8 + bit, line)) == 0:
                    byte |= 1 << (7 - bit)
            # 0x0a breaks the rendering
            # 0x0a alone is processed like LineFeed by the printe
            if byte == 0x0a:
                byte = 0x14
            stdout.write(byte.to_bytes(1, 'little'))
    return

if __name__ == '__main__':
    text = ' '.join(sys.argv[1:]).replace('\\n', '\n')
    print('Printing:\n', text, file=sys.stderr)
    lines = text.split('\n')
    for line in lines:
        if len(line) > 12:
            sys.exit('Please pass a maximum of 12 chars per line')
    image = Image.new("RGB", (384, 50 * len(lines)), (255, 255, 255))

    # Draw text
    draw = ImageDraw.Draw(image) 
        
    # drawing text size
    myFont = ImageFont.truetype('DejaVuSans.ttf', 50)
    for i, line in enumerate(lines):
        draw.text((0, i * 50), line, font=myFont, fill=(0, 0, 0))
    
    # black&white printer: dithering
    image = image.convert(mode='1')
    # image.save("to_print.png", "PNG")

    if image.height > 256:
        sys.exit('Please keep text small')

    print_header()
    print_marker(image.height)
    for y_i in range(image.height):
        print_line(image, y_i)
    print_footer()
