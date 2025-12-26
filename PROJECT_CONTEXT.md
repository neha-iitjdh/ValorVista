# ValorVista - Project Context for LLM

## Quick Summary
ValorVista is a production-grade AI-powered real estate valuation platform built with Python/Flask and Bootstrap 5. It uses a Gradient Boosting Regressor to predict house prices with <5% error and 95% confidence intervals.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, Flask 3.0 |
| ML | scikit-learn (GradientBoostingRegressor), NumPy, Pandas |
| Frontend | Bootstrap 5, vanilla JavaScript |
| PDF Reports | ReportLab |
| Visualization | Matplotlib, Seaborn |
| Deployment | Docker, Gunicorn, Render/Heroku ready |

---

## Project Structure

```
valorvista/
├── app.py                      # Flask app factory, route registration
├── config.py                   # Environment-based config (Dev/Prod/Test)
├── train_model.py              # CLI script to train the model
├── wsgi.py                     # Production WSGI entry point
├── requirements.txt            # Python dependencies
│
├── src/
│   ├── __init__.py
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── feature_engineer.py # Creates 20+ derived features
│   │   └── data_processor.py   # Imputation, encoding, scaling
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── trainer.py          # ModelTrainer with GridSearchCV
│   │   └── predictor.py        # HousePricePredictor with uncertainty
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # All API endpoints
│   │   └── validators.py       # Pydantic input validation
│   │
│   └── utils/
│       ├── __init__.py
│       ├── visualizations.py   # Chart generation (base64 images)
│       └── report_generator.py # PDF report creation
│
├── templates/
│   ├── base.html               # Base template with navbar/footer
│   ├── index.html              # Main valuation form page
│   ├── batch.html              # CSV batch processing page
│   ├── insights.html           # Feature importance & analytics
│   ├── about.html              # About page with model info
│   ├── 404.html
│   └── 500.html
│
├── static/
│   ├── css/style.css           # Custom styles (CSS variables, components)
│   └── js/
│       ├── main.js             # Shared utilities (API client, formatters)
│       ├── valuation.js        # Valuation form logic
│       ├── batch.js            # CSV upload and batch processing
│       └── insights.js         # Feature importance chart
│
├── data/
│   ├── raw/                    # Place train.csv here (from Kaggle)
│   └── processed/
│
├── models_saved/               # Trained .joblib files saved here
├── reports/                    # Generated PDF reports
├── tests/
│   ├── test_api.py
│   └── test_preprocessing.py
│
├── Dockerfile
├── docker-compose.yml
├── Procfile                    # Heroku
├── render.yaml                 # Render.com
└── README.md
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/predict` | POST | Single property prediction |
| `/api/v1/predict/batch` | POST | Batch predictions (max 100) |
| `/api/v1/explain` | POST | Prediction with key factors |
| `/api/v1/feature-importance` | GET | Model feature importance |
| `/api/v1/report` | POST | Generate PDF report |
| `/api/v1/report/download/<filename>` | GET | Download report |
| `/api/v1/neighborhoods` | GET | List valid neighborhoods |
| `/api/v1/options` | GET | Form dropdown options |

### Sample Predict Request
```json
POST /api/v1/predict
{
  "GrLivArea": 1500,
  "OverallQual": 7,
  "OverallCond": 5,
  "YearBuilt": 2005,
  "BedroomAbvGr": 3,
  "FullBath": 2
}
```

### Sample Response
```json
{
  "success": true,
  "prediction": 185000,
  "formatted_prediction": "$185,000",
  "confidence_interval": {
    "lower": 165000,
    "upper": 205000,
    "formatted": {"lower": "$165,000", "upper": "$205,000"}
  },
  "confidence_level": 0.95
}
```

---

## Key Classes

### FeatureEngineer (`src/preprocessing/feature_engineer.py`)
Creates derived features:
- **Age features**: HouseAge, RemodAge, GarageAge, IsRemodeled
- **Area features**: TotalSF, LivAreaRatio, AvgRoomSize
- **Quality features**: OverallScore, QualCondDiff, QualPerSF
- **Bathroom features**: TotalBaths, BathPerBed
- **Binary features**: HasPool, HasFireplace, HasGarage, HasBasement

