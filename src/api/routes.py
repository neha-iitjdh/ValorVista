"""
API Routes for ValorVista.
Defines all REST endpoints for the application.
"""

import os
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from flask import Blueprint, request, jsonify, current_app, send_file
import pandas as pd
import numpy as np

from src.models import HousePricePredictor
from src.api.validators import PropertyInput, BatchInput
from src.utils.report_generator import ReportGenerator
from pydantic import ValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

# Global predictor instance (initialized on first request)
_predictor = None


def get_predictor() -> HousePricePredictor:
    """Get or initialize the predictor instance."""
    global _predictor
    if _predictor is None:
        from config import Config
        _predictor = HousePricePredictor(
            model_path=Config.MODEL_PATH,
            processor_path=Config.PREPROCESSOR_PATH
        )
    return _predictor


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })


@api_bp.route("/predict", methods=["POST"])
def predict():
    """
    Single property prediction endpoint.

    Request body should contain property features.
    Returns predicted price with confidence interval.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No input data provided"
            }), 400

        # Validate input
        try:
            validated = PropertyInput(**data)
            model_input = validated.to_model_input()
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": "Validation error",
                "details": e.errors()
            }), 400

        # Get prediction
        predictor = get_predictor()
        result = predictor.predict(model_input)

        return jsonify({
            "success": True,
            "prediction": result["predictions"][0],
            "formatted_prediction": result["formatted_predictions"][0],
            "confidence_interval": result.get("prediction_intervals", [{}])[0],
            "confidence_level": result.get("confidence_level", 0.95),
            "input_summary": {
                "living_area": model_input.get("GrLivArea"),
                "bedrooms": model_input.get("BedroomAbvGr"),
                "bathrooms": model_input.get("FullBath", 0) + 0.5 * model_input.get("HalfBath", 0),
                "year_built": model_input.get("YearBuilt"),
                "overall_quality": model_input.get("OverallQual")
            }
        })

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/predict/batch", methods=["POST"])
def predict_batch():
    """
    Batch property prediction endpoint.

    Request body should contain list of properties.
    Returns predictions for all properties with statistics.
    """
    try:
        data = request.get_json()

        if not data or "properties" not in data:
            return jsonify({
                "success": False,
                "error": "No properties provided"
            }), 400

        # Validate batch input
        try:
            validated = BatchInput(**data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": "Validation error",
                "details": e.errors()
            }), 400

        # Convert to model inputs
        model_inputs = [prop.to_model_input() for prop in validated.properties]

        # Get predictions
        predictor = get_predictor()
        results = predictor.predict_batch(model_inputs)

        # Calculate summary statistics
        predictions = [r["prediction"] for r in results]
        summary = {
            "count": len(predictions),
            "mean": np.mean(predictions),
            "median": np.median(predictions),
            "min": np.min(predictions),
            "max": np.max(predictions),
            "std": np.std(predictions),
            "formatted": {
                "mean": f"${np.mean(predictions):,.0f}",
                "median": f"${np.median(predictions):,.0f}",
                "range": f"${np.min(predictions):,.0f} - ${np.max(predictions):,.0f}"
            }
        }

        return jsonify({
            "success": True,
            "total_properties": len(results),
            "predictions": results,
            "summary_statistics": summary
        })

    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/explain", methods=["POST"])
def explain_prediction():
    """
    Explain prediction for a property.

    Returns prediction with feature importance and explanation.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No input data provided"
            }), 400

        # Validate input
        try:
            validated = PropertyInput(**data)
            model_input = validated.to_model_input()
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": "Validation error",
                "details": e.errors()
            }), 400

        # Get explanation
        predictor = get_predictor()
        explanation = predictor.explain_prediction(model_input)

        return jsonify({
            "success": True,
            **explanation
        })

    except Exception as e:
        logger.error(f"Explanation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/feature-importance", methods=["GET"])
def get_feature_importance():
    """Get feature importance from the trained model."""
    try:
        top_n = request.args.get("top_n", 20, type=int)
        predictor = get_predictor()
        importance = predictor.get_feature_importance(top_n)

        return jsonify({
            "success": True,
            "feature_importance": importance
        })

    except Exception as e:
        logger.error(f"Feature importance error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/report", methods=["POST"])
