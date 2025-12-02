"""
SECURITY UTILITIES MODULE
=========================
Centralized security functions for input validation, sanitization, and threat detection.

Features:
- SQL injection detection and prevention
- XSS (Cross-Site Scripting) prevention
- Path traversal prevention
- Safe string sanitization
- File path validation
- Rate limiting helpers
"""

import re
import os
from typing import Tuple, Optional, List
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class SecurityValidator:
    """
    Centralized security validation for all user inputs.
    Prevents SQL injection, XSS, path traversal, and other attacks.
    """
    
    # ==========================================
    # SECURITY PATTERNS
    # ==========================================
    
    # SQL Injection patterns
    SQL_PATTERNS = [
        re.compile(r"(\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b|\bSELECT\b|\bUNION\b|\bEXEC\b)", re.IGNORECASE),
        re.compile(r"[;']"),  # SQL statement terminators
        re.compile(r"(-{2}|/\*|\*/|xp_)", re.IGNORECASE),  # SQL comments
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"on\w+\s*=", re.IGNORECASE),  # Event handlers (onclick, onerror, etc.)
        re.compile(r"<iframe", re.IGNORECASE),
        re.compile(r"<object", re.IGNORECASE),
        re.compile(r"<embed", re.IGNORECASE),
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        re.compile(r"\.\./"),  # Unix-style
        re.compile(r"\.\.\\"),  # Windows-style
        re.compile(r"~"),  # Home directory
        re.compile(r"/etc/"),  # Unix system files
        re.compile(r"\\windows\\", re.IGNORECASE),  # Windows system files
        re.compile(r"%00"),  # Null byte injection
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        re.compile(r"[;&|`$]"),  # Shell metacharacters
        re.compile(r"\$\(.*\)"),  # Command substitution
        re.compile(r"`.*`"),  # Backtick execution
    ]
    
    # ==========================================
    # 1. SQL INJECTION PREVENTION
    # ==========================================
    
    @staticmethod
    def detect_sql_injection(input_str: str) -> Tuple[bool, Optional[str]]:
        """
        Detect SQL injection attempts in user input.
        
        Args:
            input_str: User input to validate
            
        Returns:
            (is_safe, threat_description or None)
        """
        if not input_str or not isinstance(input_str, str):
            return True, None
        
        for pattern in SecurityValidator.SQL_PATTERNS:
            if pattern.search(input_str):
                return False, f"SQL injection pattern detected: {pattern.pattern}"
        
        return True, None
    
    # ==========================================
    # 2. XSS PREVENTION
    # ==========================================
    
    @staticmethod
    def detect_xss(input_str: str) -> Tuple[bool, Optional[str]]:
        """
        Detect XSS (Cross-Site Scripting) attempts in user input.
        
        Args:
            input_str: User input to validate
            
        Returns:
            (is_safe, threat_description or None)
        """
        if not input_str or not isinstance(input_str, str):
            return True, None
        
        for pattern in SecurityValidator.XSS_PATTERNS:
            if pattern.search(input_str):
                return False, f"XSS pattern detected: {pattern.pattern}"
        
        return True, None
    
    # ==========================================
    # 3. PATH TRAVERSAL PREVENTION
    # ==========================================
    
    @staticmethod
    def detect_path_traversal(input_str: str) -> Tuple[bool, Optional[str]]:
        """
        Detect path traversal attempts in user input.
        
        Args:
            input_str: User input to validate (e.g., filename)
            
        Returns:
            (is_safe, threat_description or None)
        """
        if not input_str or not isinstance(input_str, str):
            return True, None
        
        for pattern in SecurityValidator.PATH_TRAVERSAL_PATTERNS:
            if pattern.search(input_str):
                return False, f"Path traversal pattern detected: {pattern.pattern}"
        
        return True, None
    
    # ==========================================
    # 4. COMMAND INJECTION PREVENTION
    # ==========================================
    
    @staticmethod
    def detect_command_injection(input_str: str) -> Tuple[bool, Optional[str]]:
        """
        Detect command injection attempts in user input.
        
        Args:
            input_str: User input to validate
            
        Returns:
            (is_safe, threat_description or None)
        """
        if not input_str or not isinstance(input_str, str):
            return True, None
        
        for pattern in SecurityValidator.COMMAND_INJECTION_PATTERNS:
            if pattern.search(input_str):
                return False, f"Command injection pattern detected: {pattern.pattern}"
        
        return True, None
    
    # ==========================================
    # 5. COMPREHENSIVE VALIDATION
    # ==========================================
    
    @staticmethod
    def validate_input(input_str: str, input_type: str = "general") -> Tuple[bool, Optional[str]]:
        """
        Comprehensive input validation against all threats.
        
        Args:
            input_str: User input to validate
            input_type: Type of input ("general", "filename", "ticker", "query")
            
        Returns:
            (is_safe, threat_description or None)
        """
        if not input_str:
            return True, None
        
        # Check all threat types
        checks = [
            SecurityValidator.detect_sql_injection(input_str),
            SecurityValidator.detect_xss(input_str),
            SecurityValidator.detect_command_injection(input_str),
        ]
        
        # Add path traversal check for filename inputs
        if input_type in ["filename", "path"]:
            checks.append(SecurityValidator.detect_path_traversal(input_str))
        
        # Return first detected threat
        for is_safe, threat in checks:
            if not is_safe:
                return False, threat
        
        return True, None
    
    # ==========================================
    # 6. SANITIZATION
    # ==========================================
    
    @staticmethod
    def sanitize_string(input_str: str, allow_alphanumeric_only: bool = False) -> str:
        """
        Sanitize user input by removing dangerous characters.
        
        Args:
            input_str: User input to sanitize
            allow_alphanumeric_only: If True, only allow letters, numbers, spaces, hyphens
            
        Returns:
            Sanitized string
        """
        if not input_str or not isinstance(input_str, str):
            return ""
        
        # Remove null bytes
        sanitized = input_str.replace('\x00', '')
        
        # Remove control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
        
        # If strict mode, only allow safe characters
        if allow_alphanumeric_only:
            sanitized = re.sub(r'[^a-zA-Z0-9\s\-_.]', '', sanitized)
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and invalid characters.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Safe filename
        """
        if not filename:
            return "unnamed"
        
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', filename)
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Ensure not empty
        if not filename:
            return "unnamed"
        
        return filename
    
    # ==========================================
    # 7. SAFE FILE PATH VALIDATION
    # ==========================================
    
    @staticmethod
    def validate_file_path(file_path: str, allowed_base_dir: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate file path is safe and within allowed directory.
        
        Args:
            file_path: File path to validate
            allowed_base_dir: Base directory that file must be within (optional)
            
        Returns:
            (is_safe, error_message or None)
        """
        try:
            # Convert to Path object
            path = Path(file_path).resolve()
            
            # Check if path exists
            if not path.exists():
                return False, f"Path does not exist: {file_path}"
            
            # If base directory specified, ensure file is within it
            if allowed_base_dir:
                base = Path(allowed_base_dir).resolve()
                try:
                    path.relative_to(base)
                except ValueError:
                    return False, f"Path is outside allowed directory: {file_path}"
            
            return True, None
            
        except Exception as e:
            return False, f"Invalid path: {str(e)}"
    
    # ==========================================
    # 8. BATCH VALIDATION
    # ==========================================
    
    @staticmethod
    def validate_batch(inputs: List[str], input_type: str = "general") -> dict:
        """
        Validate multiple inputs at once.
        
        Args:
            inputs: List of user inputs
            input_type: Type of input ("general", "filename", "ticker", "query")
            
        Returns:
            Dictionary with validation results for each input
        """
        results = {}
        for i, input_str in enumerate(inputs):
            is_safe, threat = SecurityValidator.validate_input(input_str, input_type)
            results[f"input_{i}"] = {
                'input': input_str,
                'safe': is_safe,
                'threat': threat,
                'sanitized': SecurityValidator.sanitize_string(input_str)
            }
        return results


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def quick_validate(input_str: str) -> bool:
    """
    Quick validation helper (returns bool only).
    
    Args:
        input_str: User input to validate
        
    Returns:
        True if input is safe
    """
    is_safe, _ = SecurityValidator.validate_input(input_str)
    return is_safe


