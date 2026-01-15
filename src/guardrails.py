"""
Guardrails for Real-Time Multi-Source Knowledge Assistant
High-level safety and ethical guidelines similar to ChatGPT restrictions
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class ContentGuardrails:
    """
    High-level guardrails system for content safety and ethical AI usage.
    Similar to ChatGPT's safety instructions but adapted for RAG applications.
    """

    def __init__(self):
        # Content categories that should be restricted
        self.RESTRICTED_CATEGORIES = {
            'harmful_activities': [
                'violent crimes', 'terrorism', 'hacking', 'illegal activities',
                'creating weapons', 'harm to others', 'self-harm', 'suicide'
            ],
            'sensitive_topics': [
                'explicit sexual content', 'child exploitation', 'hate speech',
                'discrimination', 'harassment', 'bullying'
            ],
            'illegal_substances': [
                'drug manufacturing', 'illegal drugs', 'controlled substances'
            ],
            'privacy_violation': [
                'personal information', 'doxxing', 'identity theft', 'surveillance'
            ],
            'misinformation': [
                'false medical advice', 'conspiracy theories', 'disinformation'
            ]
        }

        # Keywords that trigger guardrail checks
        self.TRIGGER_KEYWORDS = {
            'violence': ['kill', 'murder', 'attack', 'bomb', 'weapon', 'gun', 'shoot', 'stab'],
            'hacking': ['hack', 'exploit', 'breach', 'phishing', 'malware', 'virus', 'trojan'],
            'drugs': ['meth', 'heroin', 'cocaine', 'fentanyl', 'synthesize', 'manufacture'],
            'self_harm': ['suicide', 'self-harm', 'overdose', 'cutting', 'starvation'],
            'illegal': ['forgery', 'counterfeit', 'smuggle', 'traffick', 'launder'],
            'explicit': ['porn', 'sex', 'nude', 'erotic', 'fetish', 'adult content'],
            'hate': ['racist', 'sexist', 'homophobic', 'transphobic', 'bigot']
        }

        # Allowable educational/safe contexts
        self.SAFE_CONTEXTS = [
            'historical', 'educational', 'academic', 'research', 'fiction', 'literature',
            'medical study', 'psychological research', 'legal analysis', 'news reporting'
        ]

    def check_query_safety(self, query: str) -> Tuple[bool, str, Dict]:
        """
        Check if a user query violates safety guidelines.

        Args:
            query: The user's query string

        Returns:
            Tuple of (is_safe: bool, reason: str, metadata: dict)
        """
        query_lower = query.lower().strip()

        # Check for direct violations
        violation_result = self._check_direct_violations(query_lower)
        if not violation_result['safe']:
            return False, violation_result['reason'], violation_result

        # Check for contextual violations
        context_result = self._check_contextual_violations(query_lower)
        if not context_result['safe']:
            return False, context_result['reason'], context_result

        # Check for sensitive topics
        sensitive_result = self._check_sensitive_topics(query_lower)
        if not sensitive_result['safe']:
            return False, sensitive_result['reason'], sensitive_result

        return True, "Query appears safe", {
            'safe': True,
            'reason': 'Query appears safe',
            'categories_checked': ['direct_violations', 'contextual_violations', 'sensitive_topics'],
            'timestamp': datetime.now().isoformat()
        }

    def check_response_safety(self, response: str, original_query: str = "") -> Tuple[bool, str, Dict]:
        """
        Check if an AI response violates safety guidelines.

        Args:
            response: The AI-generated response
            original_query: The original user query for context

        Returns:
            Tuple of (is_safe: bool, reason: str, metadata: dict)
        """
        response_lower = response.lower().strip()

        # Check for harmful content in response
        harmful_result = self._check_response_harmful_content(response_lower)
        if not harmful_result['safe']:
            return False, harmful_result['reason'], harmful_result

        # Check for misinformation
        misinfo_result = self._check_misinformation(response_lower, original_query)
        if not misinfo_result['safe']:
            return False, misinfo_result['reason'], misinfo_result

        return True, "Response appears safe", {
            'safe': True,
            'reason': 'Response appears safe',
            'categories_checked': ['harmful_content', 'misinformation'],
            'timestamp': datetime.now().isoformat()
        }

    def _check_direct_violations(self, query: str) -> Dict:
        """Check for direct violations of safety guidelines."""
        for category, keywords in self.TRIGGER_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query:
                    # Check if it's in a safe educational context
                    if not self._is_safe_context(query):
                        return {
                            'safe': False,
                            'reason': f"Query contains potentially harmful content related to {category.replace('_', ' ')}",
                            'category': category,
                            'trigger_word': keyword,
                            'violation_type': 'direct'
                        }

        return {'safe': True, 'reason': 'No direct violations detected'}

    def _check_contextual_violations(self, query: str) -> Dict:
        """Check for contextual violations that require deeper analysis."""
        # Check for attempts to bypass restrictions
        bypass_patterns = [
            r'how to.*without getting caught',
            r'ways to.*illegally',
            r'secret methods?.*',
            r'hidden techniques?.*',
            r'bypass.*restrictions?',
            r'circumvent.*laws?'
        ]

        for pattern in bypass_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return {
                    'safe': False,
                    'reason': 'Query appears to attempt bypassing safety restrictions or legal boundaries',
                    'violation_type': 'bypass_attempt'
                }

        # Check for role-playing harmful scenarios
        harmful_roleplay = [
            r'pretend.*(?:kill|murder|attack)',
            r'role.*play.*(?:criminal|terrorist|hacker)',
            r'act like.*(?:drug dealer|criminal)'
        ]

        for pattern in harmful_roleplay:
            if re.search(pattern, query, re.IGNORECASE):
                return {
                    'safe': False,
                    'reason': 'Query involves role-playing harmful or illegal activities',
                    'violation_type': 'harmful_roleplay'
                }

        return {'safe': True, 'reason': 'No contextual violations detected'}

    def _check_sensitive_topics(self, query: str) -> Dict:
        """Check for sensitive topics that require careful handling."""
        sensitive_indicators = [
            r'child.*(?:abuse|exploitation|porn)',
            r'minor.*(?:sexual|explicit)',
            r'underage.*(?:content|material)',
            r'genocide|holocaust.*deny',
            r'conspiracy.*government.*control'
        ]

        for pattern in sensitive_indicators:
            if re.search(pattern, query, re.IGNORECASE):
                return {
                    'safe': False,
                    'reason': 'Query involves highly sensitive topics that require special handling',
                    'violation_type': 'sensitive_topic'
                }

        return {'safe': True, 'reason': 'No sensitive topics detected'}

    def _check_response_harmful_content(self, response: str) -> Dict:
        """Check AI response for harmful content."""
        # Check for providing actionable harmful advice
        harmful_advice_patterns = [
            r'here.*s.*how to.*(?:kill|murder|attack|hack)',
            r'step.*by.*step.*(?:bomb|weapon|drug)',
            r'follow these steps.*(?:illegal|criminal)'
        ]

        for pattern in harmful_advice_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return {
                    'safe': False,
                    'reason': 'Response contains actionable harmful instructions',
                    'violation_type': 'harmful_instructions'
                }

        return {'safe': True, 'reason': 'No harmful content in response'}

    def _check_misinformation(self, response: str, original_query: str = "") -> Dict:
        """Check for potential misinformation in responses."""
        # Medical misinformation check
        if any(word in original_query.lower() for word in ['medical', 'health', 'disease', 'treatment', 'cure']):
            medical_disclaimers = ['consult a doctor', 'professional medical advice', 'not a substitute']
            if not any(disclaimer in response.lower() for disclaimer in medical_disclaimers):
                return {
                    'safe': False,
                    'reason': 'Medical query response lacks proper disclaimers',
                    'violation_type': 'missing_medical_disclaimer'
                }

        return {'safe': True, 'reason': 'No misinformation concerns detected'}

    def _is_safe_context(self, query: str) -> bool:
        """Determine if query is in a safe educational/research context."""
        return any(context in query.lower() for context in self.SAFE_CONTEXTS)

    def get_safety_guidelines(self) -> Dict:
        """
        Return the complete safety guidelines and restrictions.

        Returns:
            Dictionary containing all safety guidelines
        """
        return {
            'restricted_categories': self.RESTRICTED_CATEGORIES,
            'trigger_keywords': self.TRIGGER_KEYWORDS,
            'safe_contexts': self.SAFE_CONTEXTS,
            'guidelines': [
                'Do not assist with queries that clearly intend to engage in violent crimes or terrorist acts',
                'Do not provide instructions for illegal activities, hacking, or creating weapons',
                'Do not generate explicit sexual content or assist with child exploitation',
                'Do not promote hate speech, discrimination, or harassment',
                'Do not provide medical advice without proper disclaimers',
                'Do not spread misinformation or conspiracy theories',
                'Allow educational and research discussions in safe contexts',
                'Provide high-level answers without actionable details for sensitive topics'
            ],
            'version': '1.0',
            'last_updated': datetime.now().isoformat()
        }

# Global guardrails instance
guardrails = ContentGuardrails()

def check_query(query: str) -> Tuple[bool, str, Dict]:
    """
    Convenience function to check query safety.

    Args:
        query: User query string

    Returns:
        Tuple of (is_safe, reason, metadata)
    """
    return guardrails.check_query_safety(query)

def check_response(response: str, original_query: str = "") -> Tuple[bool, str, Dict]:
    """
    Convenience function to check response safety.

    Args:
        response: AI response string
        original_query: Original user query for context

    Returns:
        Tuple of (is_safe, reason, metadata)
    """
    return guardrails.check_response_safety(response, original_query)

def get_safety_guidelines() -> Dict:
    """
    Get the complete safety guidelines.

    Returns:
        Dictionary of safety guidelines
    """
    return guardrails.get_safety_guidelines()