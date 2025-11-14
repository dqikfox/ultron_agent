"""
AWS CloudWatch Integration for ULTRON Diagnostics
Syncs diagnostics data to AWS for oasis_app monitoring
"""

import boto3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import asyncio

from diagnostics.diagnostics_core import get_diagnostics
from utils.ultron_logger import log_info, log_error


class CloudWatchIntegration:
    """
    Integrate ULTRON diagnostics with AWS CloudWatch

    Sends metrics, logs, and alarms to AWS for centralized monitoring
    Compatible with oasis_app infrastructure
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.region = config.get("aws", {}).get("region", "us-west-2")
        self.namespace = "ULTRON/Diagnostics"
        self.app_name = config.get("aws", {}).get("oasis_app", {}).get("name", "oasis_app")

        # AWS clients
        try:
            self.cloudwatch = boto3.client('cloudwatch', region_name=self.region)
            self.logs_client = boto3.client('logs', region_name=self.region)
            self.enabled = True
            log_info("cloudwatch_integration", f"CloudWatch integration enabled for {self.region}")
        except Exception as e:
            log_error("cloudwatch_integration", f"Failed to initialize AWS clients: {e}")
            self.enabled = False

        # Log group
        self.log_group_name = f"/ultron/{self.app_name}/diagnostics"
        self.log_stream_name = f"diagnostics-{datetime.now().strftime('%Y-%m-%d')}"

        if self.enabled:
            self._ensure_log_group()

    def _ensure_log_group(self):
        """Create log group if it doesn't exist"""
        try:
            self.logs_client.create_log_group(logGroupName=self.log_group_name)
            log_info("cloudwatch_integration", f"Created log group: {self.log_group_name}")
        except self.logs_client.exceptions.ResourceAlreadyExistsException:
            pass
        except Exception as e:
            log_error("cloudwatch_integration", f"Failed to create log group: {e}")

        try:
            self.logs_client.create_log_stream(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name
            )
        except self.logs_client.exceptions.ResourceAlreadyExistsException:
            pass
        except Exception as e:
            log_error("cloudwatch_integration", f"Failed to create log stream: {e}")

    async def send_metrics(self, diagnostics_summary: Dict[str, Any]):
        """
        Send diagnostic metrics to CloudWatch

        Metrics include:
        - Crash counts
        - System health
        - Performance metrics
        """
        if not self.enabled:
            return

        try:
            metrics = []

            # Crash metrics
            crashes = diagnostics_summary.get("crashes", {})
            metrics.append({
                'MetricName': 'TotalCrashes',
                'Value': crashes.get("total", 0),
                'Unit': 'Count',
                'Timestamp': datetime.now()
            })
            metrics.append({
                'MetricName': 'CrashesLastHour',
                'Value': crashes.get("last_hour", 0),
                'Unit': 'Count',
                'Timestamp': datetime.now()
            })
            metrics.append({
                'MetricName': 'UnresolvedIssues',
                'Value': crashes.get("unresolved", 0),
                'Unit': 'Count',
                'Timestamp': datetime.now()
            })

            # System health metrics
            health = diagnostics_summary.get("performance", {}).get("latest_health", {})
            if health:
                metrics.extend([
                    {
                        'MetricName': 'CPUUtilization',
                        'Value': health.get("cpu_percent", 0),
                        'Unit': 'Percent',
                        'Timestamp': datetime.now()
                    },
                    {
                        'MetricName': 'MemoryUtilization',
                        'Value': health.get("memory_percent", 0),
                        'Unit': 'Percent',
                        'Timestamp': datetime.now()
                    },
                    {
                        'MetricName': 'DiskUtilization',
                        'Value': health.get("disk_usage_percent", 0),
                        'Unit': 'Percent',
                        'Timestamp': datetime.now()
                    }
                ])

            # Send metrics in batches (CloudWatch limit: 20 per request)
            for i in range(0, len(metrics), 20):
                batch = metrics[i:i+20]
                self.cloudwatch.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=batch
                )

            log_info("cloudwatch_integration", f"Sent {len(metrics)} metrics to CloudWatch")

        except Exception as e:
            log_error("cloudwatch_integration", f"Failed to send metrics: {e}")

    async def send_crash_log(self, crash_report: Dict[str, Any]):
        """Send crash report to CloudWatch Logs"""
        if not self.enabled:
            return

        try:
            log_event = {
                'timestamp': int(datetime.now().timestamp() * 1000),
                'message': json.dumps({
                    'event_type': 'crash',
                    'crash_id': crash_report.get('crash_id'),
                    'component': crash_report.get('component'),
                    'exception_type': crash_report.get('exception_type'),
                    'exception_message': crash_report.get('exception_message'),
                    'severity': crash_report.get('severity'),
                    'timestamp': crash_report.get('timestamp')
                })
            }

            self.logs_client.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name,
                logEvents=[log_event]
            )

            log_info("cloudwatch_integration", f"Sent crash log: {crash_report.get('crash_id')}")

        except Exception as e:
            log_error("cloudwatch_integration", f"Failed to send crash log: {e}")

    async def create_alarm(
        self,
        alarm_name: str,
        metric_name: str,
        threshold: float,
        comparison_operator: str = "GreaterThanThreshold"
    ):
        """
        Create CloudWatch alarm

        Example: Alert when crash count exceeds 10
        """
        if not self.enabled:
            return

        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName=f"ULTRON-{self.app_name}-{alarm_name}",
                ComparisonOperator=comparison_operator,
                EvaluationPeriods=1,
                MetricName=metric_name,
                Namespace=self.namespace,
                Period=300,  # 5 minutes
                Statistic='Sum',
                Threshold=threshold,
                ActionsEnabled=False,
                AlarmDescription=f'ULTRON diagnostics alarm: {alarm_name}'
            )

            log_info("cloudwatch_integration", f"Created alarm: {alarm_name}")

        except Exception as e:
            log_error("cloudwatch_integration", f"Failed to create alarm: {e}")

    async def sync_diagnostics(self):
        """
        Full sync of diagnostics to CloudWatch

        Call this periodically (e.g., every 5 minutes)
        """
        if not self.enabled:
            return

        try:
            diagnostics = get_diagnostics()
            summary = diagnostics.get_diagnostics_summary()

            # Send metrics
            await self.send_metrics(summary)

            # Send recent crash logs
            recent_crashes = [
                c for c in diagnostics.crash_reports
                if datetime.fromisoformat(c.timestamp) >
                   datetime.now() - timedelta(minutes=10)
            ]

            for crash in recent_crashes:
                await self.send_crash_log({
                    'crash_id': crash.crash_id,
                    'component': crash.component,
                    'exception_type': crash.exception_type,
                    'exception_message': crash.exception_message,
                    'severity': crash.severity,
                    'timestamp': crash.timestamp
                })

            log_info("cloudwatch_integration", "Diagnostics sync completed")

        except Exception as e:
            log_error("cloudwatch_integration", f"Failed to sync diagnostics: {e}")


