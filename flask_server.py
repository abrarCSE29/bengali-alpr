from flask import Flask, request, jsonify, send_file, url_for
import utils
from werkzeug.utils import secure_filename
import os
import cv2
import socket

app = Flask(__name__, static_url_path='/static')

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
DETECTION_FOLDER = os.path.join(STATIC_FOLDER, 'detections')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DETECTION_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to get server's IP address
def get_server_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

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
            # Get both the text and the image with bounding box
            lp_text, img_with_bbox = utils.detect_and_extract_lp_text(filepath, show_cropped_image=False, draw_bbox=True)
            print("This is from server: ", lp_text)
            
            # Save the image with bounding box to the static folder
            bbox_filename = f"bbox_{filename}"
            bbox_filepath = os.path.join(DETECTION_FOLDER, bbox_filename)
            cv2.imwrite(bbox_filepath, img_with_bbox)
            
            # Get server IP address
            server_ip = get_server_ip()
            
            # Create a URL for the image using server IP
            image_url = f"http://{server_ip}:5000/static/detections/{bbox_filename}"
            
            # Delete the temporary upload file
            os.remove(filepath)
            
            return jsonify({
                'license_plate_text': lp_text,
                'image_url': image_url,
            }), 200
        except Exception as e:
            # Delete the temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Error processing image: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Add a route to display server information
@app.route('/', methods=['GET'])
def server_info():
    server_ip = get_server_ip()
    return jsonify({
        'server_ip': server_ip,
        'server_port': 5000,
        'status': 'running'
    })

if __name__ == '__main__':
    server_ip = get_server_ip()
    print(f"Server running at: http://{server_ip}:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)