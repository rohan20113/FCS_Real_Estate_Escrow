from PIL import Image

def shrink_image(input_path, output_path, max_size=(60, 60), quality=100):
    try:
        img = Image.open(input_path)
        img.thumbnail(max_size)
        img.save(output_path, optimize=True, quality=quality)
        return True
    except Exception as e:
        return False

if __name__ == "__main__":
    input_path = "view_contract.png"  
    output_path = "view_contract.png"  
    if shrink_image(input_path, output_path):
        print("SUCCESS")
    else:
        print("FAILED")