"""
Comprehensive Demo: All 7 Specialized Agents

Demonstrates the complete multi-agent system including:
1. Dataset Ingestion Agent - HuggingFace integration
2. Deep Researcher Agent - Research & analysis
3. Grant Writing Genius Agent - NIH grant expertise
4. VPN Setup Agent - Outline SDK specialist
5. Bloom Agent - LLM behavior evaluation
6. Project Manager Agent - Intelligent routing
7. Orchestrator Agent - Co-scientist coordination

All agents follow the A2A Protocol specification.
"""
import sys
import asyncio
sys.path.append('..')

from core.a2a_base import (
    AgentRegistry, Message, TextPart, MessageRole
)
from agents import (
    OrchestratorAgent,
    ProjectManagerAgent,
    DeepResearcherAgent,
    DatasetAgent,
    GrantWritingAgent,
    VPNAgent,
    BloomAgent
)


def print_separator(title: str = ""):
    """Print a nice separator"""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    else:
        print(f"{'='*80}\n")


async def demo_grant_writing():
    """Demo: Grant Writing Genius Agent"""
    print_separator("Grant Writing Genius Agent")

    agent = GrantWritingAgent()

    # Test different capabilities
    test_requests = [
        "What are the NIH PDF formatting requirements?",
        "Check page limits for Research Strategy",
        "How do I cite papers in my grant?"
    ]

    for request in test_requests:
        print(f"📤 Request: {request}\n")

        messages = [Message(
            role=MessageRole.USER,
            parts=[TextPart(text=request)]
        )]

        task = await agent.process_message(messages)

        print(f"Status: {task.status.value}\n")

        # Show first artifact
        if task.artifacts:
            for part in task.artifacts[0].parts:
                if hasattr(part, 'text'):
                    # Print first 500 chars
                    text = part.text
                    print(text[:500] + "..." if len(text) > 500 else text)
                    print()
                    break

        print_separator()


async def demo_vpn_setup():
    """Demo: VPN Setup Agent"""
    print_separator("VPN Setup Agent - Outline SDK Specialist")

    agent = VPNAgent()

    test_requests = [
        "How do I set up Outline VPN?",
        "Bypass SNI blocking with Outline SDK",
        "Troubleshoot Outline connection issues"
    ]

    for request in test_requests:
        print(f"📤 Request: {request}\n")

        messages = [Message(
            role=MessageRole.USER,
            parts=[TextPart(text=request)]
        )]

        task = await agent.process_message(messages)

        print(f"Status: {task.status.value}\n")

        if task.artifacts:
            for part in task.artifacts[0].parts:
                if hasattr(part, 'text'):
                    text = part.text
                    print(text[:500] + "..." if len(text) > 500 else text)
                    print()
                    break

        print_separator()


async def demo_bloom_evaluation():
    """Demo: Bloom Agent - LLM Evaluation Expert"""
    print_separator("Bloom Agent - LLM Behavior Evaluation")

    agent = BloomAgent()

    test_requests = [
        "Design an evaluation for sycophancy",
        "Configure bloom pipeline for political bias testing",
        "How do I analyze bloom results?"
    ]

    for request in test_requests:
        print(f"📤 Request: {request}\n")

        messages = [Message(
            role=MessageRole.USER,
            parts=[TextPart(text=request)]
        )]

        task = await agent.process_message(messages)

        print(f"Status: {task.status.value}\n")

        if task.artifacts:
            for part in task.artifacts[0].parts:
                if hasattr(part, 'text'):
                    text = part.text
                    print(text[:500] + "..." if len(text) > 500 else text)
                    print()
                    break

        print_separator()


