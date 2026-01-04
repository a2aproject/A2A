# Multi-Agent Orchestrator System - A2A Protocol Reference Implementation

A comprehensive reference implementation demonstrating the Agent2Agent (A2A) Protocol with intelligent multi-agent orchestration, task routing, and specialized capabilities including Hugging Face dataset integration.

## 🎯 Overview

This implementation showcases a production-ready multi-agent system with:

- **Orchestrator Agent** - Co-scientist mode for complex workflow coordination
- **Project Manager Agent** - Intelligent task routing and agent selection
- **Deep Researcher Agent** - Advanced research and knowledge synthesis
- **Dataset Ingestion Agent** - Seamless Hugging Face dataset integration

All agents follow the [A2A Protocol specification](../specification.md) for standardized agent-to-agent communication.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Orchestrator Agent                          │
│                  (Co-Scientist Mode)                            │
│  • Strategic planning                                           │
│  • Workflow coordination                                        │
│  • Knowledge integration                                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Project Manager Agent                          │
│                 (Task Router)                                   │
│  • Task analysis                                                │
│  • Agent selection                                              │
│  • Workload optimization                                        │
└────────┬────────────────────────────┬───────────────────────────┘
         │                            │
         ▼                            ▼
┌──────────────────────┐    ┌──────────────────────────┐
│  Deep Researcher     │    │  Dataset Ingestion       │
│  Agent               │    │  Agent                   │
│                      │    │                          │
│  • Deep analysis     │    │  • HuggingFace loader    │
│  • Literature review │    │  • Dataset analysis      │
│  • Synthesis         │    │  • Metadata extraction   │
│  • Hypotheses        │    │  • GLUE support          │
└──────────────────────┘    └──────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/a2aproject/A2A.git
cd A2A/reference-implementation

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
import asyncio
from core.a2a_base import AgentRegistry, Message, TextPart, MessageRole
from agents.orchestrator_agent import OrchestratorAgent
from agents.project_manager_agent import ProjectManagerAgent
from agents.dataset_agent import DatasetAgent
from agents.researcher_agent import DeepResearcherAgent

async def main():
    # Create agent registry
    registry = AgentRegistry()

    # Initialize specialized agents
    dataset_agent = DatasetAgent()
    researcher_agent = DeepResearcherAgent()
    registry.register(dataset_agent)
    registry.register(researcher_agent)

    # Initialize project manager
    pm_agent = ProjectManagerAgent(registry)
    registry.register(pm_agent)

    # Initialize orchestrator
    orchestrator = OrchestratorAgent(registry)
    orchestrator.set_project_manager(pm_agent)

    # Create a task
    messages = [
        Message(
            role=MessageRole.USER,
            parts=[TextPart(text="Load GLUE cola dataset")]
        )
    ]

    # Execute through orchestrator
    task = await orchestrator.process_message(messages)

    # Access results
    for artifact in task.artifacts:
        for part in artifact.parts:
            if hasattr(part, 'text'):
                print(part.text)

asyncio.run(main())
```

### Run the Demo

```bash
cd examples
python demo.py
```

The demo showcases:
1. Dataset loading with HuggingFace integration
2. Deep research capabilities
3. Intelligent task routing
4. Complex workflow orchestration
5. Agent metadata (Agent Cards)
6. End-to-end workflows

## 📚 Components

### Core Framework (`core/a2a_base.py`)

Base classes implementing the A2A Protocol:

- `BaseAgent` - Foundation for all agents
- `AgentRegistry` - Central agent management
- `Message`, `Task`, `Artifact` - A2A protocol data structures
- `AgentCard`, `AgentSkill` - Agent metadata

### Orchestrator Agent (`agents/orchestrator_agent.py`)

**Co-scientist mode orchestrator** for complex multi-agent workflows:

**Skills:**
- `collaborative_research` - Multi-agent research coordination
- `strategic_planning` - High-level task planning
- `knowledge_integration` - Cross-agent insight synthesis
- `adaptive_delegation` - Intelligent task delegation

**Modes:**
- Single Task - Simple delegation
- Multi-Task - Coordinated parallel execution
- Workflow - Complex multi-phase pipelines

### Project Manager Agent (`agents/project_manager_agent.py`)

**Intelligent task router** that analyzes requirements and selects optimal agents:

**Skills:**
- `task_routing` - Analyze and route tasks
- `workflow_coordination` - Manage dependencies
- `agent_selection` - Optimal agent matching

**Features:**
- Keyword-based task analysis
- Skill overlap scoring
- Confidence-based selection
- Routing history tracking

### Deep Researcher Agent (`agents/researcher_agent.py`)

**Advanced research specialist** for analysis and knowledge synthesis:

**Skills:**
- `deep_analysis` - Multi-dimensional investigation
- `literature_review` - Systematic paper review
- `knowledge_synthesis` - Information integration
- `hypothesis_generation` - Experimental design

**Research Types:**
- Analysis - Technical and performance evaluation
- Literature Review - Academic paper synthesis
- Synthesis - Cross-source integration
- Hypothesis - Research design

### Dataset Ingestion Agent (`agents/dataset_agent.py`)

**HuggingFace dataset specialist** for easy data loading:

**Skills:**
- `load_dataset` - Load from HuggingFace hub
- `analyze_dataset` - Structure and schema analysis
- `dataset_info` - Metadata retrieval

**Supported Datasets:**
- GLUE benchmark (cola, sst2, mrpc, qqp, stsb, mnli, qnli, rte, wnli, ax)
- Custom dataset configurations
- Extensible for any HuggingFace dataset

## 💡 Usage Examples

### Loading a Dataset

```python
messages = [
    Message(
        role=MessageRole.USER,
        parts=[TextPart(text="Load GLUE mnli dataset")]
    )
]

