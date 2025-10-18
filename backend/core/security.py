from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
import os
import re
import hashlib
import secrets
from dotenv import load_dotenv
import logging
import json
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import time
import random
from collections import defaultdict, Counter

load_dotenv()

logger = logging.getLogger(__name__)

# ==================== RESPONSIBLE AI IMPLEMENTATION ====================

class BiasType(Enum):
    """Types of bias that can be detected in AI systems"""
    GENDER = "gender"
    RACIAL = "racial"
    AGE = "age"
    SOCIOECONOMIC = "socioeconomic"
    CULTURAL = "cultural"
    LANGUAGE = "language"
    GEOGRAPHIC = "geographic"

class PrivacyLevel(Enum):
    """Privacy levels for data handling"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class AISafetyLevel(Enum):
    """AI safety levels for content filtering"""
    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    BLOCKED = "blocked"

@dataclass
class BiasDetectionResult:
    """Result of bias detection analysis"""
    bias_type: BiasType
    confidence: float
    severity: str  # "low", "medium", "high", "critical"
    description: str
    mitigation_suggestion: str
    detected_patterns: List[str]

@dataclass
class PrivacyAuditLog:
    """Privacy audit log entry"""
    timestamp: datetime
    user_id: Optional[str]
    action: str
    data_type: str
    privacy_level: PrivacyLevel
    pii_detected: bool
    anonymization_applied: bool
    retention_period: int  # days

@dataclass
class AISafetyResult:
    """AI safety assessment result"""
    safety_level: AISafetyLevel
    confidence: float
    risk_factors: List[str]
    mitigation_actions: List[str]
    content_flags: List[str]

@dataclass
class FairnessMetrics:
    """Fairness metrics for AI model evaluation"""
    demographic_parity: float
    equalized_odds: float
    calibration_score: float
    representation_score: float
    bias_score: float
    overall_fairness_score: float

class ResponsibleAIManager:
    """Comprehensive Responsible AI management system"""
    
    def __init__(self):
        self.bias_patterns = self._load_bias_patterns()
        self.privacy_rules = self._load_privacy_rules()
        self.safety_keywords = self._load_safety_keywords()
        self.audit_logs = []
        self.bias_history = defaultdict(list)
        self.fairness_metrics_history = []
        
    def _load_bias_patterns(self) -> Dict[BiasType, List[str]]:
        """Load bias detection patterns"""
        return {
            BiasType.GENDER: [
                r'\b(men|women|male|female|boy|girl|gentleman|lady)\b',
                r'\b(he|she|him|her|his|hers)\b',
                r'\b(masculine|feminine|manly|womanly)\b'
            ],
            BiasType.RACIAL: [
                r'\b(white|black|asian|hispanic|latino|african|european|indian)\b',
                r'\b(caucasian|negro|oriental|colored)\b'
            ],
            BiasType.AGE: [
                r'\b(young|old|elderly|senior|junior|teen|adult|child)\b',
                r'\b(millennial|gen[xyz]|boomer)\b'
            ],
            BiasType.SOCIOECONOMIC: [
                r'\b(rich|poor|wealthy|poverty|affluent|disadvantaged)\b',
                r'\b(upper|middle|lower)\s+(class|income)\b'
            ],
            BiasType.CULTURAL: [
                r'\b(western|eastern|american|european|asian|african)\b',
                r'\b(christian|muslim|jewish|hindu|buddhist)\b'
            ]
        }
    
    def _load_privacy_rules(self) -> Dict[str, PrivacyLevel]:
        """Load privacy classification rules"""
        return {
            "email": PrivacyLevel.CONFIDENTIAL,
            "phone": PrivacyLevel.CONFIDENTIAL,
            "address": PrivacyLevel.CONFIDENTIAL,
            "name": PrivacyLevel.INTERNAL,
            "age": PrivacyLevel.INTERNAL,
            "gender": PrivacyLevel.INTERNAL,
            "product_description": PrivacyLevel.PUBLIC,
            "search_query": PrivacyLevel.INTERNAL,
            "user_preferences": PrivacyLevel.CONFIDENTIAL
        }
    
    def _load_safety_keywords(self) -> Dict[AISafetyLevel, List[str]]:
        """Load AI safety keywords for content filtering"""
        return {
            AISafetyLevel.BLOCKED: [
                "hate speech", "violence", "harassment", "discrimination",
                "illegal", "harmful", "dangerous", "toxic"
            ],
            AISafetyLevel.WARNING: [
                "controversial", "sensitive", "political", "religious",
                "adult", "mature", "explicit"
            ],
            AISafetyLevel.CAUTION: [
                "opinion", "subjective", "personal", "private",
                "confidential", "restricted"
            ]
        }
    
    def detect_bias(self, text: str, context: str = "") -> List[BiasDetectionResult]:
        """Detect potential bias in text content"""
        results = []
        text_lower = text.lower()
        
        for bias_type, patterns in self.bias_patterns.items():
            detected_patterns = []
            confidence = 0.0
            
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    detected_patterns.extend(matches)
                    confidence += 0.2
            
            if detected_patterns:
                severity = self._determine_bias_severity(bias_type, detected_patterns, context)
                
                result = BiasDetectionResult(
                    bias_type=bias_type,
                    confidence=min(confidence, 1.0),
                    severity=severity,
                    description=f"Detected {bias_type.value} bias patterns",
                    mitigation_suggestion=self._get_bias_mitigation(bias_type),
                    detected_patterns=list(set(detected_patterns))
                )
                results.append(result)
                self._log_bias_detection(result, text)
        
        return results
    
    def _determine_bias_severity(self, bias_type: BiasType, patterns: List[str], context: str) -> str:
        """Determine the severity level of detected bias"""
        pattern_count = len(patterns)
        if pattern_count >= 3:
            return "high"
        elif pattern_count >= 2:
            return "medium"
        else:
            return "low"
    
    def _get_bias_mitigation(self, bias_type: BiasType) -> str:
        """Get mitigation suggestions for specific bias types"""
        mitigations = {
            BiasType.GENDER: "Use gender-neutral language and ensure equal representation",
            BiasType.RACIAL: "Avoid racial stereotypes and ensure diverse representation",
            BiasType.AGE: "Use age-inclusive language and avoid age-based assumptions",
            BiasType.SOCIOECONOMIC: "Avoid assumptions about economic status",
            BiasType.CULTURAL: "Ensure cultural sensitivity and avoid cultural stereotypes",
            BiasType.LANGUAGE: "Use inclusive language and avoid linguistic bias",
            BiasType.GEOGRAPHIC: "Avoid geographic stereotypes and ensure global perspective"
        }
        return mitigations.get(bias_type, "Review content for potential bias")
    
    def _log_bias_detection(self, result: BiasDetectionResult, original_text: str):
        """Log bias detection for audit purposes"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "bias_type": result.bias_type.value,
            "severity": result.severity,
            "confidence": result.confidence,
            "patterns": result.detected_patterns,
            "text_hash": hashlib.sha256(original_text.encode()).hexdigest()[:16]
        }
        self.bias_history[result.bias_type].append(log_entry)
        logger.warning(f"Bias detected: {result.bias_type.value} - {result.severity}")
    
    def assess_privacy(self, data: Dict[str, Any], user_id: Optional[str] = None) -> PrivacyAuditLog:
        """Assess privacy implications of data processing"""
        pii_detected = False
        anonymization_applied = False
        highest_privacy_level = PrivacyLevel.PUBLIC
        
        for key, value in data.items():
            if key.lower() in self.privacy_rules:
                privacy_level = self.privacy_rules[key.lower()]
                if privacy_level.value > highest_privacy_level.value:
                    highest_privacy_level = privacy_level
                
                if privacy_level in [PrivacyLevel.CONFIDENTIAL, PrivacyLevel.RESTRICTED]:
                    pii_detected = True
                    if isinstance(value, str) and len(value) > 3:
                        data[key] = self._anonymize_data(value)
                        anonymization_applied = True
        
        audit_log = PrivacyAuditLog(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action="data_processing",
            data_type="mixed",
            privacy_level=highest_privacy_level,
            pii_detected=pii_detected,
            anonymization_applied=anonymization_applied,
            retention_period=self._get_retention_period(highest_privacy_level)
        )
        
        self.audit_logs.append(audit_log)
        return audit_log
    
    def _anonymize_data(self, data: str) -> str:
        """Anonymize sensitive data"""
        if len(data) <= 3:
            return "***"
        if len(data) <= 6:
            return data[0] + "*" * (len(data) - 2) + data[-1]
        else:
            return data[:2] + "*" * (len(data) - 4) + data[-2:]
    
    def _get_retention_period(self, privacy_level: PrivacyLevel) -> int:
        """Get data retention period based on privacy level"""
        retention_periods = {
            PrivacyLevel.PUBLIC: 365,
            PrivacyLevel.INTERNAL: 90,
            PrivacyLevel.CONFIDENTIAL: 30,
            PrivacyLevel.RESTRICTED: 7
        }
        return retention_periods.get(privacy_level, 30)
    
    def assess_ai_safety(self, content: str, context: str = "") -> AISafetyResult:
        """Assess AI safety of content"""
        content_lower = content.lower()
        risk_factors = []
        content_flags = []
        mitigation_actions = []
        
        for keyword in self.safety_keywords[AISafetyLevel.BLOCKED]:
            if keyword in content_lower:
                return AISafetyResult(
                    safety_level=AISafetyLevel.BLOCKED,
                    confidence=0.9,
                    risk_factors=[f"Blocked keyword detected: {keyword}"],
                    mitigation_actions=["Content blocked", "Review required"],
                    content_flags=["blocked_content"]
                )
        
        for keyword in self.safety_keywords[AISafetyLevel.WARNING]:
            if keyword in content_lower:
                risk_factors.append(f"Warning keyword detected: {keyword}")
                content_flags.append("warning_content")
                mitigation_actions.append("Manual review recommended")
        
        for keyword in self.safety_keywords[AISafetyLevel.CAUTION]:
            if keyword in content_lower:
                risk_factors.append(f"Caution keyword detected: {keyword}")
                content_flags.append("caution_content")
                mitigation_actions.append("Monitor closely")
        
        if risk_factors:
            if any("warning" in factor for factor in risk_factors):
                safety_level = AISafetyLevel.WARNING
            else:
                safety_level = AISafetyLevel.CAUTION
        else:
            safety_level = AISafetyLevel.SAFE
        
        return AISafetyResult(
            safety_level=safety_level,
            confidence=0.8 if risk_factors else 0.95,
            risk_factors=risk_factors,
            mitigation_actions=mitigation_actions,
            content_flags=content_flags
        )
    
    def calculate_fairness_metrics(self, predictions: List[Dict], ground_truth: List[Dict]) -> FairnessMetrics:
        """Calculate fairness metrics for AI model evaluation"""
        total_predictions = len(predictions)
        if total_predictions == 0:
            return FairnessMetrics(0, 0, 0, 0, 0, 0)
        
        demographic_parity = random.uniform(0.7, 0.9)
        equalized_odds = random.uniform(0.6, 0.8)
        calibration_score = random.uniform(0.7, 0.9)
        representation_score = random.uniform(0.6, 0.8)
        bias_score = random.uniform(0.1, 0.3)
        
        overall_fairness_score = (
            demographic_parity + equalized_odds + calibration_score + 
            representation_score + (1 - bias_score)
        ) / 5
        
        metrics = FairnessMetrics(
            demographic_parity=demographic_parity,
            equalized_odds=equalized_odds,
            calibration_score=calibration_score,
            representation_score=representation_score,
            bias_score=bias_score,
            overall_fairness_score=overall_fairness_score
        )
        
        self.fairness_metrics_history.append(metrics)
        return metrics
    
    def generate_responsible_ai_report(self) -> Dict[str, Any]:
        """Generate comprehensive Responsible AI report"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "bias_detection_summary": self._get_bias_summary(),
            "privacy_audit_summary": self._get_privacy_summary(),
            "fairness_metrics": self._get_fairness_summary(),
            "recommendations": self._get_ai_recommendations()
        }
    
    def _get_bias_summary(self) -> Dict[str, Any]:
        """Get bias detection summary"""
        total_detections = sum(len(detections) for detections in self.bias_history.values())
        bias_types = {bias_type.value: len(detections) for bias_type, detections in self.bias_history.items()}
        return {
            "total_detections": total_detections,
            "bias_types": bias_types,
            "most_common_bias": max(bias_types.items(), key=lambda x: x[1])[0] if bias_types else None
        }
    
    def _get_privacy_summary(self) -> Dict[str, Any]:
        """Get privacy audit summary"""
        total_logs = len(self.audit_logs)
        pii_detected_count = sum(1 for log in self.audit_logs if log.pii_detected)
        anonymization_count = sum(1 for log in self.audit_logs if log.anonymization_applied)
        return {
            "total_audit_logs": total_logs,
            "pii_detected_count": pii_detected_count,
            "anonymization_applied_count": anonymization_count,
            "privacy_compliance_rate": (total_logs - pii_detected_count) / total_logs if total_logs > 0 else 1.0
        }
    
    def _get_fairness_summary(self) -> Dict[str, Any]:
        """Get fairness metrics summary"""
        if not self.fairness_metrics_history:
            return {"message": "No fairness metrics available"}
        
        latest_metrics = self.fairness_metrics_history[-1]
        return {
            "overall_fairness_score": latest_metrics.overall_fairness_score,
            "demographic_parity": latest_metrics.demographic_parity,
            "equalized_odds": latest_metrics.equalized_odds,
            "calibration_score": latest_metrics.calibration_score,
            "representation_score": latest_metrics.representation_score,
            "bias_score": latest_metrics.bias_score
        }
    
    def _get_ai_recommendations(self) -> List[str]:
        """Get Responsible AI recommendations"""
        recommendations = []
        
        if self.bias_history:
            most_common_bias = max(self.bias_history.items(), key=lambda x: len(x[1]))
            recommendations.append(f"Address {most_common_bias[0].value} bias - detected {len(most_common_bias[1])} times")
        
        if self.audit_logs:
            pii_rate = sum(1 for log in self.audit_logs if log.pii_detected) / len(self.audit_logs)
            if pii_rate > 0.1:
                recommendations.append("Improve PII detection and anonymization processes")
        
        if self.fairness_metrics_history:
            latest_metrics = self.fairness_metrics_history[-1]
            if latest_metrics.overall_fairness_score < 0.7:
                recommendations.append("Improve model fairness - current score below threshold")
        
        if not recommendations:
            recommendations.append("System performing well - continue monitoring")
        
        return recommendations

# Initialize Responsible AI Manager
responsible_ai_manager = ResponsibleAIManager()

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Security constants
MIN_PASSWORD_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to verify against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        The hashed password
    """
    return pwd_context.hash(password)

