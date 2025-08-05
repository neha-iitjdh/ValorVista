# ValorVista

AI-powered real estate valuation platform that forecasts property prices using advanced regression models. Get instant, accurate estimates tailored to market dynamics.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

## Features

- **Instant Valuations**: Get property price predictions in under a second
- **High Accuracy**: Gradient Boosting model achieving <5% mean absolute percentage error
- **Confidence Intervals**: 95% confidence bounds for transparent predictions
- **Batch Processing**: Upload CSV files for bulk property valuations
- **PDF Reports**: Generate professional valuation reports
- **Market Insights**: Explore feature importance and neighborhood analysis
- **RESTful API**: Full API access for third-party integrations
- **Mobile-Friendly**: Responsive design for on-site use

## Tech Stack

- **Backend**: Python, Flask, scikit-learn
- **ML Model**: Gradient Boosting Regressor (500 estimators)
- **Frontend**: Bootstrap 5, JavaScript
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn
- **PDF Generation**: ReportLab

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/valorvista.git
cd valorvista
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download training data:
   - Get the dataset from [Kaggle House Prices Competition](https://www.kaggle.com/c/house-prices-advanced-regression-techniques/data)
   - Place `train.csv` in `data/raw/`

5. Train the model:
```bash
python train_model.py
```

6. Run the application:
```bash
python app.py
```

7. Open http://localhost:5000 in your browser

## Project Structure

```
valorvista/
├── app.py                 # Flask application entry point
├── config.py              # Configuration management
├── train_model.py         # Model training script
├── wsgi.py               # WSGI entry point
├── requirements.txt       # Python dependencies
│
├── src/
│   ├── api/              # API routes and validators
│   ├── models/           # ML model and predictor
│   ├── preprocessing/    # Data processing and feature engineering
│   └── utils/            # Utilities, visualizations, reports
│
├── static/
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript files
│
├── templates/            # HTML templates
├── data/
│   ├── raw/              # Raw training data
│   └── processed/        # Processed data
│
├── models_saved/         # Trained model files
├── reports/              # Generated PDF reports
└── tests/                # Test suite
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/predict` | POST | Single property prediction |
| `/api/v1/predict/batch` | POST | Batch predictions |
| `/api/v1/explain` | POST | Prediction explanation |
| `/api/v1/feature-importance` | GET | Model feature importance |
| `/api/v1/report` | POST | Generate PDF report |
| `/api/v1/neighborhoods` | GET | List of neighborhoods |
| `/api/v1/options` | GET | Form options |

### Example API Request

```bash
curl -X POST http://localhost:5000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "GrLivArea": 1500,
    "OverallQual": 7,
    "OverallCond": 5,
    "YearBuilt": 2005,
    "BedroomAbvGr": 3,
    "FullBath": 2
  }'
```

### Response

```json
{
  "success": true,
  "prediction": 185000,
  "formatted_prediction": "$185,000",
  "confidence_interval": {
    "lower": 165000,
    "upper": 205000,
    "formatted": {
      "lower": "$165,000",
      "upper": "$205,000"
    }
  },
  "confidence_level": 0.95
}
```

## Model Performance

| Metric | Value |
|--------|-------|
| R² Score | 0.91 |
| RMSE | $18,500 |
| MAE | $12,300 |
| MAPE | 4.8% |

## Deployment

### Docker

```bash
docker build -t valorvista .
docker run -p 5000:5000 valorvista
```

### Docker Compose

```bash
docker-compose up -d
```

### Render

Deploy directly using the `render.yaml` configuration file.

### Heroku

```bash
heroku create valorvista
git push heroku main
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
PORT=5000
```

## Running Tests

```bash
pytest tests/ -v
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Dataset: [Ames Housing Dataset](https://www.kaggle.com/c/house-prices-advanced-regression-techniques)
- Inspired by modern real estate valuation tools