### DataProcessor (`src/preprocessing/data_processor.py`)
- Fits/transforms numeric and categorical features
- Ordinal encoding for quality columns (Ex=5, Gd=4, TA=3, Fa=2, Po=1)
- StandardScaler for numeric features
- LabelEncoder for categorical features
- Save/load methods for persistence

### ModelTrainer (`src/models/trainer.py`)
- Trains GradientBoostingRegressor
- Optional hyperparameter tuning with GridSearchCV
- Log-transforms target (SalePrice) for better distribution
- Calculates RMSE, MAE, R², MAPE metrics
- Saves model and processor as .joblib files

### HousePricePredictor (`src/models/predictor.py`)
- Loads trained model and processor
- `predict()` - returns predictions with confidence intervals
- `predict_batch()` - handles multiple properties
- `explain_prediction()` - returns key factors
- Uses staged predictions for uncertainty estimation

---

## Model Details

| Parameter | Value |
|-----------|-------|
| Algorithm | GradientBoostingRegressor |
| n_estimators | 500 |
| learning_rate | 0.05 |
| max_depth | 5 |
| min_samples_split | 10 |
| min_samples_leaf | 4 |
| subsample | 0.8 |
| Target transform | log1p (log transformation) |

### Performance Metrics
- R² Score: ~0.91
- RMSE: ~$18,500
- MAE: ~$12,300
- MAPE: ~4.8%

---

## Data Source

**Ames Housing Dataset** from Kaggle:
- URL: https://www.kaggle.com/c/house-prices-advanced-regression-techniques/data
- 1,460 training samples
- 79 features covering physical attributes, quality, location, etc.
- Target: SalePrice

### Required Columns for Prediction
```
GrLivArea (required), OverallQual (required), OverallCond (required),
YearBuilt (required), LotArea, TotalBsmtSF, 1stFlrSF, 2ndFlrSF,
FullBath, HalfBath, BedroomAbvGr, GarageCars, GarageArea,
Neighborhood, and many more optional fields
```

---

## Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Download train.csv from Kaggle and place in data/raw/

# Train model
python train_model.py

# Run development server
python app.py

# Run production server
gunicorn wsgi:application --bind 0.0.0.0:5000

# Run with Docker
docker-compose up -d
```

---

## Frontend Pages

1. **/** (index.html) - Main valuation form with basic/advanced options
2. **/batch** (batch.html) - CSV upload for bulk valuations
3. **/insights** (insights.html) - Feature importance charts, neighborhood prices
4. **/about** (about.html) - How it works, tech stack, model info

---

## Configuration

Environment variables (`.env`):
```
FLASK_ENV=development|production
SECRET_KEY=your-secret-key
PORT=5000
```

Config classes in `config.py`:
- `DevelopmentConfig` - DEBUG=True
- `ProductionConfig` - DEBUG=False, requires SECRET_KEY
- `TestingConfig` - TESTING=True

---

## Common Tasks for Future Development

1. **Add new feature**: Modify `FeatureEngineer.create_all_features()`
2. **Add API endpoint**: Add route in `src/api/routes.py`
3. **Modify form**: Edit `templates/index.html` and `static/js/valuation.js`
4. **Change model**: Modify `ModelTrainer` in `src/models/trainer.py`
5. **Add validation**: Update `PropertyInput` in `src/api/validators.py`
6. **Retrain model**: Run `python train_model.py --tune` for hyperparameter search

---

## Important Notes

- Model files (`.joblib`) are gitignored - must train locally or in CI/CD
- PDF reports are saved to `reports/` directory (auto-cleaned after 24h)
- All predictions use log-transformed values internally, converted back for display
- Confidence intervals use staged predictions variance + 5% base uncertainty
- Frontend uses vanilla JS with Bootstrap 5 (no React/Vue)