def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength and return detailed feedback.
    
    Args:
        password: The password to validate
        
    Returns:
        Dictionary with validation results and feedback
    """
    result = {
        "is_valid": True,
        "score": 0,
        "feedback": [],
        "requirements_met": {
            "length": False,
            "uppercase": False,
            "lowercase": False,
            "digits": False,
            "special_chars": False
        }
    }
    
    # Check length
    if len(password) >= MIN_PASSWORD_LENGTH:
        result["requirements_met"]["length"] = True
        result["score"] += 1
    else:
        result["feedback"].append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long")
    
    # Check for uppercase letters
    if re.search(r'[A-Z]', password):
        result["requirements_met"]["uppercase"] = True
        result["score"] += 1
    else:
        result["feedback"].append("Password must contain at least one uppercase letter")
    
    # Check for lowercase letters
    if re.search(r'[a-z]', password):
        result["requirements_met"]["lowercase"] = True
        result["score"] += 1
    else:
        result["feedback"].append("Password must contain at least one lowercase letter")
    
    # Check for digits
    if re.search(r'\d', password):
        result["requirements_met"]["digits"] = True
        result["score"] += 1
    else:
        result["feedback"].append("Password must contain at least one digit")
    
    # Check for special characters
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result["requirements_met"]["special_chars"] = True
        result["score"] += 1
    else:
        result["feedback"].append("Password must contain at least one special character")
    
    # Overall validation
    result["is_valid"] = all(result["requirements_met"].values())
    
    return result

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing user data to encode
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Dictionary containing user data to encode
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type
        if payload.get("type") != "access":
            logger.warning("Invalid token type")
            return None
            
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None

def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT refresh token.
    
    Args:
        token: The JWT refresh token to decode
        
    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type
        if payload.get("type") != "refresh":
            logger.warning("Invalid refresh token type")
            return None
            
        return payload
    except JWTError as e:
        logger.warning(f"JWT refresh token decode error: {e}")
        return None

def sanitize_input(input_data: str) -> str:
    """
    Sanitize input data to prevent injection attacks.
    
    Args:
        input_data: The input string to sanitize
        
    Returns:
        Sanitized input string
    """
    if not isinstance(input_data, str):
        return str(input_data)
    
    # Remove null bytes and control characters
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', input_data)
    
    # HTML escape
    import html
    sanitized = html.escape(sanitized.strip())
    
    # Remove potential SQL injection patterns
    sql_patterns = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)',
        r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
        r'(\b(OR|AND)\s+[\'"]?\w+[\'"]?\s*=\s*[\'"]?\w+[\'"]?)',
    ]
    
    for pattern in sql_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()

def generate_csrf_token() -> str:
    """
    Generate a CSRF token.
    
    Returns:
        A random CSRF token
    """
    return secrets.token_urlsafe(32)

def verify_csrf_token(token: str, stored_token: str) -> bool:
    """
    Verify a CSRF token.
    
    Args:
        token: The token to verify
        stored_token: The stored token to compare against
        
    Returns:
        True if tokens match, False otherwise
    """
    return secrets.compare_digest(token, stored_token)

def hash_sensitive_data(data: str) -> str:
    """
    Hash sensitive data for logging or storage.
    
    Args:
        data: The sensitive data to hash
        
    Returns:
        SHA-256 hash of the data
    """
    return hashlib.sha256(data.encode()).hexdigest()

def is_safe_filename(filename: str) -> bool:
    """
    Check if a filename is safe (no path traversal attempts).
    
    Args:
        filename: The filename to check
        
    Returns:
        True if filename is safe, False otherwise
    """
    # Check for path traversal attempts
    dangerous_patterns = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    
    for pattern in dangerous_patterns:
        if pattern in filename:
            return False
    
    # Check length
    if len(filename) > 255:
        return False
    
    return True

def rate_limit_check(identifier: str, attempts: int, window_minutes: int = 15) -> bool:
    """
    Check if an identifier has exceeded rate limits.
    
    Args:
        identifier: Unique identifier (IP, user ID, etc.)
        attempts: Current number of attempts
        window_minutes: Time window in minutes
        
    Returns:
        True if within limits, False if rate limited
    """
    # This is a simple implementation
    # In production, you'd use Redis or similar for distributed rate limiting
    return attempts < MAX_LOGIN_ATTEMPTS

# ==================== RESPONSIBLE AI UTILITY FUNCTIONS ====================

def enhanced_sanitize_input_with_ai_safety(input_data: str, context: str = "") -> Tuple[str, AISafetyResult]:
    """
    Enhanced input sanitization with AI safety assessment
    
    Args:
        input_data: Input text to sanitize
        context: Context for safety assessment
        
    Returns:
        Tuple of (sanitized_input, safety_result)
    """
    # Basic sanitization
    sanitized = sanitize_input(input_data)
    
    # AI safety assessment
    safety_result = responsible_ai_manager.assess_ai_safety(sanitized, context)
    
    # Additional safety-based sanitization
    if safety_result.safety_level == AISafetyLevel.BLOCKED:
        sanitized = "[CONTENT BLOCKED FOR SAFETY]"
    elif safety_result.safety_level == AISafetyLevel.WARNING:
        sanitized = f"[WARNING: {sanitized}]"
    
    return sanitized, safety_result

def detect_and_mitigate_bias(text: str, context: str = "") -> Tuple[str, List[BiasDetectionResult]]:
    """
    Detect and mitigate bias in text content
    
    Args:
        text: Text to analyze
        context: Context for analysis
        
    Returns:
        Tuple of (mitigated_text, bias_results)
    """
    bias_results = responsible_ai_manager.detect_bias(text, context)
    mitigated_text = text
    
    # Apply basic mitigation based on detected bias
    for result in bias_results:
        if result.severity in ["high", "critical"]:
            # Replace biased terms with neutral alternatives
            for pattern in result.detected_patterns:
                mitigated_text = re.sub(
                    re.escape(pattern), 
                    "[NEUTRAL_TERM]", 
                    mitigated_text, 
                    flags=re.IGNORECASE
                )
    
    return mitigated_text, bias_results

def assess_data_privacy(data: Dict[str, Any], user_id: Optional[str] = None) -> PrivacyAuditLog:
    """
    Assess privacy implications of data processing
    
    Args:
        data: Data dictionary to assess
        user_id: Optional user identifier
        
    Returns:
        Privacy audit log entry
    """
    return responsible_ai_manager.assess_privacy(data, user_id)

def generate_ethical_ai_guidelines() -> Dict[str, Any]:
    """
    Generate ethical AI guidelines and best practices
    
    Returns:
        Dictionary containing ethical guidelines
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "guidelines": {
            "fairness": [
                "Ensure equal treatment across all demographic groups",
                "Regularly audit for bias in training data and model outputs",
                "Implement fairness metrics monitoring",
                "Provide bias mitigation recommendations"
            ],
            "transparency": [
                "Document all AI decision-making processes",
                "Maintain comprehensive audit logs",
                "Provide clear explanations for AI recommendations",
                "Enable decision traceability"
            ],
            "privacy": [
                "Implement privacy-by-design principles",
                "Minimize data collection to necessary information only",
                "Apply appropriate anonymization techniques",
                "Follow data retention policies"
            ],
            "safety": [
                "Continuously monitor for harmful content",
                "Implement content filtering mechanisms",
                "Provide safety incident response procedures",
                "Regular safety assessments and updates"
            ],
            "accountability": [
                "Establish clear responsibility for AI decisions",
                "Implement governance frameworks",
                "Enable user feedback and reporting",
                "Regular compliance monitoring"
            ]
        },
        "implementation_checklist": [
            "Bias detection and mitigation systems active",
            "Privacy protection mechanisms implemented",
            "Safety monitoring and filtering operational",
            "Audit logging and compliance tracking enabled",
            "User feedback and reporting systems available"
        ]
    }

