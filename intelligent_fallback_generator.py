#!/usr/bin/env python3
"""
Intelligent Fallback Autonomous Code Generator
=============================================

An advanced autonomous code generation system that intelligently switches between
Claude SDK and OpenCode SDK based on real-time failure detection, API availability
monitoring, and task completion success rates.

Features:
- Real-time failure detection and log analysis
- Intelligent framework switching with multiple strategies
- Health monitoring and performance analytics
- Configuration-driven fallback behavior
- Production-ready reliability and monitoring

Based on patterns from ai_coder.py fallback system with advanced intelligence.

Usage:
    python intelligent_fallback_generator.py "Create a Python calculator" -l ./projects -p calc
    python intelligent_fallback_generator.py "Build web app" -l ./projects -p app --strategy performance_based
    python intelligent_fallback_generator.py -i task.txt -l ./projects -p processor --config claude_primary_config.json

Author: Autonomous Development Framework
License: MIT
"""

import argparse
import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import tempfile

# Import the unified generator components
try:
    from unified_autonomous_generator import (
        BaseAutonomousGenerator, 
        ClaudeAutonomousGenerator, 
        OpenCodeAutonomousGenerator,
        create_generator
    )
    UNIFIED_GENERATOR_AVAILABLE = True
except ImportError:
    print("❌ Unified generator not available. Please ensure unified_autonomous_generator.py is in the same directory.")
    UNIFIED_GENERATOR_AVAILABLE = False


@dataclass
class HealthMetrics:
    """Health and performance metrics for a framework."""
    framework: str
    timestamp: datetime
    response_time: float
    success_rate: float
    error_count: int
    last_error: Optional[str]
    consecutive_failures: int
    api_available: bool
    tasks_completed: int
    total_tasks: int
    
    @property
    def health_score(self) -> float:
        """Calculate overall health score (0.0 to 1.0)."""
        if not self.api_available:
            return 0.0
        
        # Weight factors for health calculation
        success_weight = 0.4
        response_weight = 0.3
        error_weight = 0.2
        consecutive_weight = 0.1
        
        # Normalize metrics to 0-1 scale
        success_score = self.success_rate
        response_score = max(0, 1 - (self.response_time / 60))  # 60s max
        error_score = max(0, 1 - (self.error_count / 10))  # 10 errors max
        consecutive_score = max(0, 1 - (self.consecutive_failures / 5))  # 5 failures max
        
        return (
            success_weight * success_score +
            response_weight * response_score +
            error_weight * error_score +
            consecutive_weight * consecutive_score
        )


@dataclass
class SwitchingEvent:
    """Record of a framework switching event."""
    timestamp: datetime
    from_framework: str
    to_framework: str
    reason: str
    trigger_metrics: HealthMetrics
    success: bool


