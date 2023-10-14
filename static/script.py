from PIL import Image

def shrink_image(input_path, output_path, max_size=(95, 95), quality=85):
    try:
        img = Image.open(input_path)
        img.thumbnail(max_size)
        img.save(output_path, optimize=True, quality=quality)
        return True
    except Exception as e:
        return False

if __name__ == "__main__":
    input_path = "accept_icon.jpg"  
    output_path = "accept_icon.jpg"  
    if shrink_image(input_path, output_path):
        print("SUCCESS")
    else:
        print("FAILED")