# Background sync task
async def run_cloudwatch_sync(config: Dict[str, Any], interval_minutes: int = 5):
    """
    Run CloudWatch sync in background

    Usage:
        asyncio.create_task(run_cloudwatch_sync(config))
    """
    from datetime import timedelta

    integration = CloudWatchIntegration(config)

    if not integration.enabled:
        log_info("cloudwatch_sync", "CloudWatch integration disabled, skipping sync")
        return

    log_info("cloudwatch_sync", f"Starting CloudWatch sync (interval: {interval_minutes}m)")

    while True:
        try:
            await integration.sync_diagnostics()
            await asyncio.sleep(interval_minutes * 60)
        except Exception as e:
            log_error("cloudwatch_sync", f"Sync task error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error


# Example: Setup default alarms
async def setup_default_alarms(config: Dict[str, Any]):
    """Create recommended CloudWatch alarms"""
    integration = CloudWatchIntegration(config)

    if not integration.enabled:
        return

    # Alarm when crashes exceed 10 per hour
    await integration.create_alarm(
        alarm_name="HighCrashRate",
        metric_name="CrashesLastHour",
        threshold=10.0
    )

    # Alarm when CPU exceeds 90%
    await integration.create_alarm(
        alarm_name="HighCPU",
        metric_name="CPUUtilization",
        threshold=90.0
    )

    # Alarm when memory exceeds 85%
    await integration.create_alarm(
        alarm_name="HighMemory",
        metric_name="MemoryUtilization",
        threshold=85.0
    )

    log_info("cloudwatch_alarms", "Default alarms configured")
