from PIL import Image
from rembg import remove
import io

def remove_background_core(image_bytes: bytes) -> bytes:
    """
    Removes the background from an image using rembg.
    Args:
        image_bytes: The input image as bytes.
    Returns:
        Image bytes with background removed (PNG format).
    """
    try:
        input_image = Image.open(io.BytesIO(image_bytes))
        # rembg returns a PIL Image object, usually in RGBA format
        output_image = remove(input_image)

        # Save the output image to bytes in PNG format (to preserve transparency)
        byte_arr = io.BytesIO()
        output_image.save(byte_arr, format='PNG')
        return byte_arr.getvalue()
    except Exception as e:
        print(f"Error in remove_background_core: {e}")
        # Consider raising a custom exception or returning None/error indicator
        raise # Re-raise for Celery to mark task as failed

def resize_image_core(image_bytes: bytes, width: int = None, height: int = None, keep_aspect_ratio: bool = True) -> bytes:
    """
    Resizes an image.
    Args:
        image_bytes: The input image as bytes.
        width: Target width.
        height: Target height.
        keep_aspect_ratio: If true, maintains aspect ratio.
                           If both width and height are provided, it will try to fit within those dimensions.
    Returns:
        Resized image bytes (original format preserved unless specified otherwise later).
    """
    img = Image.open(io.BytesIO(image_bytes))
    original_format = img.format # Store original format

    if not width and not height:
        return image_bytes # No resize needed

    orig_width, orig_height = img.size

    if keep_aspect_ratio:
        if width and height:
            # Fit within bounding box while maintaining aspect ratio
            ratio = min(width / orig_width, height / orig_height)
            new_width = int(orig_width * ratio)
            new_height = int(orig_height * ratio)
        elif width:
            ratio = width / orig_width
            new_height = int(orig_height * ratio)
            new_width = width
        elif height:
            ratio = height / orig_height
            new_width = int(orig_width * ratio)
            new_height = height
        else: # Should not happen if width or height is provided
            return image_bytes
    else: # Not keeping aspect ratio (stretch/squash)
        new_width = width if width else orig_width
        new_height = height if height else orig_height

    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS) # Use LANCZOS for quality

    byte_arr = io.BytesIO()
    # Save in the original format if possible, default to PNG if format is unknown
    save_format = original_format if original_format else 'PNG'
    resized_img.save(byte_arr, format=save_format)
    return byte_arr.getvalue()

# Add more operations (convert_format, change_background_color) here later for MVP+