#!/usr/bin/env python3
"""
Tests for Switching Logic
========================

Unit tests for the intelligent framework switching engine.
"""

import unittest
from datetime import datetime
from intelligent_fallback_generator import (
    HealthMetrics, SwitchingEngine, FailureDetector
)


class TestSwitchingLogic(unittest.TestCase):
    """Test framework switching logic."""
    
    def setUp(self):
        self.switching_engine = SwitchingEngine()
        self.failure_detector = FailureDetector()
    
    def test_healthy_framework_no_switch(self):
        """Test that healthy framework doesn't trigger switch."""
        healthy_metrics = HealthMetrics(
            framework="claude",
            timestamp=datetime.now(),
            response_time=5.0,
            success_rate=0.9,
            error_count=0,
            last_error=None,
            consecutive_failures=0,
            api_available=True,
            tasks_completed=9,
            total_tasks=10
        )
        
        should_switch, reason = self.failure_detector.should_trigger_switch(healthy_metrics)
        self.assertFalse(should_switch)
    
    def test_consecutive_failures_trigger_switch(self):
        """Test that consecutive failures trigger switch."""
        failing_metrics = HealthMetrics(
            framework="claude",
            timestamp=datetime.now(),
            response_time=30.0,
            success_rate=0.0,
            error_count=5,
            last_error="API timeout",
            consecutive_failures=3,
            api_available=True,
            tasks_completed=0,
            total_tasks=5
        )
        
        should_switch, reason = self.failure_detector.should_trigger_switch(failing_metrics)
        self.assertTrue(should_switch)
        self.assertIn("Consecutive failures", reason)
    
    def test_api_unavailable_triggers_switch(self):
        """Test that API unavailability triggers immediate switch."""
        unavailable_metrics = HealthMetrics(
            framework="opencode",
            timestamp=datetime.now(),
            response_time=0.0,
            success_rate=0.5,
            error_count=2,
            last_error="Connection failed",
            consecutive_failures=1,
            api_available=False,
            tasks_completed=3,
            total_tasks=6
        )
        
        should_switch, reason = self.failure_detector.should_trigger_switch(unavailable_metrics)
        self.assertTrue(should_switch)
        self.assertEqual(reason, "API unavailable")
    
    def test_health_score_calculation(self):
        """Test health score calculation."""
        metrics = HealthMetrics(
            framework="claude",
            timestamp=datetime.now(),
            response_time=10.0,
            success_rate=0.8,
            error_count=2,
            last_error=None,
            consecutive_failures=0,
            api_available=True,
            tasks_completed=8,
            total_tasks=10
        )
        
        health_score = metrics.health_score
        self.assertGreater(health_score, 0.5)
        self.assertLessEqual(health_score, 1.0)


if __name__ == "__main__":
    unittest.main()