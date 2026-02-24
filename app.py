import os
import pytesseract
from flask import Flask, render_template, request, jsonify
from PIL import Image
from werkzeug.utils import secure_filename
import cv2
import numpy as np

# Tesseract Configuration
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Point to the local tessdata directory
os.environ['TESSDATA_PREFIX'] = r"c:\Users\Saurav\Desktop\OCR\tessdata"

app = Flask(__name__)

# Configure Upload Folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    """
    Advanced image preprocessing for better OCR extraction.
    """
    # Load image using OpenCV
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply denoising
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # Apply adaptive thresholding to handle uneven lighting/shadows
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Save the preprocessed image for Tesseract to read
    processed_path = image_path.replace('.', '_processed.')
    cv2.imwrite(processed_path, thresh)
    return processed_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Perform image preprocessing
            processed_filepath = preprocess_image(filepath)
            
            # Perform OCR on processed image
            img = Image.open(processed_filepath)
            
            # Use local tessdata directory explicitly
            tessdata_dir = os.path.join(os.path.dirname(__file__), 'tessdata')
            # Optimized config for better accuracy (PSM 3 is default but explicit is better)
            config = f'--tessdata-dir "{tessdata_dir}" --psm 3'
            text = pytesseract.image_to_string(img, config=config)
            
            # Cleanup: remove processed temporary file
            if os.path.exists(processed_filepath):
                os.remove(processed_filepath)
            
            return jsonify({
                'success': True,
                'text': text.strip() if text else "No text found in image."
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
            
    return jsonify({'success': False, 'error': 'Invalid file type'})

if __name__ == '__main__':
    app.run(debug=True)
