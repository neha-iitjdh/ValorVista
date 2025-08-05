"""
Input Validation Module for ValorVista API.
Uses Pydantic for robust input validation.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class MSZoning(str, Enum):
    """Zoning classification."""
    A = "A"
    C = "C"
    FV = "FV"
    I = "I"
    RH = "RH"
    RL = "RL"
    RP = "RP"
    RM = "RM"


class PropertyInput(BaseModel):
    """Validation schema for property input data."""

    # Required fields
    GrLivArea: int = Field(..., ge=100, le=15000, description="Above ground living area (sq ft)")
    OverallQual: int = Field(..., ge=1, le=10, description="Overall material and finish quality")
    OverallCond: int = Field(..., ge=1, le=10, description="Overall condition rating")
    YearBuilt: int = Field(..., ge=1800, le=2025, description="Year house was built")

    # Optional fields with defaults
    LotArea: Optional[int] = Field(None, ge=500, le=500000, description="Lot size (sq ft)")
    LotFrontage: Optional[float] = Field(None, ge=0, le=500, description="Lot frontage (feet)")

    TotalBsmtSF: Optional[int] = Field(0, ge=0, le=10000, description="Basement area (sq ft)")
    BsmtFinSF1: Optional[int] = Field(0, ge=0, le=10000, description="Type 1 finished basement (sq ft)")
    BsmtFinSF2: Optional[int] = Field(0, ge=0, le=10000, description="Type 2 finished basement (sq ft)")
    BsmtUnfSF: Optional[int] = Field(0, ge=0, le=10000, description="Unfinished basement (sq ft)")

    FirstFlrSF: Optional[int] = Field(None, ge=100, le=10000, description="First floor (sq ft)", alias="1stFlrSF")
    SecondFlrSF: Optional[int] = Field(0, ge=0, le=10000, description="Second floor (sq ft)", alias="2ndFlrSF")

    FullBath: Optional[int] = Field(1, ge=0, le=10, description="Full bathrooms above grade")
    HalfBath: Optional[int] = Field(0, ge=0, le=10, description="Half bathrooms above grade")
    BsmtFullBath: Optional[int] = Field(0, ge=0, le=5, description="Basement full bathrooms")
    BsmtHalfBath: Optional[int] = Field(0, ge=0, le=5, description="Basement half bathrooms")

    BedroomAbvGr: Optional[int] = Field(3, ge=0, le=20, description="Bedrooms above grade")
    KitchenAbvGr: Optional[int] = Field(1, ge=0, le=5, description="Kitchens above grade")
    TotRmsAbvGrd: Optional[int] = Field(6, ge=1, le=20, description="Total rooms above grade")

    Fireplaces: Optional[int] = Field(0, ge=0, le=10, description="Number of fireplaces")

    GarageCars: Optional[int] = Field(2, ge=0, le=10, description="Garage capacity (cars)")
    GarageArea: Optional[int] = Field(None, ge=0, le=5000, description="Garage area (sq ft)")
    GarageYrBlt: Optional[int] = Field(None, ge=1800, le=2025, description="Year garage was built")

    YearRemodAdd: Optional[int] = Field(None, ge=1800, le=2025, description="Year of remodel")

    WoodDeckSF: Optional[int] = Field(0, ge=0, le=2000, description="Wood deck area (sq ft)")
    OpenPorchSF: Optional[int] = Field(0, ge=0, le=1000, description="Open porch area (sq ft)")
    EnclosedPorch: Optional[int] = Field(0, ge=0, le=1000, description="Enclosed porch area (sq ft)")
    ScreenPorch: Optional[int] = Field(0, ge=0, le=1000, description="Screen porch area (sq ft)")
    ThreeSsnPorch: Optional[int] = Field(0, ge=0, le=1000, description="3-season porch area", alias="3SsnPorch")

    PoolArea: Optional[int] = Field(0, ge=0, le=1000, description="Pool area (sq ft)")
    MiscVal: Optional[int] = Field(0, ge=0, le=100000, description="Value of misc features")

    MoSold: Optional[int] = Field(6, ge=1, le=12, description="Month sold")
    YrSold: Optional[int] = Field(2024, ge=2000, le=2025, description="Year sold")

    # Categorical fields
    MSSubClass: Optional[int] = Field(20, description="Building class")
    MSZoning: Optional[str] = Field("RL", description="Zoning classification")
    Neighborhood: Optional[str] = Field("NAmes", description="Neighborhood")
    BldgType: Optional[str] = Field("1Fam", description="Building type")
    HouseStyle: Optional[str] = Field("1Story", description="House style")
    ExterQual: Optional[str] = Field("TA", description="Exterior quality")
    ExterCond: Optional[str] = Field("TA", description="Exterior condition")
    Foundation: Optional[str] = Field("PConc", description="Foundation type")
    BsmtQual: Optional[str] = Field("TA", description="Basement quality")
    BsmtCond: Optional[str] = Field("TA", description="Basement condition")
    BsmtExposure: Optional[str] = Field("No", description="Basement exposure")
    BsmtFinType1: Optional[str] = Field("Unf", description="Basement finish type 1")
    HeatingQC: Optional[str] = Field("TA", description="Heating quality")
    CentralAir: Optional[str] = Field("Y", description="Central air conditioning")
    KitchenQual: Optional[str] = Field("TA", description="Kitchen quality")
    GarageType: Optional[str] = Field("Attchd", description="Garage type")
    GarageFinish: Optional[str] = Field("Unf", description="Garage finish")
    GarageQual: Optional[str] = Field("TA", description="Garage quality")
    GarageCond: Optional[str] = Field("TA", description="Garage condition")
    PavedDrive: Optional[str] = Field("Y", description="Paved driveway")
    SaleType: Optional[str] = Field("WD", description="Sale type")
    SaleCondition: Optional[str] = Field("Normal", description="Sale condition")

    class Config:
        populate_by_name = True

    @field_validator("YearRemodAdd", mode="before")
    @classmethod
    def set_remod_year(cls, v, info):
        """Set remodel year to build year if not provided."""
        if v is None and "YearBuilt" in info.data:
            return info.data["YearBuilt"]
        return v

    @field_validator("GarageYrBlt", mode="before")
    @classmethod
    def set_garage_year(cls, v, info):
        """Set garage year to build year if not provided."""
        if v is None and "YearBuilt" in info.data:
            return info.data["YearBuilt"]
        return v

    def to_model_input(self) -> dict:
        """Convert to dictionary format expected by model."""
        data = self.model_dump(by_alias=True)
        # Handle None values
        for key, value in data.items():
            if value is None:
                data[key] = 0
        return data


class BatchInput(BaseModel):
    """Validation schema for batch prediction input."""
    properties: List[PropertyInput] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of properties to evaluate"
    )


class PredictionResponse(BaseModel):
    """Response schema for predictions."""
    success: bool
    prediction: float
    formatted_prediction: str
    confidence_interval: dict
    input_summary: dict


class BatchPredictionResponse(BaseModel):
    """Response schema for batch predictions."""
    success: bool
    total_properties: int
    predictions: List[dict]
    summary_statistics: dict
