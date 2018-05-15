import cv2 as cv
from mscoco_label_map import category_map
from PIL import ImageColor

TEXT_COLOR = (0, 0, 0)

STANDARD_COLORS = [
    'AliceBlue', 'Chartreuse', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque',
    'BlanchedAlmond', 'BlueViolet', 'BurlyWood', 'CadetBlue', 'AntiqueWhite',
    'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan',
    'DarkCyan', 'DarkGoldenRod', 'DarkGrey', 'DarkKhaki', 'DarkOrange',
    'DarkOrchid', 'DarkSalmon', 'DarkSeaGreen', 'DarkTurquoise', 'DarkViolet',
    'DeepPink', 'DeepSkyBlue', 'DodgerBlue', 'FireBrick', 'FloralWhite',
    'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod',
    'Salmon', 'Tan', 'HoneyDew', 'HotPink', 'IndianRed', 'Ivory', 'Khaki',
    'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue',
    'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGray', 'LightGrey',
    'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue',
    'LightSlateGray', 'LightSlateGrey', 'LightSteelBlue', 'LightYellow', 'Lime',
    'LimeGreen', 'Linen', 'Magenta', 'MediumAquaMarine', 'MediumOrchid',
    'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen',
    'MediumTurquoise', 'MediumVioletRed', 'MintCream', 'MistyRose', 'Moccasin',
    'NavajoWhite', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed',
    'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed',
    'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple',
    'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Green', 'SandyBrown',
    'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue',
    'SlateGray', 'SlateGrey', 'Snow', 'SpringGreen', 'SteelBlue', 'GreenYellow',
    'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'Wheat', 'White',
    'WhiteSmoke', 'Yellow', 'YellowGreen'
]


def put_text_and_background(image, text, org, fontFace, fontScale, text_color, box_color, thickness):
    text_size = cv.getTextSize(text, fontFace, fontScale, thickness)

    org = (org[0] - 1, org[1])

    org_end = (org[0] + text_size[0][0] + 1, org[1] - text_size[0][1] - 2)  # +1, -2 for padding

    cv.rectangle(image, org, org_end, box_color, cv.FILLED)

    cv.putText(
        image,
        text,
        org,
        fontFace,
        fontScale,
        text_color,
        thickness
    )


def draw_bbox(image, boxes, scores, classes, num):
    rows = image.shape[0]
    cols = image.shape[1]

    # Draw the bounding boxes with information about the predictions
    num = int(num[0])

    for i in range(num):
        bbox = boxes[0][i]
        score = scores[0][i]
        class_id = int(classes[0][i])

        # Select a background color color
        box_color = STANDARD_COLORS[class_id % len(STANDARD_COLORS)]

        # Convert color into bgr, because friggin OpenCV
        color_rgb = ImageColor.getrgb(box_color)
        color_bgr = (color_rgb[2], color_rgb[1], color_rgb[0])

        if score > 0.3:
            class_name = category_map[class_id]  # Integer --> String name
            x = int(bbox[1] * cols)
            y = int(bbox[0] * rows)
            right = int(bbox[3] * cols)
            bottom = int(bbox[2] * rows)

            # Bounding box
            cv.rectangle(image,
                         (x, y),
                         (right, bottom),
                         color_bgr,
                         thickness=2)

            put_text_and_background(
                image,
                f"{class_name}: {int(100*score)}%",
                org=(x, y),
                fontFace=1,
                fontScale=1,
                text_color=TEXT_COLOR,
                box_color=color_bgr,
                thickness=1
            )