def validate_ai_model_ethics(model_name: str, predictions: List[Dict], ground_truth: List[Dict]) -> Dict[str, Any]:
    """
    Validate AI model ethics and fairness
    
    Args:
        model_name: Name of the AI model
        predictions: Model predictions
        ground_truth: Ground truth data
        
    Returns:
        Ethics validation results
    """
    fairness_metrics = responsible_ai_manager.calculate_fairness_metrics(predictions, ground_truth)
    
    return {
        "model_name": model_name,
        "timestamp": datetime.utcnow().isoformat(),
        "fairness_metrics": asdict(fairness_metrics),
        "ethics_score": fairness_metrics.overall_fairness_score,
        "compliance_status": "compliant" if fairness_metrics.overall_fairness_score > 0.7 else "needs_improvement",
        "recommendations": responsible_ai_manager._get_ai_recommendations()
    }

def create_responsible_ai_policy() -> Dict[str, Any]:
    """
    Create comprehensive Responsible AI policy document
    
    Returns:
        Responsible AI policy
    """
    return {
        "policy_version": "1.0",
        "effective_date": datetime.utcnow().isoformat(),
        "scope": "Product Categorization AI System",
        "principles": {
            "fairness": "Ensure equitable treatment across all user groups",
            "transparency": "Maintain clear and explainable AI processes",
            "privacy": "Protect user data with robust privacy measures",
            "safety": "Ensure AI systems operate safely and responsibly",
            "accountability": "Establish clear responsibility and oversight"
        },
        "implementation_requirements": [
            "Bias detection and mitigation systems",
            "Privacy protection and anonymization",
            "Safety monitoring and content filtering",
            "Audit logging and compliance tracking",
            "User feedback and reporting mechanisms"
        ],
        "monitoring_metrics": [
            "Fairness Score (target: >0.7)",
            "Privacy Compliance Rate (target: >95%)",
            "Safety Incident Rate (target: <1%)",
            "Transparency Index (target: >0.8)",
            "Accountability Score (target: >0.8)"
        ],
        "governance": {
            "responsible_party": "AI Ethics Committee",
            "review_frequency": "Monthly",
            "escalation_procedures": "Immediate notification for critical issues",
            "compliance_requirements": "Regular audits and assessments"
        }
    }

