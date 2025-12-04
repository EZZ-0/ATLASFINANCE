# 🤖 FINANCIAL AI ADVISOR - HYBRID ARCHITECTURE
# Gemini (Free, High Quality) + Ollama (Offline Fallback)
# Created: November 30, 2025

"""
FINANCIAL AI ADVISOR
====================
Professional CFA-level financial analysis using hybrid AI:
- Primary: Google Gemini 2.0 Flash (free, 9/10 quality)
- Fallback: Ollama Llama 3.1 (offline, 7/10 quality)
- Future: GPT-4 placeholder (premium upgrade path)

Features:
- Chat interface (sidebar)
- Inline metric explanations
- Investment recommendations
- Company comparisons
- Report generation
- Response validation (math, logic, hallucination detection)
"""

import os
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Import centralized logging
from utils.logging_config import EngineLogger

# Initialize logger for this module
_logger = EngineLogger.get_logger("FinancialAI")

# Load environment variables
load_dotenv()

class FinancialAI:
    """
    Hybrid AI Financial Advisor with quality validation
    """
    
    def __init__(self, tier='free'):
        """
        Initialize AI with specified tier
        
        Args:
            tier: 'free' or 'premium'
        """
        self.tier = tier
        self.session_disclaimer_shown = False
        self.conversation_history = []
        
        # Analytics
        self.analytics_enabled = os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true'
        self.analytics_data = []
        
        # Rate limiting
        self.gemini_daily_limit = int(os.getenv('GEMINI_DAILY_LIMIT', 1500))
        self.gemini_requests_today = 0
        self.last_reset_date = datetime.now().date()
        
        # Initialize models
        self._setup_models()
    
    def _setup_models(self):
        """Setup AI models based on tier"""
        
        if self.tier == 'premium':
            # Future: Premium models
            self.primary_model = self._init_gpt4()
        else:
            # Current: Free tier
            self.primary_model = self._init_gemini()
            self.fallback_model = self._init_ollama()
    
    def _init_gemini(self):
        """Initialize Google Gemini"""
        try:
            import google.generativeai as genai
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                print("⚠️  GEMINI_API_KEY not found in .env file")
                return None
            
            genai.configure(api_key=api_key)
            model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
            model = genai.GenerativeModel(model_name)
            
            print(f"✅ Gemini initialized: {model_name}")
            return model
            
        except ImportError:
            print("⚠️  google-generativeai not installed. Run: pip install google-generativeai")
            return None
        except Exception as e:
            print(f"⚠️  Gemini initialization failed: {e}")
            return None
    
    def _init_ollama(self):
        """Initialize Ollama (local LLM)"""
        try:
            import requests
            
            # Test if Ollama is running
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            
            if response.status_code == 200:
                print("✅ Ollama initialized (local)")
                return 'ollama'
            else:
                print("⚠️  Ollama not responding")
                return None
                
        except Exception as e:
            print(f"⚠️  Ollama not available: {e}")
            return None
    
    def _init_gpt4(self):
        """Placeholder for future GPT-4 integration"""
        # Future implementation
        print("ℹ️  GPT-4 integration coming soon...")
        return None
    
    def _check_rate_limit(self) -> bool:
        """Check if Gemini rate limit is reached"""
        # Reset counter if new day
        if datetime.now().date() != self.last_reset_date:
            self.gemini_requests_today = 0
            self.last_reset_date = datetime.now().date()
        
        return self.gemini_requests_today < self.gemini_daily_limit
    
    def _build_cfa_prompt(self, question: str, company_data: Dict, context_type: str = 'general') -> str:
        """
        Build professional CFA-level prompt
        
        Args:
            question: User's question
            company_data: Financial metrics
            context_type: 'general', 'explanation', 'comparison', 'recommendation'
        """
        
        # Extract key metrics
        ticker = company_data.get('ticker', 'N/A')
        company_name = company_data.get('company_name', ticker)
        
        # Financial metrics
        pe_ratio = company_data.get('pe_ratio', 'N/A')
        growth = company_data.get('growth_rate', 'N/A')
        roe = company_data.get('roe', 'N/A')
        debt_equity = company_data.get('debt_equity', 'N/A')
        current_ratio = company_data.get('current_ratio', 'N/A')
        
        # Market data
        price = company_data.get('current_price', 'N/A')
        market_cap = company_data.get('market_cap', 'N/A')
        sector = company_data.get('sector', 'N/A')
        
        base_prompt = f"""
You are a CFA-certified financial analyst with 20 years of experience in equity research.
Your analysis is professional, data-driven, and suitable for institutional investors.

Company: {company_name} ({ticker})
Sector: {sector}

Key Financial Metrics:
- Current Price: {price}
- Market Cap: {market_cap}
- P/E Ratio: {pe_ratio}
- Growth Rate: {growth}
- ROE: {roe}%
- Debt/Equity: {debt_equity}
- Current Ratio: {current_ratio}

User Question: {question}

"""
        
        # Context-specific instructions
        if context_type == 'explanation':
            context_prompt = """
Provide a clear, professional explanation of the metric.
Include:
1. Definition and calculation
2. What it tells us about this company
3. Industry context (how it compares to sector average)
4. Investment implications

Keep explanation concise (3-4 sentences) but authoritative.
"""
        
        elif context_type == 'comparison':
            context_prompt = """
Provide a comprehensive comparison:
1. Key metrics side-by-side
2. Strengths and weaknesses of each
3. Which is better for different investor profiles
4. Risk-adjusted recommendation

Be balanced and objective.
"""
        
        elif context_type == 'recommendation':
            context_prompt = """
Provide investment recommendation:
1. Current valuation assessment (Overvalued/Fair/Undervalued)
2. Key catalysts and risks
3. Target price range (if applicable)
4. Investment rating: Buy / Hold / Sell
5. Suitability for different investor types

IMPORTANT: Include disclaimer that this is analysis, not financial advice.
"""
        
        else:  # general
            context_prompt = """
Provide professional analysis addressing the question.
Include:
1. Direct answer to the question
2. Supporting financial data
3. Industry context
4. Investment implications
5. Key risks or considerations

Be comprehensive but concise. Use professional financial terminology but explain when necessary.
"""
        
        return base_prompt + context_prompt
    
    def _validate_response(self, response: str, company_data: Dict) -> Tuple[bool, int, List[str]]:
        """
        Validate AI response for accuracy
        
        Returns:
            (is_valid, confidence_score, warnings)
        """
        warnings = []
        confidence = 100
        
        # Extract numbers from response
        numbers_in_response = re.findall(r'[\d,]+\.?\d*', response)
        
        # Check 1: Math validation
        pe_ratio = company_data.get('pe_ratio')
        if pe_ratio and str(pe_ratio) in response:
            # Verify P/E is mentioned correctly
            response_lower = response.lower()
            if 'p/e' in response_lower or 'pe ratio' in response_lower:
                # Good - P/E is contextualized
                pass
            else:
                warnings.append("P/E ratio mentioned without context")
                confidence -= 5
        
        # Check 2: Impossible values
        if 'growth rate' in response.lower():
            # Check for unrealistic growth (>200%)
            growth_numbers = [float(n.replace(',','')) for n in numbers_in_response if float(n.replace(',','')) > 100]
            if any(g > 200 for g in growth_numbers):
                warnings.append("Unrealistic growth rate mentioned")
                confidence -= 20
        
        # Check 3: Negative P/E logic
        if pe_ratio and pe_ratio < 0:
            if 'negative earnings' not in response.lower() and 'loss' not in response.lower():
                warnings.append("Negative P/E not explained properly")
                confidence -= 15
        
        # Check 4: Hallucination detection (basic)
        suspicious_phrases = [
            'according to recent reports',
            'analysts estimate',
            'expected to announce'
        ]
        for phrase in suspicious_phrases:
            if phrase in response.lower():
                warnings.append(f"Potentially unverifiable claim: '{phrase}'")
                confidence -= 10
        
        # Check 5: Response length (too short might be incomplete)
        if len(response) < 100:
            warnings.append("Response seems incomplete")
            confidence -= 10
        
        # Determine if valid
        is_valid = confidence >= 70
        
        return is_valid, max(0, confidence), warnings
    
    def _ask_gemini(self, prompt: str) -> Optional[str]:
        """Query Gemini API"""
        if not self.primary_model:
            _logger.debug("Gemini model not initialized")
            return None
        
        if not self._check_rate_limit():
            _logger.warning("Gemini daily limit reached, using fallback...")
            print("⚠️  Gemini daily limit reached, using fallback...")
            return None
        
        try:
            response = self.primary_model.generate_content(prompt)
            self.gemini_requests_today += 1
            
            # Log analytics
            if self.analytics_enabled:
                self._log_analytics('gemini', 'success', len(prompt))
            
            _logger.info(f"Gemini request successful | Prompt: {len(prompt)} chars | Response: {len(response.text)} chars")
            EngineLogger.log_ai_request('gemini', len(prompt), len(response.text), success=True)
            return response.text
            
        except Exception as e:
            _logger.error(f"Gemini error: {e}", exc_info=True)
            print(f"⚠️  Gemini error: {e}")
            
            # Log analytics
            if self.analytics_enabled:
                self._log_analytics('gemini', 'error', len(prompt))
            EngineLogger.log_ai_request('gemini', len(prompt), 0, success=False)
            
            return None
    
    def _ask_ollama(self, prompt: str) -> Optional[str]:
        """Query Ollama (local)"""
        if not self.fallback_model:
            _logger.debug("Ollama model not available")
            return None
        
        try:
            import requests
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama3.1',
                    'prompt': prompt,
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                # Log analytics
                if self.analytics_enabled:
                    self._log_analytics('ollama', 'success', len(prompt))
                
                _logger.info(f"Ollama request successful | Prompt: {len(prompt)} chars | Response: {len(response_text)} chars")
                EngineLogger.log_ai_request('ollama', len(prompt), len(response_text), success=True)
                return response_text
            else:
                _logger.warning(f"Ollama returned status code: {response.status_code}")
                print(f"⚠️  Ollama error: {response.status_code}")
                return None
                
        except Exception as e:
            _logger.error(f"Ollama error: {e}", exc_info=True)
            print(f"⚠️  Ollama error: {e}")
            
            # Log analytics
            if self.analytics_enabled:
                self._log_analytics('ollama', 'error', len(prompt))
            EngineLogger.log_ai_request('ollama', len(prompt), 0, success=False)
            
            return None
    
    def ask(self, question: str, company_data: Dict, context_type: str = 'general') -> Dict:
        """
        Main method to ask AI a question
        
        Returns:
            {
                'response': str,
                'model_used': str,
                'confidence': int,
                'warnings': List[str],
                'show_disclaimer': bool
            }
        """
        
        # Build prompt
        prompt = self._build_cfa_prompt(question, company_data, context_type)
        
        # Try primary model (Gemini)
        response = self._ask_gemini(prompt)
        model_used = 'gemini'
        
        # Fallback to Ollama if needed
        if not response:
            response = self._ask_ollama(prompt)
            model_used = 'ollama'
        
        # If still no response
        if not response:
            return {
                'response': "⚠️  AI service temporarily unavailable. Please try again.",
                'model_used': 'none',
                'confidence': 0,
                'warnings': ['No AI model available'],
                'show_disclaimer': False
            }
        
        # Validate response
        is_valid, confidence, warnings = self._validate_response(response, company_data)
        
        # Show disclaimer once per session
        show_disclaimer = not self.session_disclaimer_shown
        if show_disclaimer:
            self.session_disclaimer_shown = True
        
        # Add to conversation history
        self.conversation_history.append({
            'question': question,
            'response': response,
            'model': model_used,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'response': response,
            'model_used': model_used,
            'confidence': confidence,
            'warnings': warnings if not is_valid else [],
            'show_disclaimer': show_disclaimer
        }
    
    def _log_analytics(self, model: str, status: str, prompt_length: int):
        """Log anonymous analytics"""
        self.analytics_data.append({
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'status': status,
            'prompt_length': prompt_length
        })
        
        # Save to file periodically
        if len(self.analytics_data) >= 10:
            self._save_analytics()
    
    def _save_analytics(self):
        """Save analytics to file"""
        try:
            analytics_file = 'ai_analytics.json'
            
            # Load existing
            existing = []
            if os.path.exists(analytics_file):
                with open(analytics_file, 'r') as f:
                    existing = json.load(f)
            
            # Append new
            existing.extend(self.analytics_data)
            
            # Save
            with open(analytics_file, 'w') as f:
                json.dump(existing, f, indent=2)
            
            # Clear buffer
            self.analytics_data = []
            
        except Exception as e:
            print(f"⚠️  Analytics save error: {e}")
    
    def get_analytics_summary(self) -> Dict:
        """Get analytics summary"""
        try:
            if not os.path.exists('ai_analytics.json'):
                return {'total_requests': 0}
            
            with open('ai_analytics.json', 'r') as f:
                data = json.load(f)
            
            gemini_success = sum(1 for d in data if d['model'] == 'gemini' and d['status'] == 'success')
            ollama_success = sum(1 for d in data if d['model'] == 'ollama' and d['status'] == 'success')
            errors = sum(1 for d in data if d['status'] == 'error')
            
            return {
                'total_requests': len(data),
                'gemini_success': gemini_success,
                'ollama_success': ollama_success,
                'errors': errors,
                'success_rate': (gemini_success + ollama_success) / len(data) * 100 if data else 0
            }
            
        except Exception as e:
            return {'error': str(e)}


# Quick explanation generator for inline tooltips
def explain_metric(metric_name: str, metric_value, company_data: Dict, ai: FinancialAI) -> str:
    """
    Generate quick explanation for inline tooltip
    
    Args:
        metric_name: Name of metric (e.g., "P/E Ratio")
        metric_value: Value of metric
        company_data: Company financial data
        ai: FinancialAI instance
    
    Returns:
        Brief explanation (2-3 sentences)
    """
    
    question = f"Briefly explain {metric_name} of {metric_value} for this company in 2-3 sentences."
    
    result = ai.ask(question, company_data, context_type='explanation')
    
    return result['response']


# Example usage
if __name__ == "__main__":
    # Test the system
    print("="*80)
    print("FINANCIAL AI ADVISOR - TEST")
    print("="*80)
    
    # Initialize
    ai = FinancialAI(tier='free')
    
    # Sample company data
    test_data = {
        'ticker': 'AAPL',
        'company_name': 'Apple Inc.',
        'sector': 'Technology',
        'current_price': 195.50,
        'market_cap': '3.0T',
        'pe_ratio': 28.5,
        'growth_rate': 12.0,
        'roe': 147,
        'debt_equity': 1.96,
        'current_ratio': 1.05
    }
    
    # Test question
    question = "Should I invest in Apple at the current price?"
    
    print(f"\nQuestion: {question}\n")
    
    result = ai.ask(question, test_data, context_type='recommendation')
    
    print("="*80)
    print(f"Model Used: {result['model_used'].upper()}")
    print(f"Confidence: {result['confidence']}%")
    print("="*80)
    print(result['response'])
    print("="*80)
    
    if result['warnings']:
        print("\n⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    if result['show_disclaimer']:
        print("\n📋 Disclaimer: This is educational analysis, not financial advice.")


