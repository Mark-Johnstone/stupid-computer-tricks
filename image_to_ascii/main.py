from PIL import Image
from rembg import remove
from pathlib import Path
from pygments.formatters import ImageFormatter
import pygments.lexers

ascii_sample_file = 'ascii_sample.txt' # Path of a sample ascii text file to get character set from
char_set = ' .:-=+*#%&@' # Character set to use, ordered from light to dark representations
input_path = 'input_image.jpg'  # Path to your JPG photo input
no_bg_path = 'output_no_background.png' # Path for the image output after background is removed
png_path = 'output_png.png' # Path for the PNG output
ascii_path = 'output_ascii.txt' # Path for the ASCII output

def read_file_to_char_set(ascii_sample):
    non_blank_chars = []
    try:
        with open(ascii_sample, 'r') as file:
            for line in file:
                for char in line:
                    if char not in non_blank_chars and not char.isspace():
                        non_blank_chars.append(char)
    except FileNotFoundError:
        print(f"The file {ascii_sample} was not found.")
    except Exception as error:
        print(f"An error occurred: {error}")
    return non_blank_chars

def replace_image_background (input_file):
    """Replaces the background in an image with a white background"""
    try:
        input_image = Image.open(input_file)
        # Remove background and change to RGBA to handle transparency layer
        img_no_bg = remove(input_image).convert("RGBA")
        # Create a new white background image
        width, height = img_no_bg.size
        white_bg = Image.new("RGB", (width, height), "white")
        # Paste the foreground onto the white background
        white_bg.paste(img_no_bg, (0, 0), img_no_bg)
        # Save the final image with the white background
        white_bg.save(no_bg_path)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
    except Exception as error:
        print(f"An error occurred: {error}")

def image_to_ascii(image_path, output_width, chars):
    """Converts an image to ASCII art."""
    try:
        # Open image and convert to grayscale
        image = Image.open(image_path).convert('L')
        # Adjust for character aspect ratio
        width, height = image.size
        aspect_ratio = height / width
        new_height = int(output_width * aspect_ratio * 0.55)
        image = image.resize((output_width, new_height))
        # Get list of pixel values from image
        pixels = image.getdata()
        n_pixels = len(pixels)
        # Map pixel brightnesses to the index of the character we will use to represent them
        ascii_image = [chars[(255 - pixel) * len(chars) // 256] for pixel in pixels]
        ascii_image = ''.join(ascii_image)
        # Stitch each line back together
        lines = [ascii_image[i:i + output_width] for i in range(0, len(ascii_image), output_width)]
        return '\n'.join(lines)
    except FileNotFoundError:
        print(f"Error: Input file not found at {image_path}")
        return None
    except Exception as error:
        print(f"An error occurred: {error}")
        return None

def ascii_to_png(ascii_image):
    """Converts an ascii text image to PNG image."""
    try:
        lexer = pygments.lexers.TextLexer()
        # Read in the text from the ascii file
        png = pygments.highlight(Path(ascii_image).read_text(), lexer, ImageFormatter(line_numbers=False))
        # Write out the text as an image. We didn't do any text manipulation,
        # this is just a means to convert to PNG
        Path(png_path).write_bytes(png)
        return None
    except Exception as error:
        print(f"An error occurred: {error}")
        return None


if __name__ == "__main__":
    # The line below was used once to capture an initial list of the
    # unique characters in a sample ascii text image:
    # print(read_file_to_char_set(ascii_sample_file))

    # Replace the input image background with a white background:
    replace_image_background(input_path)

    # Take the image with a white background, and convert it to an ascii image:
    ascii_portrait = image_to_ascii(image_path=no_bg_path, output_width=100, chars=char_set)

    # Save ascii image to a text file:
    with open(ascii_path, 'w') as file:
        file.write(ascii_portrait)

    # Also save the ascii text file output to a png file,
    # because some use cases only allow png or jpg file types.
    # Chose the pygments library here, it seemed the most concise.
    ascii_to_png(ascii_path)