import os
import pickle
import pandas as pd
import numpy as np
from flask import Flask, request, render_template
from catboost import CatBoostClassifier
from tensorflow.keras.models import load_model

app = Flask(__name__)

# === Load models ===
catboost_model = CatBoostClassifier()
catboost_model.load_model('models/catboost_model.cbm')

cnn_model = load_model('models/cnn_model.keras')

# === Load preprocessing assets ===
with open('preprocessing/label_encoders.pkl', 'rb') as f:
    label_encoders = pickle.load(f)

with open('preprocessing/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open('preprocessing/target_encoder.pkl', 'rb') as f:
    target_encoder = pickle.load(f)

with open('preprocessing/catboost_categorical_features.pkl', 'rb') as f:
    cat_features = pickle.load(f)  # list of indices for CatBoost

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file and uploaded_file.filename.endswith('.csv'):
            file_path = os.path.join('uploads', uploaded_file.filename)
            uploaded_file.save(file_path)
            df = pd.read_csv(file_path)

            selected_model = request.form.get('model')

            try:
                if selected_model == 'cnn':
                    X = preprocess_for_cnn(df)
                    preds = cnn_model.predict(X)
                    preds = np.argmax(preds, axis=1)
                elif selected_model == 'catboost':
                    X = preprocess_for_catboost(df)
                    preds = catboost_model.predict(X)
                else:
                    raise ValueError("Invalid model selected.")

                # decoded = target_encoder.inverse_transform(preds.astype(int))
                if selected_model == 'catboost':
                    decoded = preds  # preds is already like ['NMAP_XMAS_TREE_SCAN']
                else:
                    decoded = target_encoder.inverse_transform(preds.astype(int))
                # return render_template('index.html', result=decoded.tolist(), file_uploaded=True)
                flat_results = [item[0] if isinstance(item, (list, np.ndarray)) else item for item in decoded.tolist()]
                return render_template('index.html', result=flat_results, file_uploaded=True)

            except Exception as e:
                return render_template('index.html', result=[f"Error: {str(e)}"], file_uploaded=True)

    return render_template('index.html', result=None, file_uploaded=False)

def preprocess_for_cnn(df):
    df = df.copy()
    for col, encoder in label_encoders.items():
        if col in df.columns:
            df[col] = encoder.transform(df[col].astype(str))  # Handle unseen safely elsewhere if needed

    if 'Attack_type' in df.columns:
        df = df.drop(columns=['Attack_type'])

    X_scaled = scaler.transform(df)
    X_reshaped = X_scaled.reshape(-1, X_scaled.shape[1], 1)
    return X_reshaped

def preprocess_for_catboost(df):
    if 'Attack_type' in df.columns:
        df = df.drop(columns=['Attack_type'])
    return df  # CatBoost handles categorical internally using `cat_features`

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
