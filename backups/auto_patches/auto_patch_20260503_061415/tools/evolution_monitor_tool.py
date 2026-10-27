"""
ULTRON Agent Evolution Monitoring Tool
Real-time monitoring and reporting of self-evolution metrics
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from utils.evolution_engine import get_evolution_engine
from utils.cache_manager import get_cache_manager
from utils.ultron_logger import get_logger

logger = get_logger("evolution_tool")


class EvolutionMonitorTool:
    """
    Tool for monitoring and managing ULTRON's self-evolution process.
    Provides real-time insights into code improvements and system evolution.
    """
    
    name = "Evolution Monitor"
    description = "Monitor ULTRON's self-improvement and evolution metrics"
    
    def __init__(self):
        self.evolution_engine = get_evolution_engine()
        self.cache_manager = get_cache_manager()
        logger.info("Evolution Monitor Tool initialized")
    
    def match(self, command: str) -> bool:
        """Check if command matches this tool"""
        keywords = [
            'evolution', 'evolve', 'improve', 'metrics', 
            'quality', 'performance', 'progress', 'report'
        ]
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in keywords)
    
    def execute(self, command: str) -> str:
        """Execute evolution monitoring command"""
        command_lower = command.lower()
        
        try:
            if 'status' in command_lower or 'summary' in command_lower:
                return self._get_evolution_status()
            
            elif 'report' in command_lower:
                return self._generate_report()
            
            elif 'suggest' in command_lower or 'improve' in command_lower:
                return self._get_improvement_suggestions()
            
            elif 'metrics' in command_lower or 'quality' in command_lower:
                return self._get_code_metrics()
            
            elif 'cache' in command_lower:
                return self._get_cache_stats()
            
            else:
                return self._get_evolution_status()
        
        except Exception as e:
            logger.error(f"Evolution monitor error: {e}")
            return f"Error monitoring evolution: {str(e)}"
    
    def _get_evolution_status(self) -> str:
        """Get current evolution status"""
        try:
            summary = self.evolution_engine.get_evolution_summary(days=7)
            
            status_report = f"""
╔══════════════════════════════════════════════════════════╗
║           ULTRON EVOLUTION STATUS REPORT                 ║
╚══════════════════════════════════════════════════════════╝

📊 Evolution Cycle: #{summary['cycle_number']}
⏱️  Analysis Period: {summary['days_analyzed']} days
📝 Total Evolution Events: {summary['total_events']}

🎯 Average Impact Score: {summary['avg_impact_score']:.2%}
🔧 Most Active Component: {summary['most_active_component']}
⚡ Dominant Activity: {summary['dominant_event_type']}

System Status: ✅ EVOLVING
"""
            
            return status_report.strip()
        
        except Exception as e:
            logger.error(f"Error getting evolution status: {e}")
            return f"Error retrieving status: {str(e)}"
    
    def _generate_report(self) -> str:
        """Generate comprehensive evolution report"""
        try:
            report = self.evolution_engine.generate_evolution_report(days=7)
            
            report_text = f"""
╔══════════════════════════════════════════════════════════╗
║        ULTRON COMPREHENSIVE EVOLUTION REPORT             ║
╚══════════════════════════════════════════════════════════╝

📋 Report ID: {report.report_id}
📅 Generated: {datetime.fromisoformat(report.generated_at).strftime('%Y-%m-%d %H:%M:%S')}
🔄 Cycle Number: {report.cycle_number}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EVOLUTION METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Events: {report.total_events}

Event Breakdown:
"""
            
            for event_type, count in sorted(report.events_by_type.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / report.total_events * 100) if report.total_events > 0 else 0
                report_text += f"  • {event_type.upper():<12}: {count:3d} ({percentage:5.1f}%)\n"
            
            report_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPROVEMENT METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Efficiency Gain: {report.efficiency_gain:+.2%}
Code Quality Improvement: {report.code_quality_improvement:+.2%}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUGGESTED NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            for i, suggestion in enumerate(report.suggested_improvements, 1):
                report_text += f"{i}. {suggestion}\n"
            
            report_text += "\n✅ Evolution proceeding optimally"
            
            return report_text.strip()
        
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return f"Error generating report: {str(e)}"
    
    def _get_improvement_suggestions(self) -> str:
        """Get prioritized improvement suggestions"""
        try:
            suggestions = self.evolution_engine.suggest_next_improvements(limit=5)
            
            if not suggestions:
                return "✅ No critical improvements needed. System is well-maintained."
            
            suggestions_text = f"""
