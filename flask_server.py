from flask import Flask, request, jsonify
import utils
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/detect_license_plate', methods=['POST'])
def detect_license_plate():
    try:
        # Check if an image file was provided
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        
        # Check if filename is valid and file type is allowed
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only jpg, jpeg, and png are allowed'}), 400

        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process the image using the utils function
        try:
            lp_text = utils.detect_and_extract_lp_text(filepath)
            print("This is from server: " ,lp_text)
            # Delete the temporary file
            
            return jsonify({'license_plate_text': lp_text}), 200
        except Exception as e:
            # Delete the temporary file
            return jsonify({'error': f'Error processing image: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)