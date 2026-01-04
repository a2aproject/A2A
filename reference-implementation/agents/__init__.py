"""
Specialized Agent Implementations

Collection of specialized agents demonstrating various capabilities:
- Orchestrator: Co-scientist mode coordination
- Project Manager: Intelligent task routing
- Deep Researcher: Advanced research and analysis
- Dataset Agent: HuggingFace dataset integration
- Grant Writing Agent: NIH grant application expert
- VPN Agent: Outline SDK and network circumvention specialist
- Bloom Agent: LLM behavior evaluation expert
"""

from .orchestrator_agent import OrchestratorAgent
from .project_manager_agent import ProjectManagerAgent
from .researcher_agent import DeepResearcherAgent
from .dataset_agent import DatasetAgent
from .grant_writing_agent import GrantWritingAgent
from .vpn_agent import VPNAgent
from .bloom_agent import BloomAgent

__all__ = [
    'OrchestratorAgent',
    'ProjectManagerAgent',
    'DeepResearcherAgent',
    'DatasetAgent',
    'GrantWritingAgent',
    'VPNAgent',
    'BloomAgent'
]
