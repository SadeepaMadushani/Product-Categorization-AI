
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum

class ProductData(BaseModel):
    """Schema for product input data"""
    description: str = Field(..., description="Product description or name")

    product_id: Optional[str] = Field(None, description="Unique product identifier")

    gender: Optional[str] = Field(None, description="Target gender")

    master_category: Optional[str] = Field(None, description="Master product category")

    sub_category: Optional[str] = Field(None, description="Product subcategory")

    article_type: Optional[str] = Field(None, description="Type of article")

    base_colour: Optional[str] = Field(None, description="Base color of the product")

    season: Optional[str] = Field(None, description="Season for the product")

    year: Optional[int] = Field(None, description="Year of production")

    usage: Optional[str] = Field(None, description="Intended usage")

    product_display_name: Optional[str] = Field(None, description="Display name for the product")

    filename: Optional[str] = Field(None, description="Associated filename")
    link: Optional[str] = Field(None, description="Product link")

class ClassificationResult(BaseModel):
    """Schema for product classification results"""
    category: str = Field(..., description="Primary category")
    subcategory: str = Field(..., description="Subcategory")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reasoning: str = Field(..., description="Reasoning for classification")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v

class AttributeValue(BaseModel):
    """Schema for individual attribute values"""
    value: str = Field(..., description="Attribute value")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v

class AttributesResult(BaseModel):
    """Schema for extracted product attributes"""
    color: Optional[AttributeValue] = Field(None, description="Color attribute")

    material: Optional[AttributeValue] = Field(None, description="Material attribute")

    size: Optional[AttributeValue] = Field(None, description="Size attribute")

    pattern: Optional[AttributeValue] = Field(None, description="Pattern attribute")

    style: Optional[AttributeValue] = Field(None, description="Style attribute")

    gender: Optional[AttributeValue] = Field(None, description="Gender attribute")

    seasonality: Optional[AttributeValue] = Field(None, description="Seasonality attribute")

    occasion: Optional[AttributeValue] = Field(None, description="Occasion attribute")
    entities: Optional[List[Dict[str, Any]]] = Field(None, description="Named entities")

class Tag(BaseModel):
    """Schema for product tags"""
    tag: str = Field(..., description="Tag text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    source: Optional[str] = Field(None, description="Source of the tag (llm, nlp, rule, etc.)")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v

class TagGenerationRequest(BaseModel):
    """Schema for tag generation requests"""
    product_data: ProductData = Field(..., description="Product information")
    attributes: Optional[AttributesResult] = Field(None, description="Extracted attributes")
    max_tags: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of tags to generate")

class TagGenerationResponse(BaseModel):
    """Schema for tag generation responses"""
    tags: List[Tag] = Field(..., description="Generated tags")

    generation_timestamp: str = Field(..., description="Timestamp of generation")

    total_generated: Optional[int] = Field(None, description="Total tags generated before deduplication")

    final_count: Optional[int] = Field(None, description="Final number of unique tags")
    
    error: Optional[str] = Field(None, description="Error message if generation failed")

class ProcessingResult(BaseModel):
    """Schema for complete processing results"""
    classification: Optional[ClassificationResult] = Field(None, description="Classification results")
    attributes: Optional[AttributesResult] = Field(None, description="Attribute extraction results")
    tags: List[Tag] = Field(default_factory=list, description="Generated tags")
    similar_products: Optional[List[Dict[str, Any]]] = Field(None, description="Similar products")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Error timestamp")

class HealthCheck(BaseModel):
    """Schema for health check responses"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Check timestamp")
    model: Optional[str] = Field(None, description="Model information")
    version: Optional[str] = Field(None, description="Service version")

class ValidationError(BaseModel):
    """Schema for validation errors"""
    field: str = Field(..., description="Field that failed validation")

    message: str = Field(..., description="Validation error message")

    value: Any = Field(..., description="Value that failed validation")