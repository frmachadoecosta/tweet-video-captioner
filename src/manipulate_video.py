from PIL import Image, ImageDraw, ImageFont


def create_header(text, video_width, font_path, max_font_size=100):
    """
    Creates a white header image with automatically sized text.

    Short text:
        large font, one line

    Long text:
        smaller font, one line if possible

    Very long text:
        wraps to two lines

    Returns:
        header_image, header_height
    """

    horizontal_padding = 50
    vertical_padding = 20

    max_width = video_width - horizontal_padding * 2

    # ---------------------------------------------------------
    # Load font and find a size that fits
    # ---------------------------------------------------------

    selected_size = None
    selected_lines = None

    words = text.split()

    for font_size in range(max_font_size, 20, -2):

        font = (
            ImageFont.truetype(font_path, font_size)
            if font_path
            else ImageFont.load_default(size=font_size)
        )

        # First try one line
        bbox = font.getbbox(text)

        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        if text_width <= max_width:
            selected_size = font_size
            selected_lines = [text]
            break

        # -----------------------------------------------------
        # Try two lines
        # -----------------------------------------------------

        best_lines = None
        best_width = float("inf")

        for i in range(1, len(words)):

            line1 = " ".join(words[:i])
            line2 = " ".join(words[i:])

            bbox1 = font.getbbox(line1)
            bbox2 = font.getbbox(line2)

            width1 = bbox1[2] - bbox1[0]
            width2 = bbox2[2] - bbox2[0]

            width = max(width1, width2)

            if width <= max_width and width < best_width:
                best_width = width
                best_lines = [line1, line2]

        if best_lines:
            selected_size = font_size
            selected_lines = best_lines
            break

    # Fallback
    if selected_size is None:
        selected_size = 20
        selected_lines = [text]

    font = (
        ImageFont.truetype(font_path, selected_size)
        if font_path
        else ImageFont.load_default(size=selected_size)
    )

    # ---------------------------------------------------------
    # Calculate EXACT dimensions using Pillow
    # ---------------------------------------------------------

    spacing = 5

    bboxes = [
        font.getbbox(line)
        for line in selected_lines
    ]

    widths = [
        bbox[2] - bbox[0]
        for bbox in bboxes
    ]

    heights = [
        bbox[3] - bbox[1]
        for bbox in bboxes
    ]

    text_width = max(widths)
    text_height = sum(heights) + spacing * (len(selected_lines) - 1)

    header_height = text_height + vertical_padding * 2
    # H.264 requires even dimensions
    header_height += header_height % 2

    # ---------------------------------------------------------
    # Create header
    # ---------------------------------------------------------

    image = Image.new(
        "RGB",
        (video_width, header_height),
        "black"
    )

    draw = ImageDraw.Draw(image)

    # ---------------------------------------------------------
    # Draw text
    # ---------------------------------------------------------

    y = vertical_padding

    for line, bbox, height, width in zip(
        selected_lines,
        bboxes,
        heights,
        widths
    ):

        x = (video_width - width) // 2

        # Account for font's internal bounding-box offset
        draw.text(
            (
                x - bbox[0],
                y - bbox[1]
            ),
            line,
            font=font,
            fill="white"
        )

        y += height + spacing

    return image, header_height