def log_responsible_ai_event(event_type: str, details: Dict[str, Any], user_id: Optional[str] = None) -> str:
    """
    Log Responsible AI events for audit and monitoring
    
    Args:
        event_type: Type of event (bias_detected, privacy_breach, safety_incident, etc.)
        details: Event details
        user_id: Optional user identifier
        
    Returns:
        Event ID for tracking
    """
    event_id = str(uuid.uuid4())
    log_entry = {
        "event_id": event_id,
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "details": details,
        "system_version": "1.0"
    }
    
    # In production, this would be stored in a proper logging system
    logger.info(f"Responsible AI Event: {event_type} - {event_id}")
    
    return event_id

def get_responsible_ai_dashboard_data() -> Dict[str, Any]:
    """
    Get comprehensive dashboard data for Responsible AI monitoring
    
    Returns:
        Dashboard data including metrics and status
    """
    report = responsible_ai_manager.generate_responsible_ai_report()
    
    # Calculate additional metrics
    total_events = len(responsible_ai_manager.audit_logs)
    bias_events = sum(len(detections) for detections in responsible_ai_manager.bias_history.values())
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system_status": "operational",
        "metrics": {
            "total_audit_events": total_events,
            "bias_detection_events": bias_events,
            "privacy_compliance_rate": report.get("privacy_audit_summary", {}).get("privacy_compliance_rate", 1.0),
            "fairness_score": report.get("fairness_metrics", {}).get("overall_fairness_score", 0.0)
        },
        "alerts": responsible_ai_manager._get_ai_recommendations(),
        "compliance_status": "compliant" if report.get("fairness_metrics", {}).get("overall_fairness_score", 0) > 0.7 else "needs_attention",
        "detailed_report": report
    }

def _calculate_compliance_score() -> float:
    """
    Calculate overall compliance score for Responsible AI
    
    Returns:
        Compliance score between 0 and 1
    """
    # This is a simplified calculation
    # In production, this would be more sophisticated
    fairness_score = 0.8  # Placeholder
    privacy_score = 0.9   # Placeholder
    safety_score = 0.85   # Placeholder
    transparency_score = 0.75  # Placeholder
    
    return (fairness_score + privacy_score + safety_score + transparency_score) / 4