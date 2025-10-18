from typing import Dict, Any

from .category_classifier_agent import CategoryClassifierAgent  # type: ignore
from .attribute_extractor_agent import AttributeExtractorAgent  # type: ignore
from .tag_generator_agent import TagGeneratorAgent


class OrchestratorAgent:
    """Coordinates multiple agents to process a product payload."""

    def __init__(self):
        # Initialize the three agents responsible for different tasks
        self.classifier = CategoryClassifierAgent() # Handles product classification (e.g., Electronics, Clothing)
        self.extractor = AttributeExtractorAgent()  # Extracts product attributes (e.g., color, brand, size)
        self.tagger = TagGeneratorAgent()           # Generates relevant tags for the product

    def process(self, product: Dict[str, Any]) -> Dict[str, Any]:
        result: Dict[str, Any] = {"input": product}  # Store the original input for reference

        # Step 1: Extract attributes (like color, brand, etc.)
        attributes = self.extractor.extract_attributes(product)
        result["attributes"] = attributes

        # Step 2: Classify the product into a specific category
        classification = self.classifier.classify_product(product)
        result["classification"] = classification

        # Step 3: Generate tags using product info and extracted attributes
        tags = self.tagger.generate_tags(product, attributes.get("attributes"))
        result["tags"] = tags

        return result


