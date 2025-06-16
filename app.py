from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np

app = Flask(__name__)
CORS(app)

# Load model, scaler, dan selector
model = joblib.load("model_knn.pkl")
scaler = joblib.load("scaler.pkl")
selector = joblib.load("selector.pkl")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/grafik')
def grafik():
    return render_template('grafik.html')

@app.route('/dokumentasi')
def dokumentasi():
    return render_template('dokumentasi.html')

@app.route('/dataset')
def dataset():
    return render_template('dataset.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # Ambil semua nilai input
    ph = data.get('ph')
    hardness = data.get('Hardness')
    solids = data.get('Solids')
    chloramines = data.get('Chloramines')
    sulfate = data.get('Sulfate')
    conductivity = data.get('Conductivity')
    organic_carbon = data.get('Organic_carbon')
    trihalomethanes = data.get('Trihalomethanes')
    turbidity = data.get('Turbidity')

    # Daftar alasan jika tidak layak
    reasons = []
    if ph < 6.5 or ph > 8.5:
        reasons.append(f"pH tidak dalam rentang aman (6.5–8.5), yaitu {ph}")
    if hardness > 500:
        reasons.append(f"Kekerasan (Hardness) melebihi batas: {hardness} mg/L")
    if solids > 10000:
        reasons.append(f"Total padatan terlarut (Solids) tinggi: {solids} mg/L")
    if chloramines > 4:
        reasons.append(f"Kloramin (Chloramines) melebihi batas: {chloramines} mg/L")
    if sulfate > 250:
        reasons.append(f"Kandungan sulfat (Sulfate) tinggi: {sulfate} mg/L")
    if conductivity > 2500:
        reasons.append(f"Konduktivitas (Conductivity) terlalu tinggi: {conductivity} µS/cm")
    if organic_carbon > 3:
        reasons.append(f"Karbon organik (Organic Carbon) melebihi batas: {organic_carbon} mg/L")
    if trihalomethanes > 80:
        reasons.append(f"Trihalometana (Trihalomethanes) terlalu tinggi: {trihalomethanes} µg/L")
    if turbidity > 5:
        reasons.append(f"Kekeruhan (Turbidity) tinggi: {turbidity} NTU")

    # Feature engineering
    sulfate_ratio = sulfate / (conductivity + 1e-6)
    is_acidic = int(ph < 7)

    # Susun fitur awal
    features = [ph, hardness, solids, chloramines, sulfate,
                conductivity, organic_carbon, trihalomethanes, turbidity,
                sulfate_ratio, is_acidic]

    # Transformasi & seleksi fitur
    X = scaler.transform([features])
    X_selected = selector.transform(X)

# Prediksi model
    model_prediction = model.predict(X_selected)[0]

# Override prediksi: jika ada alasan, anggap tidak layak
    if reasons:
        prediction = 0
    else:
        prediction = int(model_prediction)

    return jsonify({'prediction': prediction, 'reasons': reasons})

if __name__ == '__main__':
    app.run(debug=True)
