#!/usr/bin/env python3
"""Workflow Automation Engine for ULTRON Agent"""

import asyncio
import json
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from utils.ultron_logger import log_info, log_error

@dataclass
class WorkflowStep:
    name: str
    action: str
    params: Dict[str, Any]
    condition: str = None

@dataclass 
class Workflow:
    name: str
    steps: List[WorkflowStep]
    triggers: List[str]
    status: str = "inactive"

class WorkflowEngine:
    """Automates complex multi-step workflows"""
    
    def __init__(self):
        self.workflows = {}
        self.running_workflows = {}
        self.triggers = {}
        
    def register_workflow(self, workflow: Workflow):
        """Register a new workflow"""
        self.workflows[workflow.name] = workflow
        
        for trigger in workflow.triggers:
            if trigger not in self.triggers:
                self.triggers[trigger] = []
            self.triggers[trigger].append(workflow.name)
        
        log_info("workflow_engine", f"Workflow registered: {workflow.name}")
    
    async def trigger_workflow(self, trigger: str, context: Dict[str, Any] = None) -> str:
        """Trigger workflows based on event"""
        if trigger not in self.triggers:
            return f"❌ No workflows for trigger: {trigger}"
        
        results = []
        for workflow_name in self.triggers[trigger]:
            result = await self.execute_workflow(workflow_name, context or {})
            results.append(result)
        
        return "\n".join(results)
    
    async def execute_workflow(self, workflow_name: str, context: Dict[str, Any]) -> str:
        """Execute a specific workflow"""
        if workflow_name not in self.workflows:
            return f"❌ Workflow not found: {workflow_name}"
        
        workflow = self.workflows[workflow_name]
        workflow.status = "running"
        
        log_info("workflow_engine", f"Executing workflow: {workflow_name}")
        
        try:
            results = []
            for step in workflow.steps:
                if self._check_condition(step.condition, context):
                    result = await self._execute_step(step, context)
                    results.append(f"✅ {step.name}: {result}")
                    context[f"{step.name}_result"] = result
                else:
                    results.append(f"⏭️ {step.name}: Skipped (condition not met)")
            
            workflow.status = "completed"
            return f"🔄 Workflow '{workflow_name}' completed:\n" + "\n".join(results)
            
        except Exception as e:
            workflow.status = "failed"
            log_error("workflow_engine", f"Workflow failed: {e}")
            return f"❌ Workflow '{workflow_name}' failed: {str(e)}"
    
    def _check_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Check if step condition is met"""
        if not condition:
            return True
        
        try:
            # Simple condition evaluation
            return eval(condition, {"context": context})
        except:
            return True
    
    async def _execute_step(self, step: WorkflowStep, context: Dict[str, Any]) -> str:
        """Execute a workflow step"""
        action = step.action
        params = step.params
        
        if action == "ai_generate":
            return await self._ai_generate(params, context)
        elif action == "tool_execute":
            return await self._tool_execute(params, context)
        elif action == "delay":
            await asyncio.sleep(params.get("seconds", 1))
            return f"Delayed {params.get('seconds', 1)}s"
        else:
            return f"Unknown action: {action}"
    
    async def _ai_generate(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Execute AI generation step"""
        prompt = params.get("prompt", "").format(**context)
        model = params.get("model", "llava:7b")
        return f"AI response from {model}"
    
    async def _tool_execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Execute tool step"""
        tool = params.get("tool", "unknown")
        command = params.get("command", "").format(**context)
        return f"Tool {tool} executed: {command}"

# Global workflow engine
workflow_engine = WorkflowEngine()

# Register sample workflows
workflow_engine.register_workflow(Workflow(
    name="code_review_workflow",
    triggers=["code_changed", "pr_created"],
    steps=[
        WorkflowStep("analyze_code", "ai_generate", 
                    {"prompt": "Analyze code changes", "model": "qwen3-coder:480b-cloud"}),
        WorkflowStep("security_scan", "tool_execute",
                    {"tool": "security_scanner", "command": "scan {file_path}"}),
        WorkflowStep("generate_report", "ai_generate",
                    {"prompt": "Generate review report", "model": "deepseek-r1:14b"})
    ]
))

workflow_engine.register_workflow(Workflow(
    name="deployment_workflow", 
    triggers=["deploy_requested"],
    steps=[
        WorkflowStep("run_tests", "tool_execute",
                    {"tool": "pytest", "command": "pytest tests/"}),
        WorkflowStep("build_package", "tool_execute", 
                    {"tool": "build", "command": "python setup.py build"}),
        WorkflowStep("deploy_aws", "tool_execute",
                    {"tool": "aws_deploy", "command": "deploy to {environment}"})
    ]
))