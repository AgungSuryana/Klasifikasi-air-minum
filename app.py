from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

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

    # Ambil input
    ph = data.get('ph')
    hardness = data.get('Hardness')
    solids = data.get('Solids')
    chloramines = data.get('Chloramines')
    sulfate = data.get('Sulfate')
    conductivity = data.get('Conductivity')
    organic_carbon = data.get('Organic_carbon')
    trihalomethanes = data.get('Trihalomethanes')
    turbidity = data.get('Turbidity')

    # Validasi dari rentang layak
    reasons = []

    if not (0.227 <= ph <= 13.175):
        reasons.append(f"pH di luar rentang data layak (0.227 – 13.175): {ph}")
    if not (47.432 <= hardness <= 323.124):
        reasons.append(f"Hardness di luar rentang data layak (47.432 – 323.124): {hardness}")
    if not (728.751 <= solids <= 56488.672):
        reasons.append(f"Solids di luar rentang data layak (728.751 – 56488.672): {solids}")
    if not (0.352 <= chloramines <= 13.127):
        reasons.append(f"Chloramines di luar rentang data layak (0.352 – 13.127): {chloramines}")
    if not (129.000 <= sulfate <= 481.031):
        reasons.append(f"Sulfate di luar rentang data layak (129.000 – 481.031): {sulfate}")
    if not (201.620 <= conductivity <= 695.370):
        reasons.append(f"Conductivity di luar rentang data layak (201.620 – 695.370): {conductivity}")
    if not (2.200 <= organic_carbon <= 23.604):
        reasons.append(f"Organic Carbon di luar rentang data layak (2.200 – 23.604): {organic_carbon}")
    if not (8.176 <= trihalomethanes <= 124.000):
        reasons.append(f"Trihalomethanes di luar rentang data layak (8.176 – 124.000): {trihalomethanes}")
    if not (1.492 <= turbidity <= 6.494):
        reasons.append(f"Turbidity di luar rentang data layak (1.492 – 6.494): {turbidity}")

    # Engineering tambahan
    sulfate_ratio = sulfate / (conductivity + 1e-6)
    is_acidic = int(ph < 7)

    # Susun fitur
    features = [ph, hardness, solids, chloramines, sulfate,
                conductivity, organic_carbon, trihalomethanes, turbidity,
                sulfate_ratio, is_acidic]

    # Transformasi dan seleksi
    X = scaler.transform([features])
    X_selected = selector.transform(X)

    # Prediksi dari model
    model_prediction = model.predict(X_selected)[0]

    # Jika ada alasan, anggap tidak layak
    prediction = 0 if reasons else int(model_prediction)

    # Saran perbaikan
    suggestions = []
    if prediction == 0:
        try:
            distances = euclidean_distances(X_selected, model._fit_X)
            nearest_indices = distances[0].argsort()[:model.n_neighbors]
            layak_indices = [i for i in nearest_indices if model._y[i] == 1]

            if layak_indices:
                avg_scaled = model._fit_X[layak_indices].mean(axis=0).reshape(1, -1)

                # Invers ke bentuk unscaled
                dummy_all_features = np.zeros((1, selector.estimator_.n_features_in_))
                dummy_all_features[:, selector.get_support()] = avg_scaled
                avg_unscaled = scaler.inverse_transform(dummy_all_features)[0]

                delta = avg_scaled[0] - X_selected[0]
                top_changed = np.argsort(np.abs(delta))[::-1][:3]
                delta = avg_scaled[0] - X_selected[0]
                top_changed = np.argsort(np.abs(delta))[::-1][:3]

                selected_feature_names = selector.get_feature_names_out(input_features=[
                    'ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate',
                    'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity',
                    'sulfate_conductivity_ratio', 'is_acidic'
                ])
# Ambil indeks fitur asli
                # Ambil indeks fitur asli yang disarankan untuk diubah
                selected_indices = selector.get_support(indices=True)

                # Daftar nama semua fitur awal
                full_feature_names = [
                    'ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate',
                    'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity',
                    'sulfate_conductivity_ratio', 'is_acidic'
                ]

                # Ambil nilai input asli
                input_values = np.array([ph, hardness, solids, chloramines, sulfate,
                                        conductivity, organic_carbon, trihalomethanes,
                                        turbidity, sulfate_ratio, is_acidic])

                # Hitung delta berdasarkan nilai asli
                true_deltas = np.abs(avg_unscaled[selected_indices] - input_values[selected_indices])

                # Hanya pilih fitur dengan delta terbesar dan SELISIH SIGNIFIKAN (misal > threshold)
                threshold = 0.1  # bisa disesuaikan tergantung sensitifitas
                top_changed = np.argsort(true_deltas)[::-1]

                # Ambil max 3 fitur tapi hanya yang delta-nya besar
                suggestions = []
                count = 0
                for i in top_changed:
                    if true_deltas[i] > threshold:
                        fname = full_feature_names[selected_indices[i]]
                        target_val = avg_unscaled[selected_indices[i]]
                        suggestions.append(f"Pertimbangkan ubah '{fname}' ke sekitar {target_val:.2f} (nilai rata-rata layak)")
                        count += 1
                    if count == 3:
                        break

        except Exception as e:
            suggestions.append(f"Gagal menghitung saran perbaikan: {str(e)}")

    return jsonify({
        'prediction': prediction,
        'reasons': reasons,
        'suggestions': suggestions
    })

if __name__ == '__main__':
    app.run(debug=True)