class FailureDetector:
    """Advanced failure detection engine with log analysis capabilities."""
    
    # Failure patterns based on ai_coder.py analysis
    FAILURE_PATTERNS = {
        "api_errors": [
            r"API key.*invalid",
            r"rate limit.*exceeded", 
            r"authentication.*failed",
            r"connection.*timeout",
            r"service.*unavailable",
            r"quota.*exceeded",
            r"billing.*issue"
        ],
        "execution_errors": [
            r"command.*not.*found",
            r"module.*not.*found", 
            r"import.*error",
            r"syntax.*error",
            r"runtime.*error",
            r"permission.*denied"
        ],
        "framework_specific": {
            "claude": [
                r"claude.*session.*failed",
                r"mcp.*server.*unavailable",
                r"context.*window.*exceeded",
                r"claude.*sdk.*error"
            ],
            "opencode": [
                r"opencode.*session.*failed", 
                r"provider.*unavailable",
                r"model.*not.*supported",
                r"session.*timeout"
            ]
        }
    }
    
    def __init__(self, consecutive_failure_threshold: int = 3, 
                 error_rate_threshold: float = 0.3):
        self.consecutive_failure_threshold = consecutive_failure_threshold
        self.error_rate_threshold = error_rate_threshold
        self.logger = logging.getLogger(__name__)
    
    def analyze_log_output(self, output: str, framework: str) -> Dict[str, Any]:
        """Analyze log output for failure patterns."""
        analysis = {
            "has_errors": False,
            "error_type": None,
            "error_patterns": [],
            "severity": "low"
        }
        
        # Check for API errors (high severity)
        for pattern in self.FAILURE_PATTERNS["api_errors"]:
            if re.search(pattern, output, re.IGNORECASE):
                analysis["has_errors"] = True
                analysis["error_type"] = "api_error"
                analysis["error_patterns"].append(pattern)
                analysis["severity"] = "high"
        
        # Check for execution errors (medium severity)
        if not analysis["has_errors"]:
            for pattern in self.FAILURE_PATTERNS["execution_errors"]:
                if re.search(pattern, output, re.IGNORECASE):
                    analysis["has_errors"] = True
                    analysis["error_type"] = "execution_error"
                    analysis["error_patterns"].append(pattern)
                    analysis["severity"] = "medium"
        
        # Check for framework-specific errors
        if framework in self.FAILURE_PATTERNS["framework_specific"]:
            for pattern in self.FAILURE_PATTERNS["framework_specific"][framework]:
                if re.search(pattern, output, re.IGNORECASE):
                    analysis["has_errors"] = True
                    analysis["error_type"] = f"{framework}_specific"
                    analysis["error_patterns"].append(pattern)
                    analysis["severity"] = "high"
        
        return analysis
    
    def should_trigger_switch(self, metrics: HealthMetrics) -> Tuple[bool, str]:
        """Determine if a framework switch should be triggered."""
        
        # Immediate triggers
        if not metrics.api_available:
            return True, "API unavailable"
        
        if metrics.consecutive_failures >= self.consecutive_failure_threshold:
            return True, f"Consecutive failures exceeded threshold ({metrics.consecutive_failures})"
        
        # Error rate threshold
        if metrics.total_tasks > 5:  # Only check after sufficient sample size
            error_rate = metrics.error_count / metrics.total_tasks
            if error_rate > self.error_rate_threshold:
                return True, f"Error rate too high ({error_rate:.2f})"
        
        # Health score threshold
        if metrics.health_score < 0.3:
            return True, f"Health score too low ({metrics.health_score:.2f})"
        
        return False, ""


class PerformanceMonitor:
    """Monitor framework performance and health metrics."""
    
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.metrics_history: Dict[str, List[HealthMetrics]] = {}
        self.logger = logging.getLogger(__name__)
    
    def update_metrics(self, framework: str, response_time: float, 
                      success: bool, error: Optional[str] = None):
        """Update performance metrics for a framework."""
        
        if framework not in self.metrics_history:
            self.metrics_history[framework] = []
        
        history = self.metrics_history[framework]
        
        # Calculate metrics from recent history
        recent_tasks = len(history)
        recent_successes = sum(1 for m in history if m.success_rate > 0)
        recent_errors = sum(m.error_count for m in history)
        
        # Count consecutive failures
        consecutive_failures = 0
        for metrics in reversed(history):
            if metrics.success_rate == 0:
                consecutive_failures += 1
            else:
                break
        
        if not success:
            consecutive_failures += 1
        
        # Create new metrics entry
        metrics = HealthMetrics(
            framework=framework,
            timestamp=datetime.now(),
            response_time=response_time,
            success_rate=1.0 if success else 0.0,
            error_count=1 if error else 0,
            last_error=error,
            consecutive_failures=consecutive_failures,
            api_available=True,  # Will be updated by health checker
            tasks_completed=recent_successes + (1 if success else 0),
            total_tasks=recent_tasks + 1
        )
        
        # Add to history and trim if needed
        history.append(metrics)
        if len(history) > self.window_size:
            history.pop(0)
        
        # Calculate rolling metrics
        if len(history) > 1:
            metrics.success_rate = sum(1 for m in history if m.success_rate > 0) / len(history)
            metrics.error_count = sum(m.error_count for m in history)
            metrics.tasks_completed = sum(1 for m in history if m.success_rate > 0)
            metrics.total_tasks = len(history)
        
        self.logger.debug(f"Updated {framework} metrics: health={metrics.health_score:.2f}")
        return metrics
    
    def get_current_metrics(self, framework: str) -> Optional[HealthMetrics]:
        """Get current metrics for a framework."""
        if framework not in self.metrics_history or not self.metrics_history[framework]:
            return None
        return self.metrics_history[framework][-1]
    
    async def check_api_availability(self, framework: str) -> bool:
        """Check if a framework's API is available."""
        try:
            # Simple health check - try to create a generator instance
            if framework == "claude":
                generator = ClaudeAutonomousGenerator(enable_simulation=True)
            elif framework == "opencode":
                generator = OpenCodeAutonomousGenerator(enable_simulation=True)
            else:
                return False
            
            return True
        except Exception as e:
            self.logger.warning(f"API availability check failed for {framework}: {e}")
            return False


