import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import tempfile

# Add title and description
st.title("🎁 A Special Gift for You!")
st.markdown("### Hey Murshitha Fathima 👋\nI made this for you — a personalized typographic art generator! Upload a photo and see your name come to life in art.")

# Add file uploader for image input
uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

# Add custom text input box
text = st.text_input("Enter your name or custom text ✨", value="Pathu")
st.markdown("🌈 Upload a photo below and watch the magic happen! 🖼️💫")
if uploaded_file:
    image = Image.open(uploaded_file).convert("L")
    img_gray = np.array(image)

    scale = 3
    new_w = int(img_gray.shape[1] * scale)
    new_h = int(img_gray.shape[0] * scale)
    img_gray = cv2.resize(img_gray, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Create a gradient background
    gradient_bg = np.tile(np.linspace(255, 100, new_h).astype(np.uint8), (new_w, 1)).T
    bg_img = Image.fromarray(gradient_bg).convert("RGB")
    draw = ImageDraw.Draw(bg_img)

    # Use a default font path (or upload your custom font in Colab)
    font_path = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"  # Use built-in font for Colab
    base_font_size = 7
    font_levels = [
        {"scale": 3, "threshold": 0.55},
        {"scale": 2, "threshold": 0.35},
        {"scale": 1, "threshold": 0.15}
    ]

    fonts = {}
    font_dims = {}
    for level in font_levels:
        size = int(base_font_size * level["scale"])
        font = ImageFont.truetype(font_path, size)
        fonts[size] = font
        bbox = font.getbbox("A")
        font_dims[size] = (bbox[2] - bbox[0], bbox[3] - bbox[1])

    _, binary = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY_INV)

    # Typographic rendering logic
    text_idx = 0
    text_len = len(text)

    y = 0
    while y < new_h:
        x = 0
        while x < new_w:
            placed = False
            for level in font_levels:
                size = int(base_font_size * level["scale"])
                font = fonts[size]
                char_w, char_h = font_dims[size]

                if x + char_w > new_w or y + char_h > new_h:
                    continue

                region = binary[y:y+char_h, x:x+char_w]
                if region.shape[0] < char_h or region.shape[1] < char_w:
                    continue

                black_ratio = np.sum(region > 128) / (char_w * char_h)

                if black_ratio >= level["threshold"]:
                    char = text[text_idx % text_len]
                    draw.text((x, y), char, font=font, fill="black")
                    text_idx += 1
                    placed = True
                    x += char_w
                    break

            if not placed:
                x += base_font_size

        y += base_font_size

    # Display the image with typographic rendering
    st.image(bg_img, caption="Typographic Output", use_container_width=True)

    # Provide download button
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        bg_img.save(tmp.name)
        st.download_button("Download Image", data=open(tmp.name, "rb"), file_name="typographic_output.png", mime="image/png")
st.markdown("---")
st.markdown("💌 A smallgift by your friend.\n\n_This app is a little piece of digital art — just like you!_ 💕")
