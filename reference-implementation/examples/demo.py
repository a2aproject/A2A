"""
Demo: Multi-Agent Orchestrator System with Hugging Face Dataset Integration

This demonstrates the complete multi-agent system including:
1. Orchestrator Agent (Co-scientist mode)
2. Project Manager Agent (Task routing)
3. Deep Researcher Agent
4. Dataset Ingestion Agent (Hugging Face)

All agents follow the A2A Protocol specification.
"""
import sys
import asyncio
sys.path.append('..')

from core.a2a_base import (
    AgentRegistry, Message, TextPart, MessageRole
)
from agents.orchestrator_agent import OrchestratorAgent
from agents.project_manager_agent import ProjectManagerAgent
from agents.researcher_agent import DeepResearcherAgent
from agents.dataset_agent import DatasetAgent


def print_separator(title: str = ""):
    """Print a nice separator"""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    else:
        print(f"{'='*80}\n")


async def demo_dataset_loading():
    """Demo 1: Loading Hugging Face datasets"""
    print_separator("Demo 1: Dataset Loading with Dataset Agent")

    # Create registry
    registry = AgentRegistry()

    # Create and register dataset agent
    dataset_agent = DatasetAgent()
    registry.register(dataset_agent)

    # Create messages for dataset loading
    messages = [
        Message(
            role=MessageRole.USER,
            parts=[TextPart(text="Load the GLUE cola dataset")]
        )
    ]

    print("📤 Request: Load the GLUE cola dataset\n")

    # Process message
    task = await dataset_agent.process_message(messages)

    # Display results
    print(f"Task Status: {task.status.value}")
    print(f"Artifacts Generated: {len(task.artifacts)}\n")

    for artifact in task.artifacts:
        for part in artifact.parts:
            if hasattr(part, 'text'):
                print(part.text)

    print_separator()


async def demo_deep_research():
    """Demo 2: Deep research with Researcher Agent"""
    print_separator("Demo 2: Deep Research with Researcher Agent")

    # Create registry
    registry = AgentRegistry()

    # Create and register researcher agent
    researcher_agent = DeepResearcherAgent()
    registry.register(researcher_agent)

    # Create research message
    messages = [
        Message(
            role=MessageRole.USER,
            parts=[TextPart(text="Perform deep analysis on transformer architectures for NLP")]
        )
    ]

    print("📤 Request: Perform deep analysis on transformer architectures for NLP\n")

    # Process message
    task = await researcher_agent.process_message(messages)

    # Display results
    print(f"Task Status: {task.status.value}")
    print(f"Artifacts Generated: {len(task.artifacts)}\n")

    for artifact in task.artifacts:
        for part in artifact.parts:
            if hasattr(part, 'text'):
                print(part.text)

    print_separator()


async def demo_project_manager_routing():
    """Demo 3: Intelligent task routing with Project Manager"""
    print_separator("Demo 3: Task Routing with Project Manager Agent")

    # Create registry
    registry = AgentRegistry()

    # Create and register all specialized agents
    dataset_agent = DatasetAgent()
    researcher_agent = DeepResearcherAgent()
    registry.register(dataset_agent)
    registry.register(researcher_agent)

    # Create project manager
    pm_agent = ProjectManagerAgent(registry)
    registry.register(pm_agent)

    print("Available Agents:")
    for agent_name in registry.list_agents():
        print(f"  • {agent_name}")
    print()

    # Test multiple routing scenarios
    test_requests = [
        "Load the GLUE mnli dataset",
        "Research the latest developments in large language models",
    ]

    for request in test_requests:
        print(f"📤 Request: {request}\n")

        messages = [
            Message(
                role=MessageRole.USER,
                parts=[TextPart(text=request)]
            )
        ]

        # Process through project manager
        task = await pm_agent.process_message(messages)

        print(f"Task Status: {task.status.value}")
        print(f"Artifacts: {len(task.artifacts)}\n")

        # Show first artifact (routing info)
        if task.artifacts:
            first_artifact = task.artifacts[0]
            for part in first_artifact.parts:
                if hasattr(part, 'text'):
                    print(part.text)
                    break

        print_separator()


async def demo_orchestrator_workflow():
    """Demo 4: Complex orchestration with Co-scientist mode"""
    print_separator("Demo 4: Orchestration in Co-Scientist Mode")

    # Create registry
    registry = AgentRegistry()

    # Create and register all agents
    dataset_agent = DatasetAgent()
    researcher_agent = DeepResearcherAgent()
    registry.register(dataset_agent)
    registry.register(researcher_agent)

    # Create project manager
    pm_agent = ProjectManagerAgent(registry)
    registry.register(pm_agent)

    # Create orchestrator
    orchestrator = OrchestratorAgent(registry)
    orchestrator.set_project_manager(pm_agent)
    registry.register(orchestrator)

    print("🎭 Multi-Agent System Ready")
    print(f"Registered Agents: {', '.join(registry.list_agents())}\n")

    # Complex orchestration request
    messages = [
        Message(
            role=MessageRole.USER,
            parts=[TextPart(
                text="Load the GLUE cola dataset and then perform deep analysis on its structure and characteristics"
            )]
        )
    ]

    print("📤 Complex Request:")
    print("   Load the GLUE cola dataset and then perform deep analysis\n")

    # Process through orchestrator
    task = await orchestrator.process_message(messages)

    print(f"Task Status: {task.status.value}")
    print(f"Artifacts Generated: {len(task.artifacts)}\n")

    # Display orchestration results
    for artifact in task.artifacts:
        for part in artifact.parts:
            if hasattr(part, 'text'):
                print(part.text)
                break

    print_separator()


