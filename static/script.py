from PIL import Image

def shrink_image(input_path, output_path, max_size=(40, 40), quality=85):
    try:
        # Open the image
        img = Image.open(input_path)
        # print(img.size)
        # Resize the image while maintaining its aspect ratio
        img.thumbnail(max_size)
        
        # Save the resized image with the specified quality
        img.save(output_path, optimize=True, quality=quality)
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    input_path = "delete_icon2.png"  # Replace with the path to your uploaded image
    output_path = "delete_icon2.png"  # Replace with the desired output path
    
    if shrink_image(input_path, output_path):
        print("Image successfully resized and compressed.")
    else:
        print("Failed to resize and compress the image.")
