import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image

# Menggunakan impor modern dari Keras/TensorFlow
from keras.models import load_model
from keras.utils import load_img, img_to_array

# --- Inisialisasi Aplikasi Flask ---
app = Flask(__name__)

# Kunci rahasia diperlukan untuk menampilkan pesan error (flash messages)
app.config['SECRET_KEY'] = 'kunci-rahasia-anda-yang-sulit-ditebak'

# --- Konfigurasi Model dan File Upload ---

# HANYA MUAT MODEL YANG DIGUNAKAN UNTUK MENGHEMAT MEMORI
# Model lain bisa dimuat jika diperlukan di route yang berbeda
model_xception = load_model("models/Xception2L.h5")
# model_resnet = load_model("ResNet50.h5") # Dihapus karena tidak dipakai
# model_vgg = load_model("VGG16.h5") # Dihapus karena tidak dipakai
# model_inception = load_model("InceptionV3.h5") # Dihapus karena tidak dipakai

# Konfigurasi folder upload dan ekstensi yang diizinkan
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'jfif'}

def allowed_file(filename):
    """Mengecek apakah ekstensi file diizinkan."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes Aplikasi ---

@app.route("/", methods=['GET'])
def main():
    """Menampilkan halaman utama untuk upload."""
    return render_template("classifications.html")

@app.route('/predict', methods=['POST'])
def predict():
    """Menerima file gambar, melakukan prediksi, dan menampilkan hasil."""
    

    if 'image_file' not in request.files:
        flash('Tidak ada bagian file dalam request.')
        return redirect(request.url)

    file = request.files['image_file']

    if file.filename == '':
        flash('Tidak ada gambar yang dipilih untuk diunggah.')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%d%m%y-%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        

        file.save(image_path)
        

        try:

            img = load_img(image_path, target_size=(128, 128))
            x = img_to_array(img)
            x = x / 127.5 - 1  
            x = np.expand_dims(x, axis=0)
            images = np.vstack([x])


            prediction_array = model_xception.predict(images)


            class_names = ['Bercak Daun', 'Daun Sehat', 'Karat Merah']
            threshold = 0.6  

            confidence = np.max(prediction_array)
            

            if confidence > threshold:
                prediction_class = class_names[np.argmax(prediction_array)]
            else:
                prediction_class = "Bukan Penyakit Jambu Kristal"

            return render_template(
                "index.html",
                prediction=prediction_class,
                confidence=f'{confidence * 100:.2f}%',
                img_path=image_path
            )

        except Exception as e:
            flash(f'Terjadi error saat memproses gambar: {e}')
            return redirect(request.url)

    else:
        flash('Jenis file tidak diizinkan. Harap unggah file gambar.')
        return redirect(request.url)


if __name__ == '__main__':
    app.run(debug=True)