async def demo_agent_cards():
    """Demo 5: Agent Cards (A2A Protocol metadata)"""
    print_separator("Demo 5: Agent Cards - A2A Protocol Metadata")

    # Create all agents
    dataset_agent = DatasetAgent()
    researcher_agent = DeepResearcherAgent()

    agents = [dataset_agent, researcher_agent]

    for agent in agents:
        card = agent.get_agent_card()
        print(f"Agent: {card.name}")
        print(f"Description: {card.description}")
        print(f"Version: {card.version}")
        print(f"Skills: {len(card.skills)}")
        print(f"\nSkill Details:")
        for skill in card.skills:
            print(f"  • {skill.name}")
            print(f"    ID: {skill.id}")
            print(f"    Tags: {', '.join(skill.tags)}")
            if skill.examples:
                print(f"    Example: \"{skill.examples[0]}\"")
        print()

    print_separator()


async def demo_complete_workflow():
    """Demo 6: Complete end-to-end workflow"""
    print_separator("Demo 6: Complete End-to-End Workflow")

    # Setup complete system
    registry = AgentRegistry()

    dataset_agent = DatasetAgent()
    researcher_agent = DeepResearcherAgent()
    registry.register(dataset_agent)
    registry.register(researcher_agent)

    pm_agent = ProjectManagerAgent(registry)
    registry.register(pm_agent)

    orchestrator = OrchestratorAgent(registry)
    orchestrator.set_project_manager(pm_agent)
    registry.register(orchestrator)

    print("🚀 Complete Multi-Agent System Initialized\n")

    # Workflow: Dataset loading -> Research -> Synthesis
    workflow_requests = [
        {
            "description": "Dataset Loading",
            "message": "Load GLUE ax dataset for analysis"
        },
        {
            "description": "Deep Research",
            "message": "Research evaluation methodologies for NLP models"
        },
        {
            "description": "Orchestrated Workflow",
            "message": "Load the GLUE benchmark datasets and synthesize insights about their evaluation capabilities"
        }
    ]

    for i, req in enumerate(workflow_requests, 1):
        print(f"Step {i}: {req['description']}")
        print(f"Request: {req['message']}\n")

        messages = [
            Message(
                role=MessageRole.USER,
                parts=[TextPart(text=req['message'])]
            )
        ]

        # Use orchestrator for all requests
        task = await orchestrator.process_message(messages)
        print(f"✓ Status: {task.status.value}")
        print(f"✓ Artifacts: {len(task.artifacts)}\n")

    # Show statistics
    print_separator("System Statistics")

    pm_stats = pm_agent.get_routing_stats()
    print("Project Manager Statistics:")
    print(f"  Total Routings: {pm_stats['total_routings']}")
    if pm_stats['total_routings'] > 0:
        print(f"  Average Confidence: {pm_stats['average_confidence']:.1%}")
        print(f"  Most Used Agent: {pm_stats['most_used_agent']}")
        print(f"  Agent Distribution: {pm_stats['agent_distribution']}")
    print()

    orch_stats = orchestrator.get_orchestration_stats()
    print("Orchestrator Statistics:")
    print(f"  Total Workflows: {orch_stats['total_workflows']}")
    print(f"  Completed: {orch_stats['completed']}")
    print(f"  Success Rate: {orch_stats['success_rate']:.1%}")
    print(f"  Mode Distribution: {orch_stats['mode_distribution']}")

    print_separator()


async def main():
    """Run all demos"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║       Multi-Agent Orchestrator System - A2A Protocol Implementation         ║
║                                                                              ║
║  Features:                                                                   ║
║    • Orchestrator Agent (Co-scientist mode)                                  ║
║    • Project Manager Agent (Intelligent task routing)                        ║
║    • Deep Researcher Agent (Research & analysis)                             ║
║    • Dataset Ingestion Agent (Hugging Face integration)                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    demos = [
        ("Dataset Loading", demo_dataset_loading),
        ("Deep Research", demo_deep_research),
        ("Task Routing", demo_project_manager_routing),
        ("Orchestration", demo_orchestrator_workflow),
        ("Agent Cards", demo_agent_cards),
        ("Complete Workflow", demo_complete_workflow)
    ]

    print("Available Demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print()

    # Run all demos
    print("Running all demos...\n")
    for name, demo_func in demos:
        await demo_func()
        await asyncio.sleep(0.5)  # Small delay between demos

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                          All Demos Completed! 🎉                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    asyncio.run(main())
