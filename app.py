# from flask import Flask, render_template, request, send_from_directory
# import qrcode
# from PIL import Image
# import os

# app = Flask(__name__)

# # directory for storing qr codes 
# os.makedirs("static/qr_codes", exist_ok=True)
# os.makedirs("static/logo", exist_ok=True)

# @app.route("/")
# def index():
#   """Render the Home Page"""
#   return render_template("index.html")

# @app.route("/generate", methods=['POST'])
# def generate():
#   """Generate a QR Code based on form input"""
#   try:
#     # get form data
#     data = request.form.get("data")
#     fill_color = request.form.get("fill_color", "black")
#     back_color = request.form.get("back_color", "white")
#     logo_path = request.file.get("logo")

#     if not data:
#       return "ERROR data cannot be empty", 400
    
#     # generate qr code
#     qr = qrcode.QRCode(
#       version = 2,
#       error_correction = qrcode.constants.ERROR_CORRECT_H,
#       box_size =10,
#       border = 4
#     )
#     qr.add_data(data)
#     qr.make(fit=True)

#     img = qr.make_image(fill_color= fill_color, back_color= back_color)


#     # add logo if provided
#     if logo_path:
#       logo_filename = os.path.join("static/logo", logo_path.filename)
#       logo_path.save(logo_filename)
#       logo = Image.open(logo_filename)
#       logo_size = (img.size[0]//4, img.size[1]// 4)
#       logo = logo.resize(logo_size)
#       img = img.convert("RGBA")

#       logo_position = (
#         (img.size[0] // logo.size[0] // 2),
#         (img.size[1] // logo.size[1] //2)
#       )

#       img.paste(logo, logo_position, mask=logo)

#     # save qr code image
#     output_file = f"static/qr_codes/{data.replace(' ', '_')}.png"
#     Image.save(output_file)

#     return render_template("result.html", qr_code=output_file)
  
#   except Exception as e:
#     print(f"ERROR Generating QRCode: {e}")

# @app.route("/static/<path:filename>")
# def serve_file(filename):
#   """Serve static files (QR Code)"""
#   return send_from_directory("static",filename)

# if __name__ == "__main__":
#   app.run(debug=True)


from flask import Flask, render_template, request, send_from_directory, jsonify
import qrcode
from PIL import Image
import os

app = Flask(__name__)

# Create directories for storing QR codes
os.makedirs("static/qr_codes", exist_ok=True)
os.makedirs("static/logo", exist_ok=True)

@app.errorhandler(404)
def page_not_found(e):
    """Costum 404 page"""
    return render_template('error.html', e = "sorry that page does not exist."), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Costum 500 error page"""
    return render_template('error.html', e = "internal server error.")

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    """catch all error handler"""
    return render_template('error.html', e = "unexpected error")

@app.route("/")
def index():
    """Render the home page."""
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_qr():
    """Generate a QR code based on form input."""
    try:
        # Get form data
        data = request.form.get("data")
        fill_color = request.form.get("fill_color", "black")
        back_color = request.form.get("back_color", "white")
        logo_path = request.files.get("logo")

        # errors
        if not data.strip():
          raise ValueError("The text or URL for the QR code cannot be empty.")
        
        if not fill_color.isalnum() or not back_color.isalnum():
          raise ValueError("Colors must be valid names (e.g., 'black', 'white').")
        
        if logo_path and not logo_path.filename.lower().endswith((".png", ".jpg", ".jpeg")):
          raise ValueError("Only PNG and JPG images are allowed for logos.")

        # Generate QR code
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        # Add logo if provided
        if logo_path:
            logo_filename = os.path.join("static/logo", logo_path.filename)
            logo_path.save(logo_filename)
            logo = Image.open(logo_filename)
            logo_size = (img.size[0] // 4, img.size[1] // 4)
            logo = logo.resize(logo_size)
            img = img.convert("RGBA")
            logo_position = (
                (img.size[0] - logo.size[0]) // 2,
                (img.size[1] - logo.size[1]) // 2,
            )
            img.paste(logo, logo_position, mask=logo)

        # Save QR code image
        output_file = f"static/qr_codes/qr_code.png"
        if not os.path.exists(output_file):
          raise FileNotFoundError("The QR code file could not be found.")

        # filename = "".join(i for i in s if i not in "\/:*?<>|")
        img.save(output_file)

        return render_template("result.html", qr_code=output_file)

    except ValueError as ve:
      return render_template('error.html', e = str(ve)), 400
    
    except FileNotFoundError:
        return render_template('error.html', e = "File not found! Please check your input."), 404

    except Exception as x:
        return render_template('error.html' ,e = f"Unexpected Error: {x}"), 500


@app.route("/static/<path:filename>")
def serve_file(filename):
    """Serve static files (QR codes)."""
    return send_from_directory("static", filename)


if __name__ == "__main__":
    app.run(debug=True)
