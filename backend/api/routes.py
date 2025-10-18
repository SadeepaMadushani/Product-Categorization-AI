from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..agents.category_classifier_agent import CategoryClassifierAgent  # type: ignore
from ..agents.attribute_extractor_agent import AttributeExtractorAgent  # type: ignore
from ..agents.tag_generator_agent import TagGeneratorAgent
from ..agents.orchestrator_agent import OrchestratorAgent
from ..core.security import sanitize_input
from ..core.mongodb_service import mongodb_service


router = APIRouter(prefix="/api", tags=["agents"])


class ProductIn(BaseModel):
    description: str


class ProductData(BaseModel):
    productDisplayName: str
    description: str
    gender: Optional[str] = None
    masterCategory: Optional[str] = None
    subCategory: Optional[str] = None
    articleType: Optional[str] = None
    baseColour: Optional[str] = None
    season: Optional[str] = None
    year: Optional[int] = None
    usage: Optional[str] = None
    link: Optional[str] = None
    filename: Optional[str] = None


@router.post("/classifier/process")
def classifier_process(product: ProductIn) -> Dict[str, Any]:
    agent = CategoryClassifierAgent()
    payload = {"productDisplayName": sanitize_input(product.description), "description": product.description}
    return agent.classify_product(payload)


@router.post("/extractor/process")
def extractor_process(product: ProductIn) -> Dict[str, Any]:
    agent = AttributeExtractorAgent()
    payload = {"productDisplayName": sanitize_input(product.description), "description": product.description}
    return agent.extract_attributes(payload)


@router.post("/tagger/process")
def tagger_process(product: ProductIn) -> Dict[str, Any]:
    agent = TagGeneratorAgent()
    payload = {"productDisplayName": sanitize_input(product.description), "description": product.description}
    return agent.generate_tags(payload)


@router.post("/orchestrator/process")
def orchestrator_process(product: ProductIn) -> Dict[str, Any]:
    agent = OrchestratorAgent()
    payload = {"productDisplayName": sanitize_input(product.description), "description": product.description}
    return agent.process(payload)


# ==================== PRODUCT MANAGEMENT ENDPOINTS ====================

@router.post("/products/add")
def add_product(product: ProductData) -> Dict[str, Any]:
    """Add a new product to MongoDB with AI categorization"""
    try:
        # Convert Pydantic model to dict
        product_dict = product.dict()
        
        # Add product to MongoDB
        result = mongodb_service.add_product(product_dict)
        
        if result["success"]:
            return {
                "success": True,
                "message": "Product added successfully",
                "product_id": result["product_id"],
                "product": result["product"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add product: {str(e)}")


@router.get("/products")
def get_products(limit: int = 100, skip: int = 0) -> Dict[str, Any]:
    """Get all products from MongoDB"""
    try:
        products = mongodb_service.get_products(limit=limit, skip=skip)
        total_count = mongodb_service.get_products_count()
        
        return {
            "success": True,
            "products": products,
            "total_count": total_count,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get products: {str(e)}")


@router.get("/products/{product_id}")
def get_product(product_id: str) -> Dict[str, Any]:
    """Get a specific product by ID"""
    try:
        product = mongodb_service.get_product_by_id(product_id)
        
        if product:
            return {
                "success": True,
                "product": product
            }
        else:
            raise HTTPException(status_code=404, detail="Product not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get product: {str(e)}")


@router.get("/products/search")
def search_products(
    category: Optional[str] = None,
    gender: Optional[str] = None,
    color: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """Search products based on criteria"""
    try:
        query = {}
        
        if category:
            query["masterCategory"] = category
        if gender:
            query["gender"] = gender
        if color:
            query["baseColour"] = color
        
        products = mongodb_service.search_products(query, limit=limit)
        
        return {
            "success": True,
            "products": products,
            "query": query,
            "count": len(products)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search products: {str(e)}")


@router.put("/products/{product_id}")
def update_product(product_id: str, product: ProductData) -> Dict[str, Any]:
    """Update a product in MongoDB"""
    try:
        # Convert Pydantic model to dict
        product_dict = product.dict()
        
        success = mongodb_service.update_product(product_id, product_dict)
        
        if success:
            return {
                "success": True,
                "message": "Product updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Product not found or update failed")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update product: {str(e)}")


@router.delete("/products/{product_id}")
def delete_product(product_id: str) -> Dict[str, Any]:
    """Delete a product from MongoDB"""
    try:
        success = mongodb_service.delete_product(product_id)
        
        if success:
            return {
                "success": True,
                "message": "Product deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Product not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete product: {str(e)}")


