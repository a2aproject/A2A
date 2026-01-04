"""
Base Agent Framework implementing A2A Protocol
"""
import uuid
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json


class TaskStatus(Enum):
    """Task lifecycle states per A2A specification"""
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    REJECTED = "rejected"
    AUTH_REQUIRED = "auth-required"


class MessageRole(Enum):
    """Message role types"""
    USER = "user"
    AGENT = "agent"


@dataclass
class Part:
    """Base class for message parts"""
    pass


@dataclass
class TextPart(Part):
    """Text content part"""
    text: str
    type: str = "text"


@dataclass
class DataPart(Part):
    """Structured data part"""
    data: Dict[str, Any]
    mimeType: str = "application/json"
    type: str = "data"


@dataclass
class FilePart(Part):
    """File content part"""
    uri: Optional[str] = None
    data: Optional[str] = None  # base64 encoded
    mimeType: str = "application/octet-stream"
    type: str = "file"


@dataclass
class Message:
    """A2A Protocol Message"""
    role: MessageRole
    parts: List[Part]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Artifact:
    """Agent output/result"""
    parts: List[Part]
    name: Optional[str] = None
    description: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class AgentSkill:
    """Agent capability definition"""
    id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class AgentCard:
    """Agent metadata and capabilities"""
    name: str
    description: str
    version: str
    url: str
    skills: List[AgentSkill]
    defaultInputModes: List[str] = field(default_factory=lambda: ["text/plain"])
    defaultOutputModes: List[str] = field(default_factory=lambda: ["text/plain"])

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "url": self.url,
            "skills": [
                {
                    "id": skill.id,
                    "name": skill.name,
                    "description": skill.description,
                    "tags": skill.tags,
                    "examples": skill.examples
                }
                for skill in self.skills
            ],
            "defaultInputModes": self.defaultInputModes,
            "defaultOutputModes": self.defaultOutputModes
        }


@dataclass
class Task:
    """Stateful unit of work"""
    id: str
    status: TaskStatus
    messages: List[Message]
    artifacts: List[Artifact] = field(default_factory=list)
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    context_id: Optional[str] = None


class BaseAgent:
    """Base agent implementing A2A Protocol"""

    def __init__(self, name: str, description: str, version: str = "1.0.0"):
        self.name = name
        self.description = description
        self.version = version
        self.tasks: Dict[str, Task] = {}
        self.skills: List[AgentSkill] = []

    def add_skill(self, skill: AgentSkill):
        """Register a skill with this agent"""
        self.skills.append(skill)

    def get_agent_card(self) -> AgentCard:
        """Get agent metadata"""
        return AgentCard(
            name=self.name,
            description=self.description,
            version=self.version,
            url=f"http://localhost:8000/{self.name.lower().replace(' ', '-')}",
            skills=self.skills
        )

    def create_task(self, messages: List[Message], context_id: Optional[str] = None) -> Task:
        """Create a new task"""
        task = Task(
            id=str(uuid.uuid4()),
            status=TaskStatus.SUBMITTED,
            messages=messages,
            context_id=context_id
        )
        self.tasks[task.id] = task
        return task

    def update_task_status(self, task_id: str, status: TaskStatus, error: Optional[str] = None):
        """Update task status"""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            self.tasks[task_id].updated_at = datetime.now()
            if error:
                self.tasks[task_id].error = error

    def add_artifact(self, task_id: str, artifact: Artifact):
        """Add artifact to task"""
        if task_id in self.tasks:
            self.tasks[task_id].artifacts.append(artifact)
            self.tasks[task_id].updated_at = datetime.now()

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve task by ID"""
        return self.tasks.get(task_id)

    async def process_message(self, messages: List[Message]) -> Task:
        """Process incoming messages - to be overridden by subclasses"""
        raise NotImplementedError("Subclasses must implement process_message")

    def __repr__(self):
        return f"<{self.__class__.__name__} name='{self.name}' skills={len(self.skills)}>"


class AgentRegistry:
    """Central registry for managing multiple agents"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent.name] = agent
        print(f"✓ Registered agent: {agent.name}")

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return self.agents.get(name)

    def list_agents(self) -> List[str]:
        """List all registered agents"""
        return list(self.agents.keys())

    def find_agent_by_skill(self, skill_id: str) -> Optional[BaseAgent]:
        """Find agent that has a specific skill"""
        for agent in self.agents.values():
            for skill in agent.skills:
                if skill.id == skill_id:
                    return agent
        return None

    def get_all_skills(self) -> Dict[str, List[AgentSkill]]:
        """Get all skills across all agents"""
        skills_map = {}
        for agent in self.agents.values():
            skills_map[agent.name] = agent.skills
        return skills_map