task = await dataset_agent.process_message(messages)
```

### Deep Research

```python
messages = [
    Message(
        role=MessageRole.USER,
        parts=[TextPart(text="Perform deep analysis on transformer architectures")]
    )
]

task = await researcher_agent.process_message(messages)
```

### Automatic Task Routing

```python
# Project Manager automatically routes to the right agent
messages = [
    Message(
        role=MessageRole.USER,
        parts=[TextPart(text="Research the GLUE benchmark and load the cola dataset")]
    )
]

task = await pm_agent.process_message(messages)
```

### Complex Orchestration

```python
# Orchestrator coordinates multi-agent workflow
messages = [
    Message(
        role=MessageRole.USER,
        parts=[TextPart(
            text="Load GLUE datasets and synthesize insights about evaluation methodologies"
        )]
    )
]

task = await orchestrator.process_message(messages)
```

## 🔧 Configuration

### Adding New Agents

1. Extend `BaseAgent`:

```python
from core.a2a_base import BaseAgent, AgentSkill

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="My Custom Agent",
            description="Does amazing things",
            version="1.0.0"
        )

        # Register skills
        self.add_skill(AgentSkill(
            id="my_skill",
            name="My Skill",
            description="What this skill does",
            tags=["custom", "amazing"],
            examples=["Example usage 1", "Example usage 2"]
        ))

    async def process_message(self, messages):
        # Your implementation
        pass
```

2. Register with the system:

```python
registry.register(MyCustomAgent())
```

### Customizing Task Routing

Modify `ProjectManagerAgent._analyze_task_requirements()` to add custom routing logic:

```python
def _analyze_task_requirements(self, message_text: str):
    analysis = super()._analyze_task_requirements(message_text)

    # Add custom logic
    if "my_keyword" in message_text.lower():
        analysis["agent_preferences"].append("My Custom Agent")

    return analysis
```

## 🧪 Testing

Run the comprehensive demo:

```bash
python examples/demo.py
```

This runs 6 different demos showcasing all capabilities.

## 📊 A2A Protocol Compliance

This implementation follows the A2A Protocol specification:

✅ **Agent Cards** - Metadata exposure via `get_agent_card()`
✅ **Skills** - Capability declaration with `AgentSkill`
✅ **Tasks** - Stateful execution with lifecycle management
✅ **Messages** - Role-based communication (user/agent)
✅ **Artifacts** - Structured output with Parts (text/data/file)
✅ **Status Management** - Complete task lifecycle support

### Example Agent Card

```json
{
  "name": "Dataset Ingestion Agent",
  "description": "Specialized agent for loading and analyzing Hugging Face datasets",
  "version": "1.0.0",
  "url": "http://localhost:8000/dataset-ingestion-agent",
  "skills": [
    {
      "id": "load_dataset",
      "name": "Load Dataset",
      "description": "Load datasets from Hugging Face hub",
      "tags": ["data", "huggingface", "loading"],
      "examples": ["Load GLUE cola dataset"]
    }
  ]
}
```

## 🎓 Learning Resources

- [A2A Protocol Specification](../docs/specification.md)
- [Agent Architecture Guide](./docs/architecture.md)
- [Best Practices](./docs/best-practices.md)
- [API Reference](./docs/api-reference.md)

## 🤝 Contributing

This is a reference implementation. Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Add your agent or enhancement
4. Submit a pull request

## 📄 License

Apache 2.0 - See [LICENSE](../LICENSE) for details

## 🔗 Links

- [A2A Protocol Repository](https://github.com/a2aproject/A2A)
- [A2A Python SDK](https://github.com/a2aproject/a2a-python)
- [A2A JavaScript SDK](https://github.com/a2aproject/a2a-js)
- [HuggingFace Datasets](https://huggingface.co/docs/datasets)

## 💬 Support

- GitHub Issues: [Report bugs or request features](https://github.com/a2aproject/A2A/issues)
- Discussions: [Join the community](https://github.com/a2aproject/A2A/discussions)

---

**Built with ❤️ using the Agent2Agent Protocol**
