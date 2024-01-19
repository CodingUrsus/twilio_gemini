from PIL import Image
import os

# Specify the path to the images directory
image_dir = "/home/hammera/python_projects/twilio_gemini/images"

# Iterate through all images in the directory
for filename in os.listdir(image_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):  # Check for supported image formats
        filepath = os.path.join(image_dir, filename)

        # Open the image using Pillow
        with Image.open(filepath) as image:

            # Get the original image size
            width, height = image.size

            # Calculate a resizing factor to achieve a file size less than 3.5MB
            factor = 0.9  # Start with a conservative factor
            while True:
                image.thumbnail((int(width * factor), int(height * factor)))
                try:
                    with open("temp.jpg", "wb") as f:  # Temporary file to check size
                        image.save(f, "JPEG", quality=85)  # Adjust quality if needed
                    if os.path.getsize("temp.jpg") < 3.5 * 1024 * 1024:  # Check if under 3.5MB
                        break
                except OSError:  # Handle potential errors during saving
                    print(f"Error saving image {filename}. Skipping.")
                    continue
                factor -= 0.1  # Reduce factor for further resizing

            # Save the resized image to the same filename
            image.save(filepath)

# Remove the temporary file
os.remove("temp.jpg")
