# Validation module for ATLAS Financial Intelligence
# Contains benchmark comparison and accuracy validation tools

from .benchmark_validator import BenchmarkValidator, validate_metrics

__all__ = ['BenchmarkValidator', 'validate_metrics']

