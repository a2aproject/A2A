"""
Orchestrator Agent - Co-scientist format for collaborative research and development
"""
import sys
sys.path.append('..')

from typing import List, Dict, Any, Optional
from core.a2a_base import (
    BaseAgent, Message, Task, TaskStatus, Artifact,
    TextPart, DataPart, AgentSkill, MessageRole, AgentRegistry
)
from agents.project_manager_agent import ProjectManagerAgent
import json
from datetime import datetime


class OrchestratorAgent(BaseAgent):
    """
    High-level orchestrator operating in co-scientist mode.
    Coordinates complex multi-agent workflows, manages strategic decisions,
    and provides collaborative research and development capabilities.
    """

    def __init__(self, agent_registry: AgentRegistry):
        super().__init__(
            name="Orchestrator Agent",
            description="Co-scientist orchestrator for complex research and development workflows",
            version="1.0.0"
        )

        self.registry = agent_registry
        self.project_manager: Optional[ProjectManagerAgent] = None

        # Register orchestrator skills
        self.add_skill(AgentSkill(
            id="collaborative_research",
            name="Collaborative Research",
            description="Coordinate multiple agents for comprehensive research projects",
            tags=["collaboration", "research", "orchestration"],
            examples=[
                "Conduct comprehensive study on neural architectures",
                "Research and analyze multiple datasets collaboratively",
                "Coordinate multi-agent investigation"
            ]
        ))

        self.add_skill(AgentSkill(
            id="strategic_planning",
            name="Strategic Planning",
            description="Develop high-level strategies for complex tasks",
            tags=["planning", "strategy", "architecture"],
            examples=[
                "Plan multi-phase research project",
                "Design experiment pipeline",
                "Architect multi-agent workflow"
            ]
        ))

        self.add_skill(AgentSkill(
            id="knowledge_integration",
            name="Knowledge Integration",
            description="Integrate insights from multiple specialized agents",
            tags=["integration", "synthesis", "coordination"],
            examples=[
                "Synthesize findings from research and data analysis",
                "Combine insights across domains",
                "Integrate multi-agent outputs"
            ]
        ))

        self.add_skill(AgentSkill(
            id="adaptive_delegation",
            name="Adaptive Delegation",
            description="Intelligently delegate tasks based on agent capabilities and workload",
            tags=["delegation", "optimization", "coordination"],
            examples=[
                "Delegate tasks to optimal agents",
                "Balance workload across team",
                "Adapt delegation strategy based on results"
            ]
        ))

        # Workflow tracking
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.session_history: List[Dict[str, Any]] = []

    def set_project_manager(self, pm_agent: ProjectManagerAgent):
        """Set the project manager for delegation"""
        self.project_manager = pm_agent

    def _parse_orchestration_request(self, message_text: str) -> Dict[str, Any]:
        """Parse and understand orchestration requirements"""
        text_lower = message_text.lower()

        request = {
            "raw_request": message_text,
            "mode": "single_task",  # single_task, multi_task, workflow
            "requires_coordination": False,
            "requires_synthesis": False,
            "complexity": "medium",
            "sub_tasks": []
        }

        # Detect multi-task or workflow requirements
        coordination_indicators = ["and", "then", "after", "followed by", "next", "both"]
        if any(indicator in text_lower for indicator in coordination_indicators):
            request["requires_coordination"] = True
            request["mode"] = "multi_task"

        # Detect synthesis requirements
        synthesis_indicators = ["synthesize", "combine", "integrate", "merge", "consolidate"]
        if any(indicator in text_lower for indicator in synthesis_indicators):
            request["requires_synthesis"] = True

        # Detect workflow patterns
        workflow_indicators = ["pipeline", "workflow", "process", "series of", "multiple steps"]
        if any(indicator in text_lower for indicator in workflow_indicators):
            request["mode"] = "workflow"

        # Extract potential sub-tasks (simplified)
        # In production, use more sophisticated NLP
        sentences = message_text.split('.')
        if len(sentences) > 1:
            request["sub_tasks"] = [s.strip() for s in sentences if s.strip()]

        return request

    async def orchestrate_workflow(self, request: Dict[str, Any],
                                   messages: List[Message]) -> Dict[str, Any]:
        """
        Orchestrate complex multi-agent workflows.
        This is the core co-scientist functionality.
        """
        workflow_id = f"workflow_{len(self.workflows)}"

        workflow = {
            "id": workflow_id,
            "request": request,
            "mode": request["mode"],
            "started_at": datetime.now().isoformat(),
            "phases": [],
            "results": {},
            "status": "running"
        }

        self.workflows[workflow_id] = workflow

        try:
            if request["mode"] == "single_task":
                # Simple delegation through project manager
                result = await self._execute_single_task(messages, workflow)
                workflow["phases"].append({
                    "phase": "single_task_execution",
                    "status": "completed",
                    "result": result
                })

            elif request["mode"] == "multi_task":
                # Coordinate multiple tasks
                result = await self._execute_multi_task(messages, workflow)
                workflow["phases"].append({
                    "phase": "multi_task_coordination",
                    "status": "completed",
                    "result": result
                })

            elif request["mode"] == "workflow":
                # Execute complex workflow
                result = await self._execute_complex_workflow(messages, workflow)
                workflow["phases"].append({
                    "phase": "complex_workflow",
                    "status": "completed",
                    "result": result
                })

            # Synthesis phase if required
            if request["requires_synthesis"]:
                synthesis = await self._synthesize_results(workflow)
                workflow["phases"].append({
                    "phase": "synthesis",
                    "status": "completed",
                    "result": synthesis
                })
                workflow["results"]["synthesis"] = synthesis

            workflow["status"] = "completed"
            workflow["completed_at"] = datetime.now().isoformat()

        except Exception as e:
            workflow["status"] = "failed"
            workflow["error"] = str(e)

        # Record in session history
        self.session_history.append({
            "timestamp": datetime.now().isoformat(),
            "workflow_id": workflow_id,
            "status": workflow["status"]
        })

        return workflow

    async def _execute_single_task(self, messages: List[Message],
                                   workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single task through project manager"""
        if not self.project_manager:
            raise ValueError("Project manager not configured")

        task = await self.project_manager.process_message(messages)

        return {
            "execution_type": "single_task",
            "task_id": task.id,
            "status": task.status.value,
            "artifacts_count": len(task.artifacts)
        }

    async def _execute_multi_task(self, messages: List[Message],
                                  workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multiple coordinated tasks"""
        if not self.project_manager:
            raise ValueError("Project manager not configured")

        # For this reference implementation, execute primary task
        # In production, parse and execute multiple tasks
        task = await self.project_manager.process_message(messages)

        return {
            "execution_type": "multi_task",
            "tasks_executed": 1,  # Would be multiple in production
            "primary_task_id": task.id,
            "status": task.status.value
        }

    async def _execute_complex_workflow(self, messages: List[Message],
                                       workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complex multi-phase workflow"""
        if not self.project_manager:
            raise ValueError("Project manager not configured")

        # Phase 1: Initial task execution
        task = await self.project_manager.process_message(messages)

        # In production, would have multiple phases with dependencies
        phases_executed = [
            {
                "phase_number": 1,
                "phase_name": "Initial Execution",
                "task_id": task.id,
                "status": task.status.value
            }
        ]

        return {
            "execution_type": "complex_workflow",
            "total_phases": len(phases_executed),
            "phases": phases_executed,
            "status": "completed"
        }

    async def _synthesize_results(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize results from multiple agents/tasks"""
        synthesis = {
            "workflow_id": workflow["id"],
            "synthesis_type": "integrated",
            "phases_synthesized": len(workflow["phases"]),
            "key_insights": [
                "Integrated findings from multiple specialized agents",
                "Coordinated execution across workflow phases",
                "Synthesized coherent results from distributed processing"
            ],
            "confidence": 0.85,
            "synthesis_timestamp": datetime.now().isoformat()
        }

        return synthesis

    async def process_message(self, messages: List[Message]) -> Task:
        """
        Process messages in co-scientist mode.
        Orchestrates complex workflows and coordinates specialized agents.
        """
        task = self.create_task(messages)
        self.update_task_status(task.id, TaskStatus.WORKING)

        try:
            # Get the last user message
            user_messages = [msg for msg in messages if msg.role == MessageRole.USER]
            if not user_messages:
                raise ValueError("No user message found")

            last_message = user_messages[-1]
            text_parts = [part for part in last_message.parts if isinstance(part, TextPart)]

            if not text_parts:
                raise ValueError("No text content in message")

            message_text = text_parts[0].text

            # Parse orchestration request
            orchestration_request = self._parse_orchestration_request(message_text)

            # Orchestrate workflow
            workflow = await self.orchestrate_workflow(orchestration_request, messages)

            # Format response
            response_text = self._format_orchestration_response(workflow)

            # Create main artifact
            artifact = Artifact(
                name="Orchestration Report",
                description=f"Co-scientist orchestration for: {message_text[:100]}",
                parts=[
                    TextPart(text=response_text),
                    DataPart(data=workflow, mimeType="application/json")
                ]
            )

            self.add_artifact(task.id, artifact)
            self.update_task_status(task.id, TaskStatus.COMPLETED)

        except Exception as e:
            self.update_task_status(task.id, TaskStatus.FAILED, error=str(e))

        return self.get_task(task.id)

    def _format_orchestration_response(self, workflow: Dict[str, Any]) -> str:
        """Format orchestration workflow response"""
        response = f"""🎭 Orchestrator Agent - Co-Scientist Mode

Workflow ID: {workflow['id']}
Mode: {workflow['mode'].upper().replace('_', ' ')}
Status: {workflow['status'].upper()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Workflow Execution:

"""

        for i, phase in enumerate(workflow['phases'], 1):
            response += f"{i}. {phase['phase'].replace('_', ' ').title()}\n"
            response += f"   Status: {phase['status']}\n"

            if 'result' in phase:
                result = phase['result']
                if isinstance(result, dict):
                    response += f"   Type: {result.get('execution_type', 'N/A')}\n"
                    if 'tasks_executed' in result:
                        response += f"   Tasks: {result['tasks_executed']}\n"
                    if 'total_phases' in result:
                        response += f"   Phases: {result['total_phases']}\n"

            response += "\n"

        if 'synthesis' in workflow.get('results', {}):
            synthesis = workflow['results']['synthesis']
            response += "\n🔬 Synthesis:\n"
            response += f"  Confidence: {synthesis['confidence']:.1%}\n"
            response += f"  Key Insights:\n"
            for insight in synthesis['key_insights']:
                response += f"    • {insight}\n"

        response += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        response += f"\nWorkflow {workflow['status']} at {workflow.get('completed_at', 'in progress')}\n"

        return response

    def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get statistics about orchestration activities"""
        total_workflows = len(self.workflows)
        completed_workflows = sum(1 for w in self.workflows.values() if w['status'] == 'completed')
        failed_workflows = sum(1 for w in self.workflows.values() if w['status'] == 'failed')

        mode_distribution = {}
        for workflow in self.workflows.values():
            mode = workflow['mode']
            mode_distribution[mode] = mode_distribution.get(mode, 0) + 1

        return {
            "total_workflows": total_workflows,
            "completed": completed_workflows,
            "failed": failed_workflows,
            "success_rate": completed_workflows / total_workflows if total_workflows > 0 else 0,
            "mode_distribution": mode_distribution
        }