async def demo_intelligent_routing():
    """Demo: Project Manager automatically routing to specialized agents"""
    print_separator("Intelligent Task Routing")

    # Create registry with all agents
    registry = AgentRegistry()

    # Register specialized agents
    dataset_agent = DatasetAgent()
    researcher_agent = DeepResearcherAgent()
    grant_agent = GrantWritingAgent()
    vpn_agent = VPNAgent()
    bloom_agent = BloomAgent()

    registry.register(dataset_agent)
    registry.register(researcher_agent)
    registry.register(grant_agent)
    registry.register(vpn_agent)
    registry.register(bloom_agent)

    # Create project manager
    pm_agent = ProjectManagerAgent(registry)
    registry.register(pm_agent)

    print(f"Registered Agents: {len(registry.list_agents())}")
    for agent_name in registry.list_agents():
        print(f"  • {agent_name}")
    print()

    # Test routing to different agents
    test_requests = [
        "Load the GLUE cola dataset",
        "Check my grant PDF formatting",
        "Set up Outline VPN on Android",
        "Design a bloom evaluation for bias",
        "Research transformer architectures"
    ]

    for request in test_requests:
        print(f"\n📤 Request: {request}")

        messages = [Message(
            role=MessageRole.USER,
            parts=[TextPart(text=request)]
        )]

        task = await pm_agent.process_message(messages)

        print(f"✓ Routed and executed successfully")
        print(f"  Artifacts: {len(task.artifacts)}")

        # Show routing decision from first artifact
        if task.artifacts:
            for part in task.artifacts[0].parts:
                if hasattr(part, 'text'):
                    # Extract agent selection info
                    text = part.text
                    if "Selected Agent:" in text:
                        lines = text.split('\n')
                        for line in lines:
                            if "Selected Agent:" in line or "Confidence:" in line:
                                print(f"  {line.strip()}")
                    break

    print_separator()


async def demo_orchestrated_workflow():
    """Demo: Orchestrator coordinating complex multi-agent tasks"""
    print_separator("Orchestrator - Co-Scientist Mode")

    # Setup complete system
    registry = AgentRegistry()

    # Register all specialized agents
    agents = [
        DatasetAgent(),
        DeepResearcherAgent(),
        GrantWritingAgent(),
        VPNAgent(),
        BloomAgent()
    ]

    for agent in agents:
        registry.register(agent)

    # Add project manager
    pm_agent = ProjectManagerAgent(registry)
    registry.register(pm_agent)

    # Add orchestrator
    orchestrator = OrchestratorAgent(registry)
    orchestrator.set_project_manager(pm_agent)
    registry.register(orchestrator)

    print(f"🎭 Complete Multi-Agent System")
    print(f"Total Agents: {len(registry.list_agents())}\n")

    # Complex multi-step request
    complex_request = """
    I need help with three things:
    1. Load the GLUE benchmark datasets
    2. Verify my NIH grant PDF meets formatting requirements
    3. Set up a VPN using Outline SDK
    """

    print(f"📤 Complex Multi-Task Request:\n{complex_request}\n")

    messages = [Message(
        role=MessageRole.USER,
        parts=[TextPart(text=complex_request)]
    )]

    task = await orchestrator.process_message(messages)

    print(f"✓ Status: {task.status.value}")
    print(f"✓ Orchestration Complete")
    print(f"  Total Artifacts: {len(task.artifacts)}\n")

    # Show orchestration summary
    if task.artifacts:
        for part in task.artifacts[0].parts:
            if hasattr(part, 'text'):
                text = part.text
                if "Workflow ID:" in text:
                    lines = text.split('\n')
                    for line in lines[:15]:  # First 15 lines
                        print(line)
                break

    print_separator()


async def demo_all_agent_cards():
    """Demo: Display Agent Cards for all agents (A2A Protocol)"""
    print_separator("Agent Cards - A2A Protocol Metadata")

    agents = [
        DatasetAgent(),
        DeepResearcherAgent(),
        GrantWritingAgent(),
        VPNAgent(),
        BloomAgent()
    ]

    print("All Specialized Agents:\n")

    for agent in agents:
        card = agent.get_agent_card()
        print(f"{'─'*80}")
        print(f"Agent: {card.name}")
        print(f"Description: {card.description}")
        print(f"Version: {card.version}")
        print(f"Skills ({len(card.skills)}):")
        for skill in card.skills:
            print(f"  • {skill.name} ({skill.id})")
            print(f"    {skill.description}")
            if skill.examples:
                print(f"    Example: \"{skill.examples[0]}\"")
        print()

    print_separator()


