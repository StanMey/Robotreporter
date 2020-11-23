import cv2
import numpy as np


def resize_image(img, width):
    """Gets an image and the new width and resizes the height appropriately.

    Args:
        img (numpy.ndarray): A numpy array with the to be resized image
        width (int): The new size of the width

    Returns:
        numpy.ndarray: A new resized array containing the image
    """
    # get the ratio of the change and apply it to the height
    height = int((width / img.shape[1]) * img.shape[0])
    # resize the image
    img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
    return img


def overlay_transparent(background, overlay, x, y):
    """Takes two coordinates (x, y) and sets the overlay image upon the background image.
    https://stackoverflow.com/questions/40895785/using-opencv-to-overlay-transparent-image-onto-another-image

    Args:
        background (numpy.ndarray): A numpy array of the background image
        overlay (numpy.ndarray): A numpy array of the to be overlayed image
        x (int): The x-coordinate for the placement of the overlay image
        y (int): The y-coordinate for the placement of the overlay image

    Returns:
        numpy.ndarray: A numpy array with the newly created image
    """

    background_width = background.shape[1]
    background_height = background.shape[0]

    if x >= background_width or y >= background_height:
        return background

    h, w = overlay.shape[0], overlay.shape[1]

    if x + w > background_width:
        w = background_width - x
        overlay = overlay[:, :w]

    if y + h > background_height:
        h = background_height - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        overlay = np.concatenate(
            [
                overlay,
                np.ones((overlay.shape[0], overlay.shape[1], 1), dtype=overlay.dtype) * 255
            ],
            axis=2,
        )

    overlay_image = overlay[..., :3]
    mask = overlay[..., 3:] / 255.0

    background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image

    return background
