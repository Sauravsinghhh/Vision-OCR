import os
import pytesseract
from flask import Flask, render_template, request, jsonify
from PIL import Image
from werkzeug.utils import secure_filename

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
            # Perform OCR
            img = Image.open(filepath)
            # Use local tessdata directory explicitly
            tessdata_dir = os.path.join(os.path.dirname(__file__), 'tessdata')
            config = f'--tessdata-dir "{tessdata_dir}"'
            text = pytesseract.image_to_string(img, config=config)
            
            # Basic cleanup: remove temporary file if you want, or keep it
            # os.remove(filepath)
            
            return jsonify({
                'success': True,
                'text': text.strip() if text else "No text found in image."
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
            
    return jsonify({'success': False, 'error': 'Invalid file type'})

if __name__ == '__main__':
    app.run(debug=True)
