"""
Deep Researcher Agent - Specialized in research, analysis, and knowledge synthesis
"""
import sys
sys.path.append('..')

from typing import List, Dict, Any, Optional
from core.a2a_base import (
    BaseAgent, Message, Task, TaskStatus, Artifact,
    TextPart, DataPart, AgentSkill, MessageRole
)
import json
from datetime import datetime


class DeepResearcherAgent(BaseAgent):
    """
    Advanced research agent that performs deep analysis, knowledge synthesis,
    and comprehensive investigation of topics.
    """

    def __init__(self):
        super().__init__(
            name="Deep Researcher Agent",
            description="Advanced AI researcher capable of deep analysis, literature review, and knowledge synthesis",
            version="1.0.0"
        )

        # Register research skills
        self.add_skill(AgentSkill(
            id="deep_analysis",
            name="Deep Analysis",
            description="Perform comprehensive analysis of topics with multi-layered investigation",
            tags=["research", "analysis", "investigation"],
            examples=[
                "Perform deep analysis on transformer architectures",
                "Research the history of reinforcement learning",
                "Analyze trade-offs between different ML frameworks"
            ]
        ))

        self.add_skill(AgentSkill(
            id="literature_review",
            name="Literature Review",
            description="Systematic review of academic papers and technical documentation",
            tags=["research", "papers", "academic"],
            examples=[
                "Review recent papers on large language models",
                "Summarize research on federated learning",
                "Compare approaches to neural architecture search"
            ]
        ))

        self.add_skill(AgentSkill(
            id="knowledge_synthesis",
            name="Knowledge Synthesis",
            description="Synthesize information from multiple sources into coherent insights",
            tags=["synthesis", "integration", "insights"],
            examples=[
                "Synthesize findings on zero-shot learning",
                "Integrate knowledge about multi-modal models",
                "Compare and contrast different attention mechanisms"
            ]
        ))

        self.add_skill(AgentSkill(
            id="hypothesis_generation",
            name="Hypothesis Generation",
            description="Generate research hypotheses and experimental designs",
            tags=["hypothesis", "experiment", "design"],
            examples=[
                "Generate hypotheses about model scaling laws",
                "Design experiment to test prompt engineering techniques"
            ]
        ))

        # Research knowledge base
        self.knowledge_base: Dict[str, Any] = {}
        self.research_history: List[Dict[str, Any]] = []

    def _extract_research_query(self, message_text: str) -> Dict[str, Any]:
        """Extract and categorize research query"""
        text_lower = message_text.lower()

        query_info = {
            "query": message_text,
            "type": "general",
            "keywords": [],
            "depth": "standard"
        }

        # Determine research type
        if any(word in text_lower for word in ["deep", "comprehensive", "thorough", "detailed"]):
            query_info["depth"] = "deep"
        elif any(word in text_lower for word in ["quick", "brief", "summary"]):
            query_info["depth"] = "shallow"

        if any(word in text_lower for word in ["analyze", "analysis", "examine"]):
            query_info["type"] = "analysis"
        elif any(word in text_lower for word in ["review", "survey", "literature"]):
            query_info["type"] = "literature_review"
        elif any(word in text_lower for word in ["synthesize", "integrate", "combine"]):
            query_info["type"] = "synthesis"
        elif any(word in text_lower for word in ["hypothesis", "experiment", "test"]):
            query_info["type"] = "hypothesis"

        # Extract potential keywords (simplified)
        technical_terms = [
            "transformer", "llm", "bert", "gpt", "attention", "dataset",
            "neural network", "deep learning", "machine learning", "ai",
            "reinforcement learning", "supervised", "unsupervised",
            "glue", "benchmark", "evaluation"
        ]

        for term in technical_terms:
            if term in text_lower:
                query_info["keywords"].append(term)

        return query_info

    async def conduct_deep_research(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct deep research based on query type and depth.
        This is a simplified implementation - in production, integrate with
        knowledge bases, APIs, and specialized research tools.
        """
        research_type = query_info["type"]
        depth = query_info["depth"]
        keywords = query_info["keywords"]

        # Simulate research process
        research_result = {
            "query": query_info["query"],
            "type": research_type,
            "depth": depth,
            "timestamp": datetime.now().isoformat(),
            "findings": [],
            "sources": [],
            "confidence": 0.0,
            "research_steps": []
        }

        # Step 1: Initial exploration
        research_result["research_steps"].append({
            "step": 1,
            "action": "Initial exploration and context gathering",
            "status": "completed"
        })

        # Step 2: Deep dive based on type
        if research_type == "analysis":
            findings = await self._perform_analysis(keywords, depth)
            research_result["findings"] = findings
            research_result["research_steps"].append({
                "step": 2,
                "action": "Multi-dimensional analysis",
                "status": "completed"
            })

        elif research_type == "literature_review":
            findings = await self._literature_review(keywords, depth)
            research_result["findings"] = findings
            research_result["research_steps"].append({
                "step": 2,
                "action": "Systematic literature review",
                "status": "completed"
            })

        elif research_type == "synthesis":
            findings = await self._knowledge_synthesis(keywords, depth)
            research_result["findings"] = findings
            research_result["research_steps"].append({
                "step": 2,
                "action": "Knowledge integration and synthesis",
                "status": "completed"
            })

        elif research_type == "hypothesis":
            findings = await self._generate_hypotheses(keywords, depth)
            research_result["findings"] = findings
            research_result["research_steps"].append({
                "step": 2,
                "action": "Hypothesis generation and experimental design",
                "status": "completed"
            })

        else:
            findings = await self._general_research(keywords, depth)
            research_result["findings"] = findings

        # Step 3: Validation and confidence assessment
        research_result["confidence"] = self._calculate_confidence(research_result)
        research_result["research_steps"].append({
            "step": 3,
            "action": "Validation and confidence assessment",
            "status": "completed"
        })

        # Store in knowledge base
        kb_key = f"research_{len(self.research_history)}"
        self.knowledge_base[kb_key] = research_result
        self.research_history.append(research_result)

        return research_result

    async def _perform_analysis(self, keywords: List[str], depth: str) -> List[Dict[str, Any]]:
        """Perform multi-dimensional analysis"""
        findings = [
            {
                "dimension": "Technical Architecture",
                "insight": "Analysis of technical components and design patterns",
                "details": "In-depth examination of architectural decisions and trade-offs",
                "confidence": 0.85
            },
            {
                "dimension": "Performance Characteristics",
                "insight": "Evaluation of efficiency, scalability, and resource requirements",
                "details": "Quantitative and qualitative performance analysis",
                "confidence": 0.78
            }
        ]

        if depth == "deep":
            findings.extend([
                {
                    "dimension": "Historical Context",
                    "insight": "Evolution and development timeline",
                    "details": "Understanding the progression and key milestones",
                    "confidence": 0.72
                },
                {
                    "dimension": "Comparative Analysis",
                    "insight": "Comparison with alternative approaches",
                    "details": "Strengths, weaknesses, and differentiating factors",
                    "confidence": 0.80
                }
            ])

        return findings

    async def _literature_review(self, keywords: List[str], depth: str) -> List[Dict[str, Any]]:
        """Conduct systematic literature review"""
        findings = [
            {
                "category": "Foundational Papers",
                "papers": ["Seminal work establishing core concepts"],
                "summary": "Key theoretical foundations and initial breakthroughs",
                "relevance": 0.95
            },
            {
                "category": "Recent Advances",
                "papers": ["Latest developments and improvements"],
                "summary": "State-of-the-art techniques and ongoing research",
                "relevance": 0.90
            }
        ]

        if depth == "deep":
            findings.extend([
                {
                    "category": "Empirical Studies",
                    "papers": ["Experimental validations and benchmarks"],
                    "summary": "Evidence-based findings and performance comparisons",
                    "relevance": 0.82
                },
                {
                    "category": "Critical Reviews",
                    "papers": ["Meta-analyses and systematic reviews"],
                    "summary": "Comprehensive assessments and critiques",
                    "relevance": 0.78
                }
            ])

        return findings

    async def _knowledge_synthesis(self, keywords: List[str], depth: str) -> List[Dict[str, Any]]:
        """Synthesize knowledge from multiple sources"""
        return [
            {
                "theme": "Convergent Findings",
                "synthesis": "Common patterns and consensus across sources",
                "integration_level": "high"
            },
            {
                "theme": "Divergent Perspectives",
                "synthesis": "Conflicting views and open questions",
                "integration_level": "medium"
            },
            {
                "theme": "Emergent Insights",
                "synthesis": "Novel connections and implications",
                "integration_level": "high"
            }
        ]

    async def _generate_hypotheses(self, keywords: List[str], depth: str) -> List[Dict[str, Any]]:
        """Generate research hypotheses"""
        return [
            {
                "hypothesis": "Primary research hypothesis based on current understanding",
                "rationale": "Theoretical foundation and supporting evidence",
                "testability": "high",
                "experimental_design": "Proposed methodology for validation"
            },
            {
                "hypothesis": "Alternative hypothesis exploring different mechanisms",
                "rationale": "Competing explanation with distinct predictions",
                "testability": "medium",
                "experimental_design": "Comparative experimental approach"
            }
        ]

    async def _general_research(self, keywords: List[str], depth: str) -> List[Dict[str, Any]]:
        """General research across multiple dimensions"""
        return [
            {
                "aspect": "Overview",
                "content": "High-level understanding and context",
                "depth_level": depth
            },
            {
                "aspect": "Key Concepts",
                "content": "Core principles and terminology",
                "depth_level": depth
            }
        ]

    def _calculate_confidence(self, research_result: Dict[str, Any]) -> float:
        """Calculate confidence score for research findings"""
        # Simplified confidence calculation
        base_confidence = 0.75

        # Adjust based on depth
        if research_result["depth"] == "deep":
            base_confidence += 0.10
        elif research_result["depth"] == "shallow":
            base_confidence -= 0.10

        # Adjust based on number of findings
        findings_count = len(research_result["findings"])
        if findings_count > 3:
            base_confidence += 0.05

        return min(0.95, base_confidence)

    async def process_message(self, messages: List[Message]) -> Task:
        """Process research requests"""
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

            # Extract research query
            query_info = self._extract_research_query(message_text)

            # Conduct research
            research_result = await self.conduct_deep_research(query_info)

            # Format response
            response_text = self._format_research_response(research_result)

            # Create artifact
            artifact = Artifact(
                name="Research Report",
                description=f"Deep research on: {query_info['query'][:100]}",
                parts=[
                    TextPart(text=response_text),
                    DataPart(data=research_result, mimeType="application/json")
                ]
            )

            self.add_artifact(task.id, artifact)
            self.update_task_status(task.id, TaskStatus.COMPLETED)

        except Exception as e:
            self.update_task_status(task.id, TaskStatus.FAILED, error=str(e))

        return self.get_task(task.id)

    def _format_research_response(self, research_result: Dict[str, Any]) -> str:
        """Format research results into readable report"""
        response = f"""🔬 Deep Research Report

Query: {research_result['query']}
Type: {research_result['type'].replace('_', ' ').title()}
Depth: {research_result['depth'].upper()}
Confidence: {research_result['confidence']:.1%}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        # Format findings based on type
        for i, finding in enumerate(research_result['findings'], 1):
            response += f"\n🔍 Finding {i}:\n"
            for key, value in finding.items():
                if isinstance(value, str):
                    response += f"  {key.title()}: {value}\n"
                elif isinstance(value, (int, float)):
                    if 'confidence' in key or 'relevance' in key:
                        response += f"  {key.title()}: {value:.1%}\n"
                    else:
                        response += f"  {key.title()}: {value}\n"
                elif isinstance(value, list):
                    response += f"  {key.title()}:\n"
                    for item in value:
                        response += f"    - {item}\n"

        response += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        response += f"\n📊 Research Process:\n"
        for step in research_result['research_steps']:
            response += f"  {step['step']}. {step['action']} - {step['status']}\n"

        return response
