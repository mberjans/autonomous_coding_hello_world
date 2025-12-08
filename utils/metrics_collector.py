#!/usr/bin/env python3
"""
Metrics Collection Utilities
============================

Collect and aggregate performance metrics for framework monitoring.
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import statistics


@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: float
    framework: str
    metric_type: str
    value: float
    metadata: Dict[str, Any]


class MetricsCollector:
    """Collect and aggregate performance metrics."""
    
    def __init__(self, retention_hours: int = 24):
        self.metrics: List[MetricPoint] = []
        self.retention_hours = retention_hours
    
    def record_metric(self, framework: str, metric_type: str, 
                     value: float, metadata: Dict[str, Any] = None):
        """Record a metric point."""
        point = MetricPoint(
            timestamp=time.time(),
            framework=framework,
            metric_type=metric_type,
            value=value,
            metadata=metadata or {}
        )
        
        self.metrics.append(point)
        self._cleanup_old_metrics()
    
    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period."""
        cutoff = time.time() - (self.retention_hours * 3600)
        self.metrics = [m for m in self.metrics if m.timestamp >= cutoff]
    
    def get_framework_summary(self, framework: str, 
                            hours: int = 1) -> Dict[str, Any]:
        """Get summary statistics for a framework."""
        cutoff = time.time() - (hours * 3600)
        
        framework_metrics = [
            m for m in self.metrics 
            if m.framework == framework and m.timestamp >= cutoff
        ]
        
        if not framework_metrics:
            return {"error": "No metrics found"}
        
        # Group by metric type
        by_type = {}
        for metric in framework_metrics:
            if metric.metric_type not in by_type:
                by_type[metric.metric_type] = []
            by_type[metric.metric_type].append(metric.value)
        
        # Calculate statistics
        summary = {}
        for metric_type, values in by_type.items():
            summary[metric_type] = {
                "count": len(values),
                "avg": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "latest": values[-1] if values else 0
            }
            
            if len(values) > 1:
                summary[metric_type]["std"] = statistics.stdev(values)
        
        return summary
    
    def export_metrics(self) -> List[Dict[str, Any]]:
        """Export all metrics as JSON-serializable format."""
        return [asdict(metric) for metric in self.metrics]