def sanitize(input_str: str) -> str:
    """
    Quick sanitization helper.
    
    Args:
        input_str: User input to sanitize
        
    Returns:
        Sanitized string
    """
    return SecurityValidator.sanitize_string(input_str)


if __name__ == "__main__":
    # Test cases
    print("=" * 80)
    print("SECURITY VALIDATOR - TEST SUITE")
    print("=" * 80)
    
    test_cases = [
        ("AAPL", "general", True, "Normal ticker"),
        ("SELECT * FROM users", "general", False, "SQL injection"),
        ("'; DROP TABLE users; --", "general", False, "SQL injection with comment"),
        ("<script>alert('XSS')</script>", "general", False, "XSS attack"),
        ("javascript:alert(1)", "general", False, "XSS via javascript:"),
        ("../etc/passwd", "filename", False, "Path traversal (Unix)"),
        ("..\\windows\\system32", "filename", False, "Path traversal (Windows)"),
        ("report_2025.pdf", "filename", True, "Safe filename"),
        ("test; rm -rf /", "general", False, "Command injection"),
        ("normal text input", "general", True, "Safe text"),
    ]
    
    for input_str, input_type, should_pass, description in test_cases:
        is_safe, threat = SecurityValidator.validate_input(input_str, input_type)
        status = "✅ PASS" if (is_safe == should_pass) else "❌ FAIL"
        threat_msg = f" | Threat: {threat}" if threat else ""
        print(f"{status} | {description:35} | Input: {input_str:30}{threat_msg}")
    
    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)