class SwitchingEngine:
    """Intelligent framework switching engine with multiple strategies."""
    
    def __init__(self, strategy: str = "intelligent_primary_secondary"):
        self.strategy = strategy
        self.switching_history: List[SwitchingEvent] = []
        self.hysteresis_time = 300  # 5 minutes minimum between switches
        self.logger = logging.getLogger(__name__)
    
    def should_switch_framework(self, current_framework: str, 
                               current_metrics: HealthMetrics,
                               fallback_metrics: Optional[HealthMetrics],
                               failure_detector: FailureDetector) -> Tuple[bool, str, str]:
        """Decide if framework should be switched."""
        
        # Check for recent switches (hysteresis)
        if self.switching_history:
            last_switch = self.switching_history[-1]
            time_since_switch = (datetime.now() - last_switch.timestamp).total_seconds()
            if time_since_switch < self.hysteresis_time:
                return False, "", "Recent switch hysteresis"
        
        # Check if current framework should be switched
        should_switch, reason = failure_detector.should_trigger_switch(current_metrics)
        if not should_switch:
            return False, "", reason
        
        # Determine target framework
        target_framework = "opencode" if current_framework == "claude" else "claude"
        
        # Validate target framework is healthy
        if fallback_metrics and fallback_metrics.health_score < 0.5:
            self.logger.warning(f"Target framework {target_framework} also unhealthy")
            return False, "", "Target framework unhealthy"
        
        return True, target_framework, reason
    
    def record_switch(self, from_framework: str, to_framework: str, 
                     reason: str, metrics: HealthMetrics, success: bool):
        """Record a switching event."""
        event = SwitchingEvent(
            timestamp=datetime.now(),
            from_framework=from_framework,
            to_framework=to_framework,
            reason=reason,
            trigger_metrics=metrics,
            success=success
        )
        self.switching_history.append(event)
        
        # Keep only recent history
        if len(self.switching_history) > 50:
            self.switching_history.pop(0)
        
        self.logger.info(f"Recorded switch: {from_framework} → {to_framework} ({reason})")


class ConfigManager:
    """Manage fallback system configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load fallback configuration."""
        default_config = {
            "fallback_system": {
                "enabled": True,
                "strategy": "intelligent_primary_secondary",
                "monitoring_interval": 30,
                "health_check_timeout": 10,
                "consecutive_failure_threshold": 3,
                "error_rate_threshold": 0.3,
                "response_time_threshold": 30.0,
                "hysteresis_time": 300
            },
            "frameworks": {
                "primary": {
                    "name": "claude",
                    "enabled": True,
                    "priority": 1,
                    "health_weight": 1.0
                },
                "secondary": {
                    "name": "opencode",
                    "enabled": True, 
                    "priority": 2,
                    "health_weight": 0.9
                }
            },
            "task_routing": {
                "simple_tasks": "opencode",
                "complex_tasks": "claude",
                "web_development": "opencode",
                "algorithm_implementation": "claude"
            }
        }
        
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                default_config.update(loaded_config)
                return default_config
            except Exception as e:
                print(f"Error loading config {self.config_path}: {e}")
        
        return default_config
    
    def get_primary_framework(self) -> str:
        """Get the primary framework name."""
        return self.config["frameworks"]["primary"]["name"]
    
    def get_secondary_framework(self) -> str:
        """Get the secondary framework name."""
        return self.config["frameworks"]["secondary"]["name"]
    
    def get_fallback_settings(self) -> Dict[str, Any]:
        """Get fallback system settings."""
        return self.config["fallback_system"]