async def demo_skill_based_search():
    """Demo: Find agents by skill"""
    print_separator("Skill-Based Agent Discovery")

    registry = AgentRegistry()

    # Register all agents
    for agent in [DatasetAgent(), DeepResearcherAgent(), GrantWritingAgent(),
                  VPNAgent(), BloomAgent()]:
        registry.register(agent)

    # Get all skills
    all_skills = registry.get_all_skills()

    print("Skills Available Across All Agents:\n")

    for agent_name, skills in all_skills.items():
        print(f"\n{agent_name}:")
        for skill in skills:
            print(f"  • {skill.name} ({skill.id})")

    # Test skill-based search
    print("\n" + "─"*80)
    print("\nFinding agents by skill:\n")

    test_skills = ["load_dataset", "format_validation", "outline_setup", "evaluation_design"]

    for skill_id in test_skills:
        agent = registry.find_agent_by_skill(skill_id)
        if agent:
            print(f"Skill '{skill_id}' → {agent.name}")

    print_separator()


async def demo_comparison():
    """Demo: Compare agent capabilities"""
    print_separator("Agent Capability Comparison")

    agents = [
        ("Dataset Agent", DatasetAgent()),
        ("Researcher Agent", DeepResearcherAgent()),
        ("Grant Writing Agent", GrantWritingAgent()),
        ("VPN Agent", VPNAgent()),
        ("Bloom Agent", BloomAgent())
    ]

    print(f"{'Agent':<25} | {'Skills':<8} | {'Primary Focus'}")
    print("─"*80)

    for name, agent in agents:
        skill_count = len(agent.skills)
        primary_skill = agent.skills[0].name if agent.skills else "N/A"
        print(f"{name:<25} | {skill_count:<8} | {primary_skill}")

    print()

    # Show specialization matrix
    print("\nSpecialization Matrix:\n")
    print(f"{'Capability':<30} | {'Best Agent'}")
    print("─"*80)

    capabilities = [
        ("Load HuggingFace datasets", "Dataset Agent"),
        ("Deep research & analysis", "Researcher Agent"),
        ("NIH grant formatting", "Grant Writing Agent"),
        ("VPN & network circumvention", "VPN Agent"),
        ("LLM behavior evaluation", "Bloom Agent")
    ]

    for capability, best_agent in capabilities:
        print(f"{capability:<30} | {best_agent}")

    print_separator()


async def main():
    """Run all comprehensive demos"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              7-Agent Multi-Agent System - Complete Demonstration             ║
║                        A2A Protocol Implementation                           ║
║                                                                              ║
║  Specialized Agents:                                                         ║
║    1. Dataset Ingestion Agent - HuggingFace datasets                         ║
║    2. Deep Researcher Agent - Research & analysis                            ║
║    3. Grant Writing Genius - NIH grants expert                               ║
║    4. VPN Setup Agent - Outline SDK specialist                               ║
║    5. Bloom Agent - LLM behavior evaluation                                  ║
║    6. Project Manager - Intelligent routing                                  ║
║    7. Orchestrator - Co-scientist coordination                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    demos = [
        ("Grant Writing Genius", demo_grant_writing),
        ("VPN Setup Specialist", demo_vpn_setup),
        ("Bloom Evaluation Expert", demo_bloom_evaluation),
        ("Intelligent Routing", demo_intelligent_routing),
        ("Orchestrated Workflow", demo_orchestrated_workflow),
        ("Agent Cards (A2A Protocol)", demo_all_agent_cards),
        ("Skill-Based Discovery", demo_skill_based_search),
        ("Capability Comparison", demo_comparison)
    ]

    print("Available Demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print()

    # Run all demos
    print("Running all demos...\n")
    for name, demo_func in demos:
        await demo_func()
        await asyncio.sleep(0.3)  # Small delay between demos

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                  All Demos Completed Successfully! 🎉                        ║
║                                                                              ║
║  You now have a complete multi-agent system with:                            ║
║    ✓ 5 specialized domain expert agents                                     ║
║    ✓ 1 intelligent project manager for routing                              ║
║    ✓ 1 orchestrator for complex workflows                                   ║
║    ✓ Full A2A Protocol compliance                                           ║
║    ✓ Extensible architecture for adding more agents                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    asyncio.run(main())
