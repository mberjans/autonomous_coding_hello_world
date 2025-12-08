#!/usr/bin/env python3
"""
Log Analysis Utilities
=====================

Advanced log analysis utilities for detecting framework failures and patterns.
Based on patterns identified in ai_coder.py fallback system.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class LogAnalysisResult:
    """Result of log analysis operation."""
    has_errors: bool
    error_type: Optional[str]
    error_patterns: List[str]
    severity: str
    confidence: float
    suggestions: List[str]


class LogAnalyzer:
    """Advanced log analyzer for framework failure detection."""
    
    # Extended failure patterns from ai_coder.py analysis
    CRITICAL_PATTERNS = {
        "authentication": [
            r"API key.*invalid",
            r"authentication.*failed",
            r"unauthorized.*access",
            r"invalid.*credentials",
            r"token.*expired"
        ],
        "rate_limiting": [
            r"rate limit.*exceeded",
            r"quota.*exceeded",
            r"throttled.*request",
            r"too many.*requests",
            r"billing.*limit"
        ],
        "network": [
            r"connection.*timeout",
            r"network.*error",
            r"dns.*resolution.*failed",
            r"connection.*refused",
            r"service.*unavailable"
        ],
        "resource": [
            r"memory.*error",
            r"out of.*memory",
            r"disk.*full",
            r"resource.*exhausted",
            r"timeout.*exceeded"
        ]
    }
    
    FRAMEWORK_PATTERNS = {
        "claude": [
            r"claude.*session.*failed",
            r"mcp.*server.*unavailable",
            r"context.*window.*exceeded",
            r"claude.*sdk.*error",
            r"anthropic.*api.*error"
        ],
        "opencode": [
            r"opencode.*session.*failed",
            r"provider.*unavailable", 
            r"model.*not.*supported",
            r"session.*timeout",
            r"opencode.*api.*error"
        ]
    }
    
    EXECUTION_PATTERNS = {
        "import_errors": [
            r"module.*not.*found",
            r"import.*error",
            r"no module named",
            r"cannot import.*name"
        ],
        "syntax_errors": [
            r"syntax.*error",
            r"invalid.*syntax",
            r"indentation.*error",
            r"unexpected.*token"
        ],
        "runtime_errors": [
            r"runtime.*error",
            r"null.*pointer",
            r"segmentation.*fault",
            r"stack.*overflow"
        ]
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_log_content(self, log_content: str, framework: str = None) -> LogAnalysisResult:
        """
        Comprehensive analysis of log content for failure detection.
        
        Args:
            log_content: Raw log content to analyze
            framework: Specific framework context (claude, opencode)
            
        Returns:
            LogAnalysisResult with detailed analysis
        """
        
        result = LogAnalysisResult(
            has_errors=False,
            error_type=None,
            error_patterns=[],
            severity="low",
            confidence=0.0,
            suggestions=[]
        )
        
        # Check critical patterns first (highest severity)
        for category, patterns in self.CRITICAL_PATTERNS.items():
            matches = self._check_patterns(log_content, patterns)
            if matches:
                result.has_errors = True
                result.error_type = category
                result.error_patterns.extend(matches)
                result.severity = "critical"
                result.confidence = 0.9
                result.suggestions.extend(self._get_suggestions(category))
        
        # Check framework-specific patterns
        if framework and framework in self.FRAMEWORK_PATTERNS:
            matches = self._check_patterns(log_content, self.FRAMEWORK_PATTERNS[framework])
            if matches:
                result.has_errors = True
                if not result.error_type:
                    result.error_type = f"{framework}_specific"
                result.error_patterns.extend(matches)
                result.severity = max(result.severity, "high", key=self._severity_weight)
                result.confidence = max(result.confidence, 0.8)
                result.suggestions.extend(self._get_framework_suggestions(framework))
        
        # Check execution patterns (medium severity)
        if not result.has_errors:
            for category, patterns in self.EXECUTION_PATTERNS.items():
                matches = self._check_patterns(log_content, patterns)
                if matches:
                    result.has_errors = True
                    result.error_type = category
                    result.error_patterns.extend(matches)
                    result.severity = "medium"
                    result.confidence = 0.7
                    result.suggestions.extend(self._get_execution_suggestions(category))
                    break
        
        return result
    
    def _check_patterns(self, content: str, patterns: List[str]) -> List[str]:
        """Check content against list of regex patterns."""
        matches = []
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                matches.append(pattern)
        return matches
    
    def _severity_weight(self, severity: str) -> int:
        """Get numeric weight for severity comparison."""
        weights = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        return weights.get(severity, 0)
    
    def _get_suggestions(self, category: str) -> List[str]:
        """Get remediation suggestions for error category."""
        suggestions = {
            "authentication": [
                "Check API key validity and expiration",
                "Verify environment variables are set correctly",
                "Rotate API key if compromised"
            ],
            "rate_limiting": [
                "Implement exponential backoff",
                "Check API usage quotas",
                "Consider upgrading API plan"
            ],
            "network": [
                "Check internet connectivity",
                "Verify firewall settings",
                "Try alternative network endpoint"
            ],
            "resource": [
                "Monitor system resource usage",
                "Increase timeout values",
                "Check available disk space"
            ]
        }
        return suggestions.get(category, ["Review error logs for specific details"])
    
    def _get_framework_suggestions(self, framework: str) -> List[str]:
        """Get framework-specific suggestions."""
        suggestions = {
            "claude": [
                "Check Claude SDK installation and version",
                "Verify MCP server configuration",
                "Review Claude API status page"
            ],
            "opencode": [
                "Check OpenCode SDK installation",
                "Verify provider API keys",
                "Try alternative provider/model"
            ]
        }
        return suggestions.get(framework, ["Check framework documentation"])
    
    def _get_execution_suggestions(self, category: str) -> List[str]:
        """Get execution error suggestions."""
        suggestions = {
            "import_errors": [
                "Check Python package installation",
                "Verify PYTHONPATH configuration",
                "Install missing dependencies"
            ],
            "syntax_errors": [
                "Review generated code for syntax issues",
                "Check Python version compatibility",
                "Validate code formatting"
            ],
            "runtime_errors": [
                "Check input data validity",
                "Review error stack trace",
                "Validate program logic"
            ]
        }
        return suggestions.get(category, ["Review execution environment"])
    
    def extract_error_metrics(self, log_content: str) -> Dict[str, Any]:
        """Extract quantitative metrics from log content."""
        metrics = {
            "error_count": 0,
            "warning_count": 0,
            "critical_count": 0,
            "response_times": [],
            "error_types": {},
            "timestamp_range": None
        }
        
        lines = log_content.split('\n')
        
        for line in lines:
            # Count error levels
            if re.search(r'ERROR', line, re.IGNORECASE):
                metrics["error_count"] += 1
            elif re.search(r'WARNING', line, re.IGNORECASE):
                metrics["warning_count"] += 1
            elif re.search(r'CRITICAL', line, re.IGNORECASE):
                metrics["critical_count"] += 1
            
            # Extract response times
            time_match = re.search(r'(\d+\.?\d*)\s*seconds?', line)
            if time_match:
                metrics["response_times"].append(float(time_match.group(1)))
            
            # Extract timestamps for range calculation
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})', line)
            if timestamp_match:
                try:
                    timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                    if not metrics["timestamp_range"]:
                        metrics["timestamp_range"] = [timestamp, timestamp]
                    else:
                        metrics["timestamp_range"][0] = min(metrics["timestamp_range"][0], timestamp)
                        metrics["timestamp_range"][1] = max(metrics["timestamp_range"][1], timestamp)
                except ValueError:
                    pass
        
        return metrics


def analyze_framework_logs(log_file_path: str, framework: str) -> LogAnalysisResult:
    """Convenience function to analyze framework log file."""
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analyzer = LogAnalyzer()
        return analyzer.analyze_log_content(content, framework)
    
    except Exception as e:
        return LogAnalysisResult(
            has_errors=True,
            error_type="file_error",
            error_patterns=[str(e)],
            severity="critical",
            confidence=1.0,
            suggestions=[f"Check log file accessibility: {log_file_path}"]
        )