class IntelligentFallbackGenerator:
    """
    Main orchestrator for intelligent fallback autonomous code generation.
    
    Manages multiple framework instances with intelligent switching, failure detection,
    and performance monitoring based on ai_coder.py fallback patterns.
    """
    
    def __init__(self, config_path: Optional[str] = None, enable_simulation: bool = False):
        self.config_manager = ConfigManager(config_path)
        self.enable_simulation = enable_simulation
        
        # Initialize components
        settings = self.config_manager.get_fallback_settings()
        self.failure_detector = FailureDetector(
            consecutive_failure_threshold=settings["consecutive_failure_threshold"],
            error_rate_threshold=settings["error_rate_threshold"]
        )
        self.performance_monitor = PerformanceMonitor()
        self.switching_engine = SwitchingEngine(strategy=settings["strategy"])
        
        # Initialize framework generators
        self.generators: Dict[str, BaseAutonomousGenerator] = {}
        self.current_framework = self.config_manager.get_primary_framework()
        
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize generators
        self._initialize_generators()
    
    def setup_logging(self):
        """Setup comprehensive logging."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"fallback_generator_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def _initialize_generators(self):
        """Initialize both framework generators."""
        try:
            # Initialize Claude generator
            self.generators["claude"] = ClaudeAutonomousGenerator(
                enable_simulation=self.enable_simulation
            )
            self.logger.info("✅ Claude generator initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Claude generator: {e}")
        
        try:
            # Initialize OpenCode generator  
            self.generators["opencode"] = OpenCodeAutonomousGenerator(
                enable_simulation=self.enable_simulation
            )
            self.logger.info("✅ OpenCode generator initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize OpenCode generator: {e}")
        
        if not self.generators:
            raise RuntimeError("No generators could be initialized")
    
    async def _execute_with_monitoring(self, generator: BaseAutonomousGenerator, 
                                     task: str, location: str, project_name: str,
                                     framework: str) -> Tuple[Optional[Path], bool, float, Optional[str]]:
        """Execute code generation with performance monitoring."""
        start_time = time.time()
        error_message = None
        
        try:
            self.logger.info(f"🚀 Starting {framework} generation for: {task}")
            
            # Execute generation
            project_dir, success = await generator.generate_code(task, location, project_name)
            
            # Calculate metrics
            response_time = time.time() - start_time
            
            self.logger.info(f"✅ {framework} completed in {response_time:.2f}s, success: {success}")
            return project_dir, success, response_time, error_message
            
        except Exception as e:
            response_time = time.time() - start_time
            error_message = str(e)
            
            # Analyze error for failure patterns
            analysis = self.failure_detector.analyze_log_output(error_message, framework)
            
            self.logger.error(f"❌ {framework} failed after {response_time:.2f}s: {error_message}")
            self.logger.debug(f"Error analysis: {analysis}")
            
            return None, False, response_time, error_message
    
    async def generate_code_with_fallback(self, task: str, location: str, 
                                        project_name: str) -> Tuple[Optional[Path], bool, List[str]]:
        """
        Generate code with intelligent fallback between frameworks.
        
        Returns:
            Tuple of (project_directory, success, frameworks_tried)
        """
        
        frameworks_tried = []
        last_error = None
        
        # Try current framework first
        framework = self.current_framework
        if framework not in self.generators:
            self.logger.error(f"Framework {framework} not available")
            # Switch to available framework
            available = [f for f in self.generators.keys() if f != framework]
            if available:
                framework = available[0]
                self.current_framework = framework
            else:
                return None, False, []
        
        for attempt in range(2):  # Try up to 2 frameworks
            if framework in frameworks_tried:
                break
                
            frameworks_tried.append(framework)
            generator = self.generators[framework]
            
            # Execute with monitoring
            project_dir, success, response_time, error = await self._execute_with_monitoring(
                generator, task, location, project_name, framework
            )
            
            # Update performance metrics
            metrics = self.performance_monitor.update_metrics(
                framework, response_time, success, error
            )
            
            # Check API availability
            metrics.api_available = await self.performance_monitor.check_api_availability(framework)
            
            if success:
                self.logger.info(f"🎉 Successfully completed with {framework}")
                return project_dir, True, frameworks_tried
            
            # Check if we should switch frameworks
            other_framework = "opencode" if framework == "claude" else "claude"
            other_metrics = self.performance_monitor.get_current_metrics(other_framework)
            
            should_switch, target_framework, reason = self.switching_engine.should_switch_framework(
                framework, metrics, other_metrics, self.failure_detector
            )
            
            if should_switch and target_framework in self.generators:
                self.logger.info(f"🔄 Switching from {framework} to {target_framework}: {reason}")
                
                # Record the switch
                self.switching_engine.record_switch(
                    framework, target_framework, reason, metrics, False
                )
                
                # Update current framework
                self.current_framework = target_framework
                framework = target_framework
                last_error = error
            else:
                self.logger.warning(f"No suitable fallback available for {framework}")
                break
        
        self.logger.error(f"❌ All frameworks failed. Tried: {frameworks_tried}")
        return None, False, frameworks_tried
    
    def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "current_framework": self.current_framework,
            "frameworks": {},
            "switching_history": [],
            "overall_health": "unknown"
        }
        
        # Framework health
        total_health = 0
        healthy_count = 0
        
        for framework in self.generators.keys():
            metrics = self.performance_monitor.get_current_metrics(framework)
            if metrics:
                report["frameworks"][framework] = {
                    "health_score": metrics.health_score,
                    "success_rate": metrics.success_rate,
                    "response_time": metrics.response_time,
                    "consecutive_failures": metrics.consecutive_failures,
                    "api_available": metrics.api_available,
                    "tasks_completed": metrics.tasks_completed,
                    "total_tasks": metrics.total_tasks
                }
                
                if metrics.api_available:
                    total_health += metrics.health_score
                    healthy_count += 1
        
        # Overall health assessment
        if healthy_count > 0:
            avg_health = total_health / healthy_count
            if avg_health > 0.8:
                report["overall_health"] = "excellent"
            elif avg_health > 0.6:
                report["overall_health"] = "good"
            elif avg_health > 0.4:
                report["overall_health"] = "fair"
            else:
                report["overall_health"] = "poor"
        
        # Recent switching history
        recent_switches = self.switching_engine.switching_history[-10:]
        for switch in recent_switches:
            report["switching_history"].append({
                "timestamp": switch.timestamp.isoformat(),
                "from": switch.from_framework,
                "to": switch.to_framework,
                "reason": switch.reason,
                "success": switch.success
            })
        
        return report


def read_instruction_file(file_path: str) -> str:
    """Read instruction file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            raise ValueError(f"Instruction file {file_path} is empty")
        
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"Instruction file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading instruction file {file_path}: {e}")