def generate_report():
    """
    Generate PDF report for property valuation.

    Returns URL to download the generated report.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No input data provided"
            }), 400

        # Validate input
        try:
            validated = PropertyInput(**data)
            model_input = validated.to_model_input()
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": "Validation error",
                "details": e.errors()
            }), 400

        # Get prediction and explanation
        predictor = get_predictor()
        prediction_result = predictor.predict(model_input)
        explanation = predictor.explain_prediction(model_input)
        feature_importance = predictor.get_feature_importance(10)

        # Generate report
        report_generator = ReportGenerator()
        report_id = str(uuid.uuid4())[:8]
        report_filename = f"valuation_report_{report_id}.pdf"

        from config import Config
        report_path = Config.REPORTS_DIR / report_filename

        report_generator.generate_report(
            property_data=model_input,
            prediction=prediction_result,
            explanation=explanation,
            feature_importance=feature_importance,
            output_path=report_path
        )

        return jsonify({
            "success": True,
            "report_id": report_id,
            "download_url": f"/api/v1/report/download/{report_filename}"
        })

    except Exception as e:
        logger.error(f"Report generation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/report/download/<filename>", methods=["GET"])
def download_report(filename: str):
    """Download generated report."""
    try:
        from config import Config
        report_path = Config.REPORTS_DIR / filename

        if not report_path.exists():
            return jsonify({
                "success": False,
                "error": "Report not found"
            }), 404

        return send_file(
            report_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Report download error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/neighborhoods", methods=["GET"])
def get_neighborhoods():
    """Get list of valid neighborhoods."""
    neighborhoods = [
        "Blmngtn", "Blueste", "BrDale", "BrkSide", "ClearCr",
        "CollgCr", "Crawfor", "Edwards", "Gilbert", "IDOTRR",
        "MeadowV", "Mitchel", "NAmes", "NoRidge", "NPkVill",
        "NridgHt", "NWAmes", "OldTown", "SWISU", "Sawyer",
        "SawyerW", "Somerst", "StoneBr", "Timber", "Veenker"
    ]
    return jsonify({
        "success": True,
        "neighborhoods": neighborhoods
    })


@api_bp.route("/options", methods=["GET"])
def get_form_options():
    """Get all form options for the frontend."""
    return jsonify({
        "success": True,
        "options": {
            "buildingTypes": [
                {"value": "1Fam", "label": "Single-family Detached"},
                {"value": "2FmCon", "label": "Two-family Conversion"},
                {"value": "Duplx", "label": "Duplex"},
                {"value": "TwnhsE", "label": "Townhouse End Unit"},
                {"value": "TwnhsI", "label": "Townhouse Inside Unit"}
            ],
            "houseStyles": [
                {"value": "1Story", "label": "One Story"},
                {"value": "1.5Fin", "label": "One and Half Story Finished"},
                {"value": "1.5Unf", "label": "One and Half Story Unfinished"},
                {"value": "2Story", "label": "Two Story"},
                {"value": "2.5Fin", "label": "Two and Half Story Finished"},
                {"value": "2.5Unf", "label": "Two and Half Story Unfinished"},
                {"value": "SFoyer", "label": "Split Foyer"},
                {"value": "SLvl", "label": "Split Level"}
            ],
            "qualityRatings": [
                {"value": 1, "label": "1 - Very Poor"},
                {"value": 2, "label": "2 - Poor"},
                {"value": 3, "label": "3 - Fair"},
                {"value": 4, "label": "4 - Below Average"},
                {"value": 5, "label": "5 - Average"},
                {"value": 6, "label": "6 - Above Average"},
                {"value": 7, "label": "7 - Good"},
                {"value": 8, "label": "8 - Very Good"},
                {"value": 9, "label": "9 - Excellent"},
                {"value": 10, "label": "10 - Very Excellent"}
            ],
            "exteriorQuality": [
                {"value": "Ex", "label": "Excellent"},
                {"value": "Gd", "label": "Good"},
                {"value": "TA", "label": "Typical/Average"},
                {"value": "Fa", "label": "Fair"},
                {"value": "Po", "label": "Poor"}
            ],
            "garageTypes": [
                {"value": "Attchd", "label": "Attached to Home"},
                {"value": "Detchd", "label": "Detached from Home"},
                {"value": "BuiltIn", "label": "Built-In"},
                {"value": "CarPort", "label": "Car Port"},
                {"value": "Basment", "label": "Basement Garage"},
                {"value": "2Types", "label": "More than One Type"},
                {"value": "NA", "label": "No Garage"}
            ],
            "foundations": [
                {"value": "PConc", "label": "Poured Concrete"},
                {"value": "CBlock", "label": "Cinder Block"},
                {"value": "BrkTil", "label": "Brick & Tile"},
                {"value": "Stone", "label": "Stone"},
                {"value": "Wood", "label": "Wood"},
                {"value": "Slab", "label": "Slab"}
            ]
        }
    })
