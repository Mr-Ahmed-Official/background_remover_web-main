import os
import io
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageFilter, ImageOps
from rembg import remove

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def clean_edges(img):
    r, g, b, a = img.split()
    inverted_alpha = ImageOps.invert(a)
    blurred = inverted_alpha.filter(ImageFilter.GaussianBlur(2))
    final_alpha = ImageOps.invert(blurred)
    img.putalpha(final_alpha)
    return img

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]
        if file:
            input_bytes = file.read()
            output = remove(input_bytes)
            img = Image.open(io.BytesIO(output)).convert("RGBA")

            alpha = img.getchannel("A")
            alpha = alpha.filter(ImageFilter.GaussianBlur(radius=1.5))
            img.putalpha(alpha)
            img = clean_edges(img)

            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            return send_file(buffer, mimetype='image/png', as_attachment=True,
                             download_name=f"{os.path.splitext(file.filename)[0]}_nobg.png")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
