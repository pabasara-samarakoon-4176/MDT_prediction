# AI-Driven MDT Footprint Prediction

This repository contains the source code, data pipeline, and model implementations for **AI-Driven MDT (Minimization of Drive Test) Footprint Prediction**, developed in collaboration with **Dialog Axiata PLC**. The project leverages geospatial features, synthetic MDT data, and transformer-based deep learning models to predict **RSRP** and **RSRQ** coverage footprints.

---

## 📌 Project Overview

Drive Tests are costly and time-consuming for mobile operators. This project uses **Minimization of Drive Test (MDT)** techniques and **AI-based prediction** to estimate coverage footprints without extensive field measurements.

We integrate:

* **Geospatial data** (NDVI, Population, roads, buildings, population density)
* **Antenna parameters** (azimuth, tilt, height)
* **Synthetic MDT data** for privacy-preserving training
* **Transformer-based models** for footprint prediction

---

## 🏗️ System Architecture

The system is divided into:

1. **Data Ingestion** – MDT CSVs, OSM, DEM, NDVI, WorldPop
2. **Preprocessing** – raster sampling, vector aggregation, geohash encoding, feature engineering
3. **Feature Store** – cleaned datasets stored in Parquet/PostGIS
4. **Model Training** – multiple transformer architectures (V1–V5)
5. **Model Serving** – REST API for predictions & heatmaps
6. **Monitoring** – drift detection and retraining pipeline

---

## 🔄 Model Versions

* **Model 1 (V1)** – Single-Head Transformer with Geohash positional encoding

  * Dataset: 512 geohash cells
  * Results: MSE = 66.47, MAE = 6.74, R² = –0.0186

* **Model 2 (V2)** – Multi-Head Transformer with richer dataset

  * Dataset: 100K+ records (added road coverage & population density)
  * Results: MSE = 0.4546, MAE = 13.33, R² = 0.58

* **Model 3 (V3)** – Transformer with sequence-aware input

  * Dataset structured into sequences of 256 points
  * Results: MSE = 61.28, MAE = 7.83, R² = 0.09

* **Model 4 → 5 (V5 Final)** – Absolute → Relative location mapping

  * Pipeline: `Absolute → Relative → Transformer → Relative → Absolute`
  * Multiscale transformer backbone with uncertainty estimation
  * Improved generalization and stability

---

## ⚙️ Installation

```bash
# Clone repository
git clone https://github.com/<your-org>/MDT_prediction.git
cd MDT_prediction-main

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 📊 Evaluation Metrics

* RMSE, MAE, R²
* Calibration of uncertainty estimates
* Sector-wise error breakdown

---

## 🛠️ Tech Stack

* **Python 3.10**
* **PyTorch 2.x / TensorFlow**
* **GeoPandas, Rasterio, Shapely** for geospatial processing
* **Postgres + PostGIS** for spatial queries
* **FastAPI** for serving
* **MLflow** for experiment tracking

---

## 📈 Future Work

* Integration with real MDT data (privacy-compliant)
* Enhanced cell boundary detection
* Online model retraining & monitoring

---

## 👥 Authors

Group 05 — University of Ruhuna
In collaboration with **Dialog Axiata PLC**

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.
