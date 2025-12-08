#!/usr/bin/env python3
"""
Tests for Failure Detection Engine
=================================

Unit tests for the failure detection and log analysis components.
"""

import unittest
from utils.log_analyzer import LogAnalyzer, LogAnalysisResult


class TestFailureDetection(unittest.TestCase):
    """Test failure detection logic."""
    
    def setUp(self):
        self.analyzer = LogAnalyzer()
    
    def test_api_key_error_detection(self):
        """Test detection of API key errors."""
        log_content = "ERROR: API key is invalid or expired"
        result = self.analyzer.analyze_log_content(log_content)
        
        self.assertTrue(result.has_errors)
        self.assertEqual(result.error_type, "authentication")
        self.assertEqual(result.severity, "critical")
        self.assertGreater(result.confidence, 0.8)
    
    def test_rate_limit_detection(self):
        """Test detection of rate limiting."""
        log_content = "WARNING: Rate limit exceeded, please try again later"
        result = self.analyzer.analyze_log_content(log_content)
        
        self.assertTrue(result.has_errors)
        self.assertEqual(result.error_type, "rate_limiting")
        self.assertEqual(result.severity, "critical")
    
    def test_claude_specific_errors(self):
        """Test Claude-specific error patterns."""
        log_content = "ERROR: Claude session failed to initialize"
        result = self.analyzer.analyze_log_content(log_content, framework="claude")
        
        self.assertTrue(result.has_errors)
        self.assertEqual(result.error_type, "claude_specific")
        self.assertIn("claude.*session.*failed", result.error_patterns)
    
    def test_opencode_specific_errors(self):
        """Test OpenCode-specific error patterns."""
        log_content = "ERROR: OpenCode session timeout occurred"
        result = self.analyzer.analyze_log_content(log_content, framework="opencode")
        
        self.assertTrue(result.has_errors)
        self.assertEqual(result.error_type, "opencode_specific")
    
    def test_no_errors_detected(self):
        """Test clean log content with no errors."""
        log_content = "INFO: Successfully generated code\nINFO: Task completed"
        result = self.analyzer.analyze_log_content(log_content)
        
        self.assertFalse(result.has_errors)
        self.assertIsNone(result.error_type)
        self.assertEqual(result.severity, "low")


if __name__ == "__main__":
    unittest.main()