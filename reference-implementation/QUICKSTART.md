# Quick Start Guide - Multi-Agent Orchestrator System

Get started with the A2A multi-agent system in 5 minutes!

## 🚀 Installation

```bash
cd reference-implementation
pip install -r requirements.txt
```

## 🎯 Run Your First Agent in 30 Seconds

### Example 1: Load a HuggingFace Dataset

```python
import asyncio
from core.a2a_base import Message, TextPart, MessageRole
from agents.dataset_agent import DatasetAgent

async def load_dataset():
    # Create dataset agent
    agent = DatasetAgent()

    # Create request
    messages = [
        Message(
            role=MessageRole.USER,
            parts=[TextPart(text="Load GLUE cola dataset")]
        )
    ]

    # Process
    task = await agent.process_message(messages)

    # Show results
    for artifact in task.artifacts:
        for part in artifact.parts:
            if hasattr(part, 'text'):
                print(part.text)

asyncio.run(load_dataset())
```

**Output:**
```
✓ Dataset Loaded Successfully

📊 Dataset: nyu-mll/glue
⚙️  Configuration: cola
📁 Splits: train, validation, test

📋 Features:
  - sentence: string
  - label: int (0-1)

💻 Loading Code:
```python
from datasets import load_dataset
ds = load_dataset("nyu-mll/glue", "cola")
```

---

### Example 2: Run Deep Research

```python
import asyncio
from core.a2a_base import Message, TextPart, MessageRole
from agents.researcher_agent import DeepResearcherAgent

async def do_research():
    agent = DeepResearcherAgent()

    messages = [
        Message(
            role=MessageRole.USER,
            parts=[TextPart(text="Analyze transformer architectures")]
        )
    ]

    task = await agent.process_message(messages)

    for artifact in task.artifacts:
        for part in artifact.parts:
            if hasattr(part, 'text'):
                print(part.text)

asyncio.run(do_research())
```

---

### Example 3: Complete Multi-Agent System

```python
import asyncio
from core.a2a_base import AgentRegistry, Message, TextPart, MessageRole
from agents import (
    OrchestratorAgent,
    ProjectManagerAgent,
    DatasetAgent,
    DeepResearcherAgent
)

async def main():
    # 1. Create registry
    registry = AgentRegistry()

    # 2. Register specialized agents
    dataset_agent = DatasetAgent()
    researcher_agent = DeepResearcherAgent()
    registry.register(dataset_agent)
    registry.register(researcher_agent)

    # 3. Add project manager
    pm = ProjectManagerAgent(registry)
    registry.register(pm)

    # 4. Add orchestrator
    orchestrator = OrchestratorAgent(registry)
    orchestrator.set_project_manager(pm)

    # 5. Send request - it auto-routes to the right agent!
    messages = [
        Message(
            role=MessageRole.USER,
            parts=[TextPart(text="Load the GLUE cola dataset")]
        )
    ]

    task = await orchestrator.process_message(messages)

    # 6. Get results
    print(f"Status: {task.status.value}")
    print(f"Artifacts: {len(task.artifacts)}")

asyncio.run(main())
```

---

## 🎬 Run the Full Demo

```bash
cd examples
python demo.py
```

This runs 6 comprehensive demos:
1. **Dataset Loading** - HuggingFace integration
2. **Deep Research** - Advanced analysis
3. **Task Routing** - Intelligent agent selection
4. **Orchestration** - Complex workflows
5. **Agent Cards** - A2A metadata
6. **Complete Workflow** - End-to-end system

---

## 🎓 Understanding the System

### The Four Agent Types

```
┌─────────────────────────────────────────────────┐
│ 1. ORCHESTRATOR (Co-Scientist)                 │
│    • Coordinates everything                     │
│    • Manages complex workflows                  │
│    • Synthesizes results                        │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 2. PROJECT MANAGER (Task Router)               │
│    • Analyzes incoming tasks                    │
│    • Selects best agent                         │
│    • Routes automatically                       │
└────────┬──────────────────┬─────────────────────┘
         │                  │
         ▼                  ▼
┌──────────────────┐  ┌──────────────────┐
│ 3. RESEARCHER    │  │ 4. DATASET       │
│    • Analysis    │  │    • Load data   │
│    • Synthesis   │  │    • Analyze     │
│    • Research    │  │    • Metadata    │
└──────────────────┘  └──────────────────┘
```

### When to Use Each Agent

| Agent | Use When |
|-------|----------|
| **Dataset Agent** | Loading HuggingFace datasets, data analysis |
| **Researcher Agent** | Deep analysis, literature review, synthesis |
| **Project Manager** | You want automatic routing |
| **Orchestrator** | Complex multi-step workflows, synthesis needed |

---

## 💡 Common Patterns

### Pattern 1: Direct Agent Use

When you know exactly which agent you need:

```python
agent = DatasetAgent()
task = await agent.process_message(messages)
```

### Pattern 2: Auto-Routing

When you want the system to choose:

```python
pm = ProjectManagerAgent(registry)
task = await pm.process_message(messages)
# Automatically routes to best agent!
```

### Pattern 3: Orchestrated Workflow

For complex multi-step tasks:

```python
orchestrator = OrchestratorAgent(registry)
orchestrator.set_project_manager(pm)
task = await orchestrator.process_message(messages)
# Coordinates multiple agents, synthesizes results
```

---

## 🔧 Customization

### Add Your Own Agent

```python
from core.a2a_base import BaseAgent, AgentSkill, Message, Task, TaskStatus

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="My Agent",
            description="What it does",
            version="1.0.0"
        )

        self.add_skill(AgentSkill(
            id="my_skill",
            name="My Skill",
            description="Skill description",
            tags=["custom"],
            examples=["Example usage"]
        ))

    async def process_message(self, messages: List[Message]) -> Task:
        task = self.create_task(messages)
        self.update_task_status(task.id, TaskStatus.WORKING)

        # Your logic here

        self.update_task_status(task.id, TaskStatus.COMPLETED)
        return self.get_task(task.id)

# Register it
registry.register(MyAgent())
```

---

## 📊 Access Results

### Get Task Status

```python
task = await agent.process_message(messages)
print(task.status.value)  # "completed", "failed", etc.
```

### Get Artifacts

```python
for artifact in task.artifacts:
    print(f"Artifact: {artifact.name}")
    for part in artifact.parts:
        if hasattr(part, 'text'):
            print(part.text)
        elif hasattr(part, 'data'):
            print(part.data)  # JSON data
```

### Get Agent Card (Metadata)

```python
agent = DatasetAgent()
card = agent.get_agent_card()
print(f"Name: {card.name}")
print(f"Skills: {[s.name for s in card.skills]}")
```

---

## 🐛 Troubleshooting

### "No user message found"

Make sure you're creating messages correctly:

```python
messages = [
    Message(
        role=MessageRole.USER,  # ✓ Correct
        parts=[TextPart(text="Your request")]
    )
]
```

### "Project manager not configured"

Set the project manager before using orchestrator:

```python
orchestrator.set_project_manager(pm)  # ✓ Don't forget this!
```

### Import Errors

Make sure you're in the right directory:

```bash
cd reference-implementation
python your_script.py
```

---

## 📚 Next Steps

- Read the [full README](./README.md)
- Check out [demo.py](./examples/demo.py) for comprehensive examples
- Learn about the [A2A Protocol](../docs/specification.md)
- Build your own custom agent!

---

## 💬 Need Help?

- GitHub Issues: [Report bugs](https://github.com/a2aproject/A2A/issues)
- Discussions: [Ask questions](https://github.com/a2aproject/A2A/discussions)

**Happy Building! 🚀**
