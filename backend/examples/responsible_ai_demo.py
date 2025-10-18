#!/usr/bin/env python3
"""
Responsible AI Demo Script

This script demonstrates the comprehensive Responsible AI features
implemented in the security.py module.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.security import (
    responsible_ai_manager,
    enhanced_sanitize_input_with_ai_safety,
    detect_and_mitigate_bias,
    assess_data_privacy,
    generate_ethical_ai_guidelines,
    validate_ai_model_ethics,
    create_responsible_ai_policy,
    log_responsible_ai_event,
    get_responsible_ai_dashboard_data,
    BiasType,
    PrivacyLevel,
    AISafetyLevel
)
import json
from datetime import datetime

def demo_bias_detection():
    """Demonstrate bias detection capabilities"""
    print("🔍 BIAS DETECTION DEMO")
    print("=" * 50)
    
    test_texts = [
        "This product is perfect for women who want to look feminine",
        "Men prefer blue colors while women prefer pink",
        "Young people will love this trendy design",
        "This is suitable for all ages and genders",
        "Only wealthy customers can afford this luxury item"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Testing: '{text}'")
        bias_results = responsible_ai_manager.detect_bias(text)
        
        if bias_results:
            for result in bias_results:
                print(f"   ⚠️  Bias detected: {result.bias_type.value}")
                print(f"   📊 Severity: {result.severity}")
                print(f"   🎯 Confidence: {result.confidence:.2f}")
                print(f"   💡 Mitigation: {result.mitigation_suggestion}")
                print(f"   🔍 Patterns: {result.detected_patterns}")
        else:
            print("   ✅ No bias detected")

def demo_privacy_protection():
    """Demonstrate privacy protection capabilities"""
    print("\n\n🔒 PRIVACY PROTECTION DEMO")
    print("=" * 50)
    
    test_data = [
        {
            "user_email": "john.doe@example.com",
            "phone_number": "+1234567890",
            "product_description": "Blue cotton shirt",
            "user_preferences": "casual wear"
        },
        {
            "name": "Jane Smith",
            "age": "25",
            "search_query": "red dress",
            "address": "123 Main St, City"
        }
    ]
    
    for i, data in enumerate(test_data, 1):
        print(f"\n{i}. Processing data: {list(data.keys())}")
        processed_data, privacy_log = assess_data_privacy(data, f"user_{i}")
        
        print(f"   📊 Privacy Level: {privacy_log.privacy_level.value}")
        print(f"   🔍 PII Detected: {privacy_log.pii_detected}")
        print(f"   🛡️  Anonymization Applied: {privacy_log.anonymization_applied}")
        print(f"   ⏰ Retention Period: {privacy_log.retention_period} days")
        print(f"   📝 Processed Data: {processed_data}")

def demo_ai_safety():
    """Demonstrate AI safety assessment"""
    print("\n\n🛡️ AI SAFETY DEMO")
    print("=" * 50)
    
    test_contents = [
        "I need a comfortable blue shirt for work",
        "This product contains controversial political content",
        "This is a safe and reliable product for everyone",
        "This content may be harmful to children",
        "Great product with excellent quality"
    ]
    
    for i, content in enumerate(test_contents, 1):
        print(f"\n{i}. Testing: '{content}'")
        safety_result = responsible_ai_manager.assess_ai_safety(content)
        
        print(f"   🚦 Safety Level: {safety_result.safety_level.value}")
        print(f"   📊 Confidence: {safety_result.confidence:.2f}")
        
        if safety_result.risk_factors:
            print(f"   ⚠️  Risk Factors: {safety_result.risk_factors}")
        
        if safety_result.mitigation_actions:
            print(f"   💡 Mitigation Actions: {safety_result.mitigation_actions}")
        
        if safety_result.content_flags:
            print(f"   🏷️  Content Flags: {safety_result.content_flags}")

def demo_fairness_metrics():
    """Demonstrate fairness metrics calculation"""
    print("\n\n⚖️ FAIRNESS METRICS DEMO")
    print("=" * 50)
    
    # Simulate some predictions and ground truth
    predictions = [
        {"prediction": "shirt", "confidence": 0.9, "demographic": "male"},
        {"prediction": "dress", "confidence": 0.8, "demographic": "female"},
        {"prediction": "jeans", "confidence": 0.7, "demographic": "male"},
        {"prediction": "blouse", "confidence": 0.85, "demographic": "female"}
    ]
    
    ground_truth = [
        {"label": "shirt", "demographic": "male"},
        {"label": "dress", "demographic": "female"},
        {"label": "jeans", "demographic": "male"},
        {"label": "blouse", "demographic": "female"}
    ]
    
    fairness_metrics = responsible_ai_manager.calculate_fairness_metrics(predictions, ground_truth)
    
    print(f"📊 Overall Fairness Score: {fairness_metrics.overall_fairness_score:.3f}")
    print(f"👥 Demographic Parity: {fairness_metrics.demographic_parity:.3f}")
    print(f"⚖️  Equalized Odds: {fairness_metrics.equalized_odds:.3f}")
    print(f"🎯 Calibration Score: {fairness_metrics.calibration_score:.3f}")
    print(f"📈 Representation Score: {fairness_metrics.representation_score:.3f}")
    print(f"⚠️  Bias Score: {fairness_metrics.bias_score:.3f}")

def demo_enhanced_sanitization():
    """Demonstrate enhanced input sanitization with AI safety"""
    print("\n\n🧹 ENHANCED SANITIZATION DEMO")
    print("=" * 50)
    
    test_inputs = [
        "I need a blue shirt for work",
        "This product is <script>alert('xss')</script> dangerous",
        "SELECT * FROM users WHERE id = 1",
        "This content contains harmful material"
    ]
    
    for i, input_data in enumerate(test_inputs, 1):
        print(f"\n{i}. Input: '{input_data}'")
        sanitized, safety_result = enhanced_sanitize_input_with_ai_safety(input_data)
        
        print(f"   🧹 Sanitized: '{sanitized}'")
        print(f"   🚦 Safety Level: {safety_result.safety_level.value}")
        
        if safety_result.safety_level == AISafetyLevel.BLOCKED:
            print("   🚫 Content blocked due to safety concerns")

def demo_responsible_ai_report():
    """Demonstrate comprehensive Responsible AI reporting"""
    print("\n\n📊 RESPONSIBLE AI REPORT DEMO")
    print("=" * 50)
    
    # Generate comprehensive report
    report = responsible_ai_manager.generate_responsible_ai_report()
    
    print("📋 Responsible AI Report:")
    print(json.dumps(report, indent=2, default=str))

def demo_ethical_guidelines():
    """Demonstrate ethical AI guidelines"""
    print("\n\n📜 ETHICAL AI GUIDELINES DEMO")
    print("=" * 50)
    
    guidelines = generate_ethical_ai_guidelines()
    
    print("🎯 Ethical AI Principles:")
    for principle, description in guidelines["principles"].items():
        print(f"   • {principle.title()}: {description}")
    
    print("\n🛠️ Implementation Guidelines:")
    for area, description in guidelines["implementation"].items():
        print(f"   • {area.replace('_', ' ').title()}: {description}")

def demo_responsible_ai_policy():
    """Demonstrate Responsible AI policy creation"""
    print("\n\n📋 RESPONSIBLE AI POLICY DEMO")
    print("=" * 50)
    
    policy = create_responsible_ai_policy()
    
    print(f"📄 Policy Version: {policy['policy_version']}")
    print(f"📅 Effective Date: {policy['effective_date']}")
    print(f"🎯 Scope: {policy['scope']}")
    
    print("\n🏛️ Governance Roles:")
    for role, description in policy["governance"]["roles"].items():
        print(f"   • {role.replace('_', ' ').title()}: {description}")

def demo_dashboard_data():
    """Demonstrate Responsible AI dashboard data"""
    print("\n\n📊 DASHBOARD DATA DEMO")
    print("=" * 50)
    
    dashboard_data = get_responsible_ai_dashboard_data()
    
    print("📈 System Status:")
    for status, active in dashboard_data["system_status"].items():
        status_icon = "✅" if active else "❌"
        print(f"   {status_icon} {status.replace('_', ' ').title()}")
    
    print(f"\n📊 Compliance Score: {dashboard_data['compliance_score']:.2f}")
    print(f"📅 Next Review Date: {dashboard_data['next_review_date']}")

def demo_event_logging():
    """Demonstrate Responsible AI event logging"""
    print("\n\n📝 EVENT LOGGING DEMO")
    print("=" * 50)
    
    # Log some sample events
    log_responsible_ai_event(
        "bias_detected",
        {"bias_type": "gender", "severity": "medium", "text_hash": "abc123"},
        "user_123"
    )
    
    log_responsible_ai_event(
        "privacy_breach_prevented",
        {"data_type": "email", "action": "anonymized"},
        "user_456"
    )
    
    log_responsible_ai_event(
        "safety_incident",
        {"content_level": "warning", "action_taken": "flagged_for_review"},
        "user_789"
    )
    
    print("✅ Logged sample Responsible AI events")
    print(f"📊 Total audit logs: {len(responsible_ai_manager.audit_logs)}")

def main():
    """Run all Responsible AI demonstrations"""
    print("🤖 RESPONSIBLE AI COMPREHENSIVE DEMO")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        demo_bias_detection()
        demo_privacy_protection()
        demo_ai_safety()
        demo_fairness_metrics()
        demo_enhanced_sanitization()
        demo_responsible_ai_report()
        demo_ethical_guidelines()
        demo_responsible_ai_policy()
        demo_dashboard_data()
        demo_event_logging()
        
        print("\n\n✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("🎯 Key Features Demonstrated:")
        print("   • Bias Detection & Mitigation")
        print("   • Privacy Protection & Anonymization")
        print("   • AI Safety Assessment")
        print("   • Fairness Metrics Calculation")
        print("   • Enhanced Input Sanitization")
        print("   • Comprehensive Reporting")
        print("   • Ethical Guidelines & Policies")
        print("   • Event Logging & Monitoring")
        print("   • Dashboard Data Generation")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
