import os
import uuid
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from audio_processor import process_audio

app = Flask(__name__)
app.secret_key = "secret_key_for_session" # In a real app, use a secure random key

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'm4p', 'flac', 'ogg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB limit

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def handle_upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        original_filename = file.filename
        extension = original_filename.rsplit('.', 1)[1].lower()
        
        # Secure the name part but keep the extension safe
        name_part = secure_filename(original_filename.rsplit('.', 1)[0])
        if not name_part:
            name_part = "audio"
            
        # Use UUID to avoid collisions
        unique_id = str(uuid.uuid4())
        input_filename = f"{unique_id}_{name_part}.{extension}"
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        file.save(input_path)
        
        output_filename = f"cleaned_{unique_id}_{name_part}.{extension}"
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
        
        try:
            process_audio(input_path, output_path)
            return send_file(output_path, as_attachment=True, download_name=f"cleaned_{name_part}.{extension}")
        except Exception as e:
            import traceback
            print(f"ERROR: {str(e)}")
            traceback.print_exc()
            flash(f"An error occurred during processing: {str(e)}")
            return redirect(url_for('index'))
    else:
        flash('Allowed file types are wav, mp3, m4a, flac, ogg')
        return redirect(request.url)

if __name__ == '__main__':
    # Ensure folders exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5001)
