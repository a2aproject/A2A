"""
Specialized Agent Implementations

Collection of specialized agents demonstrating various capabilities:
- Orchestrator: Co-scientist mode coordination
- Project Manager: Intelligent task routing
- Deep Researcher: Advanced research and analysis
- Dataset Agent: HuggingFace dataset integration
"""

from .orchestrator_agent import OrchestratorAgent
from .project_manager_agent import ProjectManagerAgent
from .researcher_agent import DeepResearcherAgent
from .dataset_agent import DatasetAgent

__all__ = [
    'OrchestratorAgent',
    'ProjectManagerAgent',
    'DeepResearcherAgent',
    'DatasetAgent'
]
