import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image

from keras.models import load_model
from keras.utils import load_img, img_to_array

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kunci-rahasia-anda-yang-sulit-ditebak'

disease_info_db = {
    "Bercak Daun": {
        "description": "Penyakit ini disebabkan oleh jamur *Pestalotiopsis psidii*. Gejalanya berupa bercak coklat kecil pada daun yang dapat membesar seiring waktu, seringkali dengan bagian tengah yang lebih terang. Infeksi parah dapat menyebabkan daun rontok.",
        "handling": "Pangkas dan musnahkan daun yang terinfeksi untuk mengurangi penyebaran. Semprotkan fungisida yang mengandung bahan aktif seperti mankozeb atau propineb. Pastikan sirkulasi udara di sekitar tanaman baik.",
        "youtube_link": "https://www.youtube.com/watch?v=0x4RUWDYGTM"
    },
    "Karat Merah": {
        "description": "Karat merah atau 'Red Rust' disebabkan oleh alga (ganggang) *Cephaleuros virescens*. Gejalanya adalah munculnya bercak oranye kemerahan seperti beludru pada permukaan daun. Penyakit ini dapat menghambat fotosintesis.",
        "handling": "Lakukan sanitasi kebun dengan membersihkan gulma dan daun yang jatuh. Pangkas bagian tanaman yang terinfeksi berat. Aplikasikan fungisida atau bakterisida yang mengandung tembaga hidroksida.",
        "youtube_link": "https://www.youtube.com/watch?v=Og72IHR6rO0"
    },
    "Daun Sehat": {
        "description": "Tidak ditemukan indikasi penyakit jamur atau alga yang signifikan pada daun ini. Daun tampak sehat dengan warna hijau yang seragam dan tidak ada bercak atau kerusakan yang mencurigakan.",
        "handling": "Teruskan praktik perawatan yang baik. Lakukan pemupukan berimbang, penyiraman yang cukup, dan inspeksi rutin untuk mendeteksi masalah sejak dini.",
        "youtube_link": None
    },
    "default": {
        "description": "Objek yang dideteksi tidak teridentifikasi sebagai salah satu penyakit umum pada daun jambu kristal dalam database kami.",
        "handling": "Pastikan gambar yang diunggah adalah daun jambu kristal dengan pencahayaan yang baik dan fokus yang jelas. Coba ambil gambar dari sudut yang berbeda jika perlu.",
        "youtube_link": None
    }
}


model_xception = load_model("models/Xception2L.h5")
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'jfif'}

def allowed_file(filename):
    """Mengecek apakah ekstensi file diizinkan."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

            if prediction_class in disease_info_db:
                info = disease_info_db[prediction_class]
            else:
                info = disease_info_db["default"]

            return render_template(
                "classifications.html",
                prediction=prediction_class,
                confidence=f'{confidence * 100:.2f}%',
                img_path=image_path,
                disease_description=info["description"],
                disease_handling=info["handling"],
                youtube_link=info["youtube_link"]
            )

        except Exception as e:
            flash(f'Terjadi error saat memproses gambar: {e}')
            return redirect(request.url)
    else:
        flash('Jenis file tidak diizinkan. Harap unggah file gambar.')
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)