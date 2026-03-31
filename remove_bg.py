import sys
from PIL import Image, ImageOps

def remove_black_background(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    
    # Convert image to grayscale for the mask
    gray = img.convert("L")
    
    # We want black to become transparent (alpha 0) and non-black to be opaque.
    # So the mask should be the gray image itself (black=0, white=255)
    # This works perfectly if it's a white/light logo on a black background.
    
    # Let's apply the mask
    img.putalpha(gray)
    
    img.save(output_path, "PNG")

if __name__ == "__main__":
    remove_black_background(sys.argv[1], sys.argv[2])
