import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, List
from utils.ultron_logger import log_info, log_error

class AWSCostMonitor:
    """AWS cost monitoring and alerting for ULTRON Agent"""
    
    def __init__(self):
        self.ce_client = boto3.client('ce', region_name='us-east-1')
        self.sns_client = boto3.client('sns', region_name='us-east-1')
        self.cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
    
    def get_current_costs(self) -> Dict:
        """Get current month AWS costs"""
        try:
            end_date = datetime.now().date()
            start_date = end_date.replace(day=1)
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            costs = {}
            total_cost = 0
            
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    costs[service] = cost
                    total_cost += cost
            
            log_info("cost_monitor", f"Current month costs: ${total_cost:.2f}")
            return {'total': total_cost, 'by_service': costs}
            
        except Exception as e:
            log_error("cost_monitor", f"Error getting costs: {e}")
            return {'total': 0, 'by_service': {}}
    
    def check_budget_alerts(self, budget_limit: float = 100.0) -> List[Dict]:
        """Check if costs exceed budget thresholds"""
        costs = self.get_current_costs()
        total_cost = costs['total']
        alerts = []
        
        thresholds = [
            (25, 0.25, "INFO"),
            (50, 0.50, "WARNING"), 
            (75, 0.75, "CRITICAL"),
            (90, 0.90, "URGENT")
        ]
        
        for threshold_pct, threshold_ratio, severity in thresholds:
            threshold_amount = budget_limit * threshold_ratio
            
            if total_cost >= threshold_amount:
                alert = {
                    'severity': severity,
                    'threshold': threshold_pct,
                    'current_cost': total_cost,
                    'budget_limit': budget_limit,
                    'percentage_used': (total_cost / budget_limit) * 100,
                    'message': f"AWS costs at {threshold_pct}% of budget (${total_cost:.2f}/${budget_limit:.2f})"
                }
                alerts.append(alert)
                log_info("cost_monitor", alert['message'])
        
        return alerts
    
    def send_cost_alert(self, alert: Dict, sns_topic_arn: str):
        """Send cost alert via SNS"""
        try:
            message = {
                'alert_type': 'AWS_COST_ALERT',
                'severity': alert['severity'],
                'current_cost': alert['current_cost'],
                'budget_limit': alert['budget_limit'],
                'percentage_used': alert['percentage_used'],
                'timestamp': datetime.now().isoformat(),
                'project': 'ULTRON Agent'
            }
            
            self.sns_client.publish(
                TopicArn=sns_topic_arn,
                Subject=f"ULTRON Agent - AWS Cost Alert ({alert['severity']})",
                Message=json.dumps(message, indent=2)
            )
            
            log_info("cost_monitor", f"Cost alert sent: {alert['severity']}")
            
        except Exception as e:
            log_error("cost_monitor", f"Error sending alert: {e}")
    
    def get_bedrock_usage(self) -> Dict:
        """Get Bedrock-specific usage metrics"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['BlendedCost', 'UsageQuantity'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ],
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': ['Amazon Bedrock']
                    }
                }
            )
            
            bedrock_costs = []
            for result in response['ResultsByTime']:
                date = result['TimePeriod']['Start']
                cost = 0
                usage = 0
                
                for group in result['Groups']:
                    if 'Amazon Bedrock' in group['Keys']:
                        cost = float(group['Metrics']['BlendedCost']['Amount'])
                        usage = float(group['Metrics']['UsageQuantity']['Amount'])
                
                bedrock_costs.append({
                    'date': date,
                    'cost': cost,
                    'usage': usage
                })
            
            return {'daily_usage': bedrock_costs}
            
        except Exception as e:
            log_error("cost_monitor", f"Error getting Bedrock usage: {e}")
            return {'daily_usage': []}
    
    def publish_metrics_to_cloudwatch(self, costs: Dict):
        """Publish cost metrics to CloudWatch"""
        try:
            self.cloudwatch.put_metric_data(
                Namespace='ULTRON/Costs',
                MetricData=[
                    {
                        'MetricName': 'TotalMonthlyCost',
                        'Value': costs['total'],
                        'Unit': 'None',
                        'Timestamp': datetime.now()
                    }
                ]
            )
            
            for service, cost in costs['by_service'].items():
                self.cloudwatch.put_metric_data(
                    Namespace='ULTRON/Costs',
                    MetricData=[
                        {
                            'MetricName': f'{service}Cost',
                            'Value': cost,
                            'Unit': 'None',
                            'Timestamp': datetime.now()
                        }
                    ]
                )
            
            log_info("cost_monitor", "Metrics published to CloudWatch")
            
        except Exception as e:
            log_error("cost_monitor", f"Error publishing metrics: {e}")

def monitor_aws_costs():
    """Main function to run cost monitoring"""
    monitor = AWSCostMonitor()
    
    # Get current costs
    costs = monitor.get_current_costs()
    
    # Check budget alerts
    alerts = monitor.check_budget_alerts(budget_limit=100.0)
    
    # Publish metrics
    monitor.publish_metrics_to_cloudwatch(costs)
    
    # Get Bedrock usage
    bedrock_usage = monitor.get_bedrock_usage()
    
    return {
        'costs': costs,
        'alerts': alerts,
        'bedrock_usage': bedrock_usage
    }