╔══════════════════════════════════════════════════════════╗
║        ULTRON IMPROVEMENT SUGGESTIONS                    ║
╚══════════════════════════════════════════════════════════╝

Top {len(suggestions)} Priority Improvements:

"""
            
            priority_icons = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
            type_icons = {
                'refactor': '🔧',
                'optimize': '⚡',
                'document': '📝',
                'enhance': '✨',
                'extend': '🚀'
            }
            
            for i, suggestion in enumerate(suggestions, 1):
                priority_icon = priority_icons.get(suggestion['priority'], '⚪')
                type_icon = type_icons.get(suggestion['type'], '🔹')
                
                suggestions_text += f"""
{i}. {priority_icon} Priority: {suggestion['priority'].upper()}
   {type_icon} Type: {suggestion['type'].upper()}
   📁 Target: {suggestion['target']}
   💡 Reason: {suggestion['reason']}
   📊 Impact: {suggestion['estimated_impact']:.0%}
"""
            
            return suggestions_text.strip()
        
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return f"Error retrieving suggestions: {str(e)}"
    
    def _get_code_metrics(self) -> str:
        """Get codebase quality metrics"""
        try:
            metrics = self.evolution_engine.scan_codebase_metrics()
            
            if not metrics:
                return "No metrics available. Run a codebase scan first."
            
            # Calculate aggregate metrics
            total_loc = sum(m.lines_of_code for m in metrics.values())
            total_comments = sum(m.comment_lines for m in metrics.values())
            avg_maintainability = sum(m.maintainability_index for m in metrics.values()) / len(metrics)
            avg_complexity = sum(m.complexity_score for m in metrics.values()) / len(metrics)
            
            # Find best and worst files
            best_file = max(metrics.items(), key=lambda x: x[1].maintainability_index)
            worst_file = min(metrics.items(), key=lambda x: x[1].maintainability_index)
            
            metrics_text = f"""
╔══════════════════════════════════════════════════════════╗
║          ULTRON CODE QUALITY METRICS                     ║
╚══════════════════════════════════════════════════════════╝

📊 CODEBASE OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Files Analyzed: {len(metrics)}
Total Lines of Code: {total_loc:,}
Total Comment Lines: {total_comments:,}
Comment Ratio: {(total_comments / (total_loc + total_comments) * 100 if total_loc > 0 else 0):.1f}%

📈 QUALITY METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average Maintainability Index: {avg_maintainability:.1f}/100
Average Complexity Score: {avg_complexity:.1f}

🏆 BEST MAINTAINED FILE
{best_file[0]}
Maintainability: {best_file[1].maintainability_index:.1f}/100

⚠️  NEEDS ATTENTION
{worst_file[0]}
Maintainability: {worst_file[1].maintainability_index:.1f}/100

Overall Code Health: {'🟢 Excellent' if avg_maintainability > 80 else '🟡 Good' if avg_maintainability > 60 else '🔴 Needs Improvement'}
"""
            
            return metrics_text.strip()
        
        except Exception as e:
            logger.error(f"Error getting code metrics: {e}")
            return f"Error retrieving metrics: {str(e)}"
    
    def _get_cache_stats(self) -> str:
        """Get cache performance statistics"""
        try:
            stats = self.cache_manager.get_stats()
            
            cache_text = f"""
╔══════════════════════════════════════════════════════════╗
║          ULTRON CACHE PERFORMANCE STATS                  ║
╚══════════════════════════════════════════════════════════╝

📊 CACHE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hit Rate: {stats['hit_rate']}
Total Hits: {stats['hits']:,}
Total Misses: {stats['misses']:,}

💾 STORAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cached Entries: {stats['entries']:,}
Cache Size: {stats['size_mb']} MB
Redis Connected: {'✅ Yes' if stats['redis_connected'] else '❌ No (SQLite fallback)'}

⚡ OPERATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sets: {stats['sets']:,}
Deletes: {stats['deletes']:,}
Evictions: {stats['evictions']:,}

Performance Status: {'🟢 Optimal' if float(stats['hit_rate'].strip('%')) > 60 else '🟡 Moderate' if float(stats['hit_rate'].strip('%')) > 30 else '🔴 Needs Improvement'}
"""
            
            return cache_text.strip()
        
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return f"Error retrieving cache stats: {str(e)}"
    
    @classmethod
    def schema(cls):
        """Return tool schema for AI integration"""
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Evolution monitoring command (status, report, suggest, metrics, cache)"
                }
            }
        }


# Export for tool discovery
__all__ = ['EvolutionMonitorTool']
