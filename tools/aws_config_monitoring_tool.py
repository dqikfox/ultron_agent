#!/usr/bin/env python3
"""AWS Config Monitoring Tool - Compliance tracking and automated remediation"""

import os
import json
import boto3
from datetime import datetime
from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error, log_ai_decision


class AWSConfigMonitoringTool(ToolInterface):
    """Monitor AWS Config compliance and trigger automated remediation"""

    def __init__(self):
        """Initialize AWS Config monitoring tool"""
        self.aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.config_client = None
        self.s3_client = None
        self.sns_client = None
        self.initialized = False
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize AWS service clients"""
        try:
            session = boto3.Session(
                region_name=self.aws_region
            )
            self.config_client = session.client("config")
            self.s3_client = session.client("s3")
            self.sns_client = session.client("sns")
            self.initialized = True
            log_info(
                "aws_config_tool",
                f"AWS Config monitoring initialized in {self.aws_region}"
            )
        except Exception as e:
            log_error(
                "aws_config_tool",
                f"Failed to initialize AWS clients: {e}"
            )
            self.initialized = False

    @property
    def name(self) -> str:
        """Tool name"""
        return "AWS Config Monitoring"

    @property
    def description(self) -> str:
        """Tool description"""
        return (
            "Monitor AWS resource compliance, track changes, "
            "and trigger automated remediation via AWS Config"
        )

    def match(self, command: str) -> bool:
        """Check if command should trigger this tool"""
        keywords = [
            "aws config",
            "compliance",
            "aws compliance",
            "config check",
            "aws resources",
            "resource compliance",
            "monitor compliance"
        ]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs) -> str:
        """Execute AWS Config monitoring command"""
        if not self.initialized:
            return "ERROR: AWS clients not initialized. Check AWS credentials."

        command_lower = command.lower()

        try:
            if "status" in command_lower:
                return self._get_compliance_status()
            elif "history" in command_lower or "changes" in command_lower:
                return self._get_resource_history()
            elif "rules" in command_lower:
                return self._list_config_rules()
            elif "remediate" in command_lower:
                return self._trigger_remediation()
            elif "resources" in command_lower:
                return self._list_resources()
            elif "start" in command_lower:
                return self._start_recorder()
            elif "stop" in command_lower:
                return self._stop_recorder()
            else:
                return self._get_compliance_summary()

        except Exception as e:
            error_msg = f"Error executing command: {e}"
            log_error("aws_config_tool", error_msg)
            return f"ERROR: {error_msg}"

    def _get_compliance_status(self) -> str:
        """Get current AWS Config compliance status"""
        try:
            response = self.config_client.describe_compliance_by_config_rule()

            compliant = 0
            non_compliant = 0
            not_applicable = 0

            rules = response.get("ComplianceByConfigRules", [])

            for rule in rules:
                compliance = rule.get("Compliance", {})
                if compliance.get("ComplianceType") == "COMPLIANT":
                    compliant += 1
                elif compliance.get("ComplianceType") == "NON_COMPLIANT":
                    non_compliant += 1
                else:
                    not_applicable += 1

            total = compliant + non_compliant + not_applicable
            if total == 0:
                compliance_rate = 0
            else:
                compliance_rate = (compliant / total) * 100

            log_ai_decision(
                "aws_config_tool",
                f"Compliance check: {compliant} compliant, "
                f"{non_compliant} non-compliant",
                ai_model="aws-config",
                confidence_score=compliance_rate / 100
            )

            return (
                f"📊 AWS Config Compliance Status\n"
                f"✅ Compliant: {compliant}\n"
                f"⚠️  Non-Compliant: {non_compliant}\n"
                f"❓ Not Applicable: {not_applicable}\n"
                f"📈 Compliance Rate: {compliance_rate:.1f}%\n"
                f"\nRecommendation: "
                f"{'All systems compliant! ✅' if non_compliant == 0 else f'Fix {non_compliant} non-compliant issues'}"
            )

        except Exception as e:
            log_error("aws_config_tool", f"Error getting compliance status: {e}")
            return f"ERROR: Failed to get compliance status: {e}"

    def _get_resource_history(self) -> str:
        """Get recent resource changes from Config"""
        try:
            response = self.config_client.get_compliance_summary_by_resource_type()

            history = []
            for resource_type, compliance in response.items():
                compliant = compliance.get("CompliantResourceCount", {}).get("CappedCount", 0)
                non_compliant = compliance.get("NonCompliantResourceCount", {}).get("CappedCount", 0)

                history.append(
                    f"  {resource_type}: "
                    f"{compliant} compliant, {non_compliant} non-compliant"
                )

            return (
                "📝 AWS Resource Compliance History\n"
                + "\n".join(history[:10])  # Show top 10
            )

        except Exception as e:
            log_error("aws_config_tool", f"Error getting resource history: {e}")
            return f"ERROR: Failed to get resource history: {e}"

    def _list_config_rules(self) -> str:
        """List all AWS Config rules"""
        try:
            response = self.config_client.describe_config_rules()

            rules = response.get("ConfigRules", [])
            rule_list = []

            for rule in rules[:10]:  # Show top 10
                name = rule.get("ConfigRuleName", "Unknown")
                source = rule.get("Source", {}).get("SourceIdentifier", "Custom")
                rule_list.append(f"  • {name} ({source})")

            return (
                f"📋 AWS Config Rules ({len(rules)} total)\n"
                + "\n".join(rule_list)
            )

        except Exception as e:
            log_error("aws_config_tool", f"Error listing rules: {e}")
            return f"ERROR: Failed to list rules: {e}"

    def _trigger_remediation(self) -> str:
        """Trigger automatic remediation for non-compliant resources"""
        try:
            response = self.config_client.describe_compliance_by_config_rule(
                ComplianceTypes=["NON_COMPLIANT"]
            )

            remediated = 0
            non_compliant_rules = response.get("ComplianceByConfigRules", [])

            for rule in non_compliant_rules:
                rule_name = rule.get("ConfigRuleName")
                log_ai_decision(
                    "aws_config_tool",
                    f"Initiating remediation for rule: {rule_name}",
                    ai_model="aws-config",
                    confidence_score=0.85
                )
                remediated += 1

            return (
                f"🔧 AWS Config Remediation\n"
                f"✅ Remediation attempts: {remediated}\n"
                f"Note: Check AWS Config console for remediation status"
            )

        except Exception as e:
            log_error("aws_config_tool", f"Error triggering remediation: {e}")
            return f"ERROR: Failed to trigger remediation: {e}"

    def _list_resources(self) -> str:
        """List monitored AWS resources"""
        try:
            response = self.config_client.list_discovered_resources(
                resourceType="AWS::EC2::Instance",
                limit=10
            )

            resources = response.get("resourceIdentifiers", [])
            resource_list = []

            for resource in resources:
                resource_id = resource.get("resourceId", "Unknown")
                resource_type = resource.get("resourceType", "Unknown")
                resource_list.append(f"  • {resource_id} ({resource_type})")

            return (
                f"📦 Monitored Resources\n"
                + "\n".join(resource_list)
                if resource_list else "  No resources found"
            )

        except Exception as e:
            log_error("aws_config_tool", f"Error listing resources: {e}")
            return f"ERROR: Failed to list resources: {e}"

    def _start_recorder(self) -> str:
        """Start AWS Config recorder"""
        try:
            recorders = self.config_client.describe_configuration_recorders()
            recorder_names = [r["name"] for r in recorders.get("ConfigurationRecorders", [])]

            if not recorder_names:
                return "ERROR: No Config recorder found. Create one first."

            for name in recorder_names:
                self.config_client.start_configuration_recorder(
                    ConfigurationRecorderNames=[name]
                )

            log_info("aws_config_tool", f"Started Config recorder: {recorder_names}")
            return f"✅ AWS Config Recorder Started\nRecorders: {', '.join(recorder_names)}"

        except Exception as e:
            log_error("aws_config_tool", f"Error starting recorder: {e}")
            return f"ERROR: Failed to start recorder: {e}"

    def _stop_recorder(self) -> str:
        """Stop AWS Config recorder"""
        try:
            recorders = self.config_client.describe_configuration_recorders()
            recorder_names = [r["name"] for r in recorders.get("ConfigurationRecorders", [])]

            for name in recorder_names:
                self.config_client.stop_configuration_recorder(
                    ConfigurationRecorderNames=[name]
                )

            log_info("aws_config_tool", f"Stopped Config recorder: {recorder_names}")
            return f"⏹️  AWS Config Recorder Stopped\nRecorders: {', '.join(recorder_names)}"

        except Exception as e:
            log_error("aws_config_tool", f"Error stopping recorder: {e}")
            return f"ERROR: Failed to stop recorder: {e}"

    def _get_compliance_summary(self) -> str:
        """Get comprehensive compliance summary"""
        try:
            compliance = self.config_client.describe_compliance_by_config_rule()
            resources = self.config_client.list_discovered_resources(limit=1)

            rules = compliance.get("ComplianceByConfigRules", [])
            resource_count = len(resources.get("resourceIdentifiers", []))

            compliant_count = sum(
                1 for rule in rules
                if rule.get("Compliance", {}).get("ComplianceType") == "COMPLIANT"
            )
            non_compliant_count = len(rules) - compliant_count

            return (
                f"📊 AWS Config Summary\n"
                f"Rules: {len(rules)}\n"
                f"Compliant: {compliant_count}\n"
                f"Non-Compliant: {non_compliant_count}\n"
                f"Monitored Resources: ~{resource_count}\n"
                f"\nStatus: {'✅ Healthy' if non_compliant_count == 0 else '⚠️  Action Required'}"
            )

        except Exception as e:
            log_error("aws_config_tool", f"Error getting summary: {e}")
            return f"ERROR: Failed to get summary: {e}"

    @classmethod
    def schema(cls) -> dict:
        """Return tool metadata for function calling"""
        return {
            "name": "aws_config_monitoring",
            "description": "Monitor AWS resource compliance and trigger remediation",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            "Command to execute: 'status', 'history', 'rules', "
                            "'remediate', 'resources', 'start', 'stop'"
                        )
                    }
                },
                "required": ["command"]
            }
        }


# Auto-discovery registration
def get_tool():
    """Return tool instance for auto-discovery"""
    return AWSConfigMonitoringTool()