def main():
    """Main entry point for the intelligent fallback generator."""
    parser = argparse.ArgumentParser(
        description="Intelligent Fallback Autonomous Code Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic usage with intelligent fallback
    python intelligent_fallback_generator.py "Create a Python calculator" -l ./projects -p calc
    
    # Use specific configuration
    python intelligent_fallback_generator.py "Build web app" -l ./projects -p app --config claude_primary_config.json
    
    # Enable simulation mode
    python intelligent_fallback_generator.py "Create API server" -l ./test -p api --enable-simulation
    
    # From instruction file with performance strategy
    echo "Create a data processing pipeline" > task.txt
    python intelligent_fallback_generator.py -i task.txt -l ./projects -p pipeline --strategy performance_based
    
    # Get health report
    python intelligent_fallback_generator.py --health-report
        """
    )
    
    # Input arguments
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "task",
        nargs="?",
        help="Text description of what to generate"
    )
    input_group.add_argument(
        "-i", "--input-file",
        type=str,
        help="Path to file containing program instructions"
    )
    input_group.add_argument(
        "--health-report",
        action="store_true",
        help="Generate and display health report"
    )
    
    # Project arguments
    parser.add_argument(
        "-l", "--location",
        type=str,
        help="Directory where project will be created"
    )
    parser.add_argument(
        "-p", "--project",
        type=str,
        help="Project name"
    )
    
    # Fallback system arguments
    parser.add_argument(
        "--config",
        type=str,
        help="Path to fallback configuration file"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["intelligent_primary_secondary", "performance_based", "round_robin"],
        default="intelligent_primary_secondary",
        help="Fallback strategy to use"
    )
    parser.add_argument(
        "--enable-simulation",
        action="store_true",
        help="Enable simulation mode for testing without API keys"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    if not UNIFIED_GENERATOR_AVAILABLE:
        print("❌ Unified generator components not available")
        return 1
    
    try:
        # Initialize fallback generator
        generator = IntelligentFallbackGenerator(
            config_path=args.config,
            enable_simulation=args.enable_simulation
        )
        
        # Handle health report request
        if args.health_report:
            report = generator.get_health_report()
            print("🏥 Framework Health Report")
            print("=" * 50)
            print(json.dumps(report, indent=2, default=str))
            return 0
        
        # Validate required arguments for code generation
        if not args.task and not args.input_file:
            print("❌ Either task description or input file is required")
            return 1
        
        if not args.location or not args.project:
            print("❌ Location (-l) and project (-p) arguments are required")
            return 1
        
        # Determine task description
        if args.task:
            task_description = args.task
        else:
            task_description = read_instruction_file(args.input_file)
            print(f"📖 Loaded instructions from: {args.input_file}")
        
        # Run intelligent fallback generation
        print(f"🤖 Starting intelligent fallback autonomous generation...")
        print(f"   Task: {task_description}")
        print(f"   Location: {args.location}")
        print(f"   Project: {args.project}")
        print(f"   Strategy: {args.strategy}")
        
        project_dir, success, frameworks_tried = asyncio.run(
            generator.generate_code_with_fallback(
                task_description, args.location, args.project
            )
        )
        
        if success and project_dir:
            print(f"\\n🎉 SUCCESS: Intelligent fallback generation completed!")
            print(f"📁 Project created at: {project_dir}")
            print(f"🔧 Frameworks used: {' → '.join(frameworks_tried)}")
            print(f"\\n🚀 To use your generated project:")
            print(f"   cd {project_dir}")
            print(f"   cat README.md          # Read documentation")
            print(f"   ./init.sh              # Set up environment")
            
            # Show specific run instructions
            if (project_dir / "src" / "main.py").exists():
                print(f"   python3 src/main.py    # Run Python program")
            elif (project_dir / "src" / "main.js").exists():
                print(f"   node src/main.js       # Run JavaScript program")
            
            # Display health report
            print(f"\\n📊 Final Health Report:")
            report = generator.get_health_report()
            print(f"   Overall Health: {report['overall_health']}")
            print(f"   Active Framework: {report['current_framework']}")
            
            return 0
        else:
            print(f"\\n❌ Generation failed")
            print(f"🔧 Frameworks attempted: {', '.join(frameworks_tried) if frameworks_tried else 'None'}")
            
            # Display health report for debugging
            print(f"\\n📊 Health Report for Debugging:")
            report = generator.get_health_report()
            for framework, metrics in report["frameworks"].items():
                print(f"   {framework}: health={metrics.get('health_score', 0):.2f}, available={metrics.get('api_available', False)}")
            
            return 1
            
    except KeyboardInterrupt:
        print("\\n⏹️ Generation interrupted by user")
        return 1
    except Exception as e:
        print(f"\\n💥 Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())