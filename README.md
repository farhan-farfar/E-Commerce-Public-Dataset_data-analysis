# Proyek Analisis Data: E-Commerce Public Dataset

Proyek ini menganalisis data pesanan e-commerce (Olist, Brasil) untuk menjawab:
1. Kategori produk dengan revenue tertinggi dan terendah (2017) serta tren revenue bulanan (Jan 2017 - Agu 2018).
2. State dengan persentase keterlambatan pengiriman tertinggi (2017-2018) dan kaitannya dengan skor review.
3. Segmentasi pelanggan dengan RFM Analysis.

## Struktur Direktori
```
submission
├── dashboard
│   ├── main_data.csv
│   ├── rfm_data.csv
│   └── dashboard.py
├── data
│   └── (9 file CSV dataset asli)
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment
```
pip install -r requirements.txt
```

(Opsional, dengan virtual environment)
```
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan Dashboard
Jalankan dari folder `submission`:
```
streamlit run dashboard/dashboard.py
```
Dashboard akan terbuka di browser pada `http://localhost:8501`.
