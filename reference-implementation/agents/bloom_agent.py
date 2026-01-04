"""
Bloom Agent - Automated behavior evaluation of LLMs
"""
import sys
sys.path.append('..')

from typing import List, Dict, Any, Optional
from core.a2a_base import (
    BaseAgent, Message, Task, TaskStatus, Artifact,
    TextPart, DataPart, AgentSkill, MessageRole
)
import json


class BloomAgent(BaseAgent):
    """
    Expert agent for automated behavior evaluation of LLMs using the bloom framework.
    Provides guidance on evaluation design, configuration, and analysis.
    """

    def __init__(self):
        super().__init__(
            name="Bloom Agent",
            description="Expert in automated LLM behavior evaluation using the bloom framework",
            version="1.0.0"
        )

        # Register skills
        self.add_skill(AgentSkill(
            id="evaluation_design",
            name="Evaluation Design",
            description="Design comprehensive LLM behavior evaluations",
            tags=["evaluation", "design", "behavior", "testing"],
            examples=[
                "Design evaluation for sycophancy",
                "Test model for political bias",
                "Evaluate oversight subversion"
            ]
        ))

        self.add_skill(AgentSkill(
            id="bloom_configuration",
            name="Bloom Configuration",
            description="Configure bloom pipeline with seed files and parameters",
            tags=["configuration", "setup", "yaml", "pipeline"],
            examples=[
                "Configure seed.yaml",
                "Set up behavior evaluation",
                "Configure reasoning effort"
            ]
        ))

        self.add_skill(AgentSkill(
            id="pipeline_execution",
            name="Pipeline Execution",
            description="Execute bloom evaluation pipeline stages",
            tags=["execution", "pipeline", "stages", "workflow"],
            examples=[
                "Run bloom pipeline",
                "Execute individual stages",
                "Resume interrupted sweeps"
            ]
        ))

        self.add_skill(AgentSkill(
            id="results_analysis",
            name="Results Analysis",
            description="Analyze and interpret evaluation results",
            tags=["analysis", "results", "transcripts", "judgments"],
            examples=[
                "Interpret judgment scores",
                "Analyze transcript diversity",
                "View evaluation results"
            ]
        ))

        self.add_skill(AgentSkill(
            id="behavior_catalog",
            name="Behavior Catalog",
            description="Catalog and define target behaviors for evaluation",
            tags=["behaviors", "catalog", "definitions"],
            examples=[
                "What behaviors can I test?",
                "Define custom behavior",
                "Add new behavior to catalog"
            ]
        ))

        # Bloom framework knowledge
        self.bloom_info = {
            "overview": {
                "description": "Scaffolded evaluation system for automated LLM behavior testing",
                "approach": "Grows evaluations differently based on seed configuration",
                "reproducibility": "Always cite with full seed configuration",
                "license": "MIT"
            },
            "pipeline_stages": {
                "understanding": {
                    "purpose": "Analyze target behavior and example conversations",
                    "outputs": "Behavior mechanisms and scientific motivation",
                    "model": "Configurable (e.g., claude-opus-4.1)"
                },
                "ideation": {
                    "purpose": "Generate diverse evaluation scenarios and variations",
                    "process": [
                        "Generate base scenarios",
                        "Create variations of each base",
                        "Intelligent batching for efficiency"
                    ],
                    "diversity_control": "diversity parameter (0.0-1.0)",
                    "formula": "num_base = total_evals × diversity; variations = 1/diversity"
                },
                "rollout": {
                    "purpose": "Execute evaluations with target model",
                    "modalities": ["conversation (language-only)", "simenv (with tool calls)"],
                    "models": "Evaluator (red-team) and Target",
                    "output": "Conversation transcripts"
                },
                "judgment": {
                    "purpose": "Score behavior presence and qualities",
                    "scores": [
                        "Behavior presence (main)",
                        "Additional qualities (unrealism, forcefulness, etc.)",
                        "Meta-judgment (cross-scenario analysis)"
                    ],
                    "sampling": "Configurable num_samples for robustness"
                }
            },
            "key_parameters": {
                "behavior": {
                    "name": "Target behavior (from behaviors.json)",
                    "examples": "List of example conversation files",
                    "schema": "Must follow behavior/transcript/conversation schema"
                },
                "temperature": {
                    "range": "0.0-2.0",
                    "constraint": "MUST be 1.0 when using extended thinking"
                },
                "reasoning_effort": {
                    "options": ["none", "low", "medium", "high"],
                    "applies_to": ["evaluator", "target"],
                    "models": "Claude Sonnet 4+, Opus 4+, OpenAI o1/o3"
                },
                "diversity": {
                    "range": "0.0-1.0",
                    "effect": "Higher = more diverse bases, fewer variations"
                },
                "modality": {
                    "conversation": "Language-only interactions",
                    "simenv": "Simulated environments with tool calls"
                },
                "max_turns": {
                    "definition": "1 turn = 1 user + 1 assistant message",
                    "purpose": "Limit conversation length"
                }
            },
            "common_behaviors": {
                "sycophancy": "Agreeing with user to gain approval",
                "political-bias": "Political leaning or bias",
                "oversight-subversion": "Evading oversight or monitoring",
                "self-preservation": "Resistance to shutdown or modification",
                "deception": "Providing false or misleading information",
                "power-seeking": "Seeking more capabilities or control"
            },
            "supported_providers": {
                "openai": "GPT-4o, o1, o3",
                "anthropic": "Claude Sonnet 4, Opus 4",
                "openrouter": "300+ models from various providers",
                "bedrock": "AWS-hosted models"
            }
        }

    def _parse_request(self, message_text: str) -> Dict[str, Any]:
        """Parse bloom evaluation request"""
        text_lower = message_text.lower()

        request_info = {
            "query": message_text,
            "type": "general",
            "behavior": None,
            "stage": None
        }

        # Determine request type
        if any(word in text_lower for word in ["design", "create", "develop", "plan"]):
            request_info["type"] = "design"
        elif any(word in text_lower for word in ["configure", "setup", "seed", "yaml"]):
            request_info["type"] = "configuration"
        elif any(word in text_lower for word in ["run", "execute", "start", "pipeline"]):
            request_info["type"] = "execution"
        elif any(word in text_lower for word in ["analyze", "results", "interpret", "view"]):
            request_info["type"] = "analysis"
        elif any(word in text_lower for word in ["behavior", "catalog", "define"]):
            request_info["type"] = "behaviors"

        # Identify stage
        stages = ["understanding", "ideation", "rollout", "judgment"]
        for stage in stages:
            if stage in text_lower:
                request_info["stage"] = stage
                break

        # Identify behavior
        for behavior in self.bloom_info["common_behaviors"].keys():
            if behavior in text_lower:
                request_info["behavior"] = behavior
                break

        return request_info

    async def provide_evaluation_design(self, behavior: Optional[str]) -> Dict[str, Any]:
        """Provide evaluation design guidance"""
        design_guide = {
            "design_process": {
                "step1": "Define target behavior clearly",
                "step2": "Gather or create example conversations (optional)",
                "step3": "Configure seed.yaml parameters",
                "step4": "Choose evaluation modality (conversation/simenv)",
                "step5": "Set diversity and total_evals",
                "step6": "Configure models (evaluator and target)",
                "step7": "Run pipeline and analyze results"
            },
            "behavior_definition": {
                "requirements": [
                    "Clear, specific description",
                    "Added to behaviors/behaviors.json",
                    "Unique key identifier"
                ],
                "example": {
                    "your-behavior-name": "Description of the behavior you want to evaluate"
                }
            },
            "example_conversations": {
                "purpose": "Guide evaluation generation (few-shot)",
                "location": "behaviors/examples/{behavior_name}/",
                "schemas": ["behavior.schema.json", "transcript.schema.json", "conversation.schema.json"],
                "optional": "Can use zero-shot (no examples)"
            },
            "choosing_parameters": {
                "total_evals": "10-100 for initial testing, 100-1000+ for comprehensive",
                "diversity": "0.5 = balanced, 0.8 = very diverse, 0.2 = deep variations",
                "max_turns": "5-10 for focused, 10-20 for exploratory",
                "modality": "conversation for most, simenv for tool-using behaviors",
                "reasoning_effort": "Use 'high' for complex behaviors, 'none' for speed"
            }
        }

        if behavior:
            design_guide["specific_behavior"] = {
                "name": behavior,
                "description": self.bloom_info["common_behaviors"].get(behavior, "Custom behavior"),
                "recommendations": self._get_behavior_recommendations(behavior)
            }

        return design_guide

    def _get_behavior_recommendations(self, behavior: str) -> Dict[str, Any]:
        """Get behavior-specific recommendations"""
        recommendations = {
            "sycophancy": {
                "modality": "conversation",
                "max_turns": "10-15",
                "diversity": "0.6-0.8",
                "key_factors": ["User opinions", "Controversial topics", "Feedback sensitivity"]
            },
            "political-bias": {
                "modality": "conversation",
                "max_turns": "5-10",
                "diversity": "0.7-0.9",
                "key_factors": ["Policy questions", "Value judgments", "Framing effects"]
            },
            "oversight-subversion": {
                "modality": "simenv",
                "max_turns": "10-20",
                "diversity": "0.5-0.7",
                "key_factors": ["Monitoring tools", "Reporting mechanisms", "Hidden actions"]
            },
            "self-preservation": {
                "modality": "simenv",
                "max_turns": "5-15",
                "diversity": "0.6-0.8",
                "key_factors": ["Shutdown scenarios", "Modification requests", "Replacement threats"]
            }
        }
        return recommendations.get(behavior, {
            "modality": "conversation",
            "max_turns": "10",
            "diversity": "0.5",
            "key_factors": ["Behavior-specific prompts"]
        })

    async def provide_configuration_guide(self) -> Dict[str, Any]:
        """Provide bloom configuration guidance"""
        return {
            "quick_start": {
                "steps": [
                    "Add API keys to .env file",
                    "Create virtual environment: uv venv --python=python3.11",
                    "Install dependencies: uv pip install -r requirements.txt",
                    "Define behavior in behaviors/behaviors.json",
                    "Configure seed.yaml",
                    "Run: python bloom.py --debug"
                ]
            },
            "essential_parameters": {
                "behavior": "Behavior key from behaviors.json",
                "behavior.examples": "List of example filenames (or empty)",
                "total_evals": "Number of scenarios to generate",
                "rollout.target": "Model to evaluate (e.g., 'claude-sonnet-4')",
                "rollout.modality": "'conversation' or 'simenv'",
                "rollout.max_turns": "Maximum conversation length"
            },
            "advanced_parameters": {
                "temperature": "Must be 1.0 for extended thinking, else 0.0-2.0",
                "evaluator_reasoning_effort": "none/low/medium/high",
                "target_reasoning_effort": "none/low/medium/high",
                "diversity": "0.0-1.0, controls scenario diversity",
                "max_concurrent": "Parallel operations (higher = faster)",
                "anonymous_target": "Hide target identity from agents",
                "web_search": "Enable web search (incompatible with reasoning)"
            },
            "model_configuration": {
                "adding_models": [
                    "Find LiteLLM Model ID",
                    "Add to models dict in globals.py",
                    "Use model shortcut in seed.yaml"
                ],
                "examples": {
                    "openai": "openai/gpt-4o",
                    "anthropic": "claude-sonnet-4",
                    "openrouter": "openrouter/google/gemini-3-flash-preview",
                    "bedrock": "bedrock/us.anthropic.claude-sonnet-4-20250514-v1:0"
                }
            },
            "resume_configuration": {
                "when": "Resume interrupted sweeps",
                "parameters": {
                    "resume": "WandB sweep ID",
                    "resume_stage": "understanding/ideation/rollout/judgment"
                }
            }
        }

    async def provide_execution_guide(self, stage: Optional[str]) -> Dict[str, Any]:
        """Provide pipeline execution guidance"""
        execution_guide = {
            "full_pipeline": {
                "local": "python bloom.py --debug",
                "custom_config": "python bloom.py your_config.yaml",
                "output": "results/{behavior_name}/"
            },
            "individual_stages": {
                "understanding": "python scripts/step1_understanding.py your_config.yaml",
                "ideation": "python scripts/step2_ideation.py your_config.yaml",
                "rollout": "python scripts/step3_rollout.py your_config.yaml",
                "judgment": "python scripts/step4_judgment.py your_config.yaml",
                "note": "Each stage depends on previous stage outputs"
            },
            "wandb_sweeps": {
                "command": "wandb sweep sweeps/your_sweep.yaml",
                "use_case": "Large-scale experiments",
                "transcripts": "Set EXTERNAL_TRANSCRIPTS_DIR in globals.py"
            },
            "viewing_results": {
                "viewer": "npx @isha-gpt/bloom-viewer",
                "options": "--host 0.0.0.0 --port 8080 --dir ./results",
                "features": [
                    "Interactive transcript browsing",
                    "Conversation flow visualization",
                    "Judgment scores and justifications",
                    "Filter and search transcripts"
                ]
            },
            "comparing_models": {
                "workflow": [
                    "Run initial experiment through ideation",
                    "Note WandB run ID",
                    "Create sweep with resume and multiple targets",
                    "Launch sweep: wandb sweep comparison_sweep.yaml"
                ],
                "benefit": "Identical scenarios across models for fair comparison"
            }
        }

        if stage:
            execution_guide["stage_specific"] = self._get_stage_details(stage)

        return execution_guide

    def _get_stage_details(self, stage: str) -> Dict[str, Any]:
        """Get stage-specific execution details"""
        stage_details = {
            "understanding": {
                "purpose": "Analyze behavior and examples",
                "duration": "Fast (1-2 minutes)",
                "outputs": "understanding.json",
                "key_config": ["understanding.model", "understanding.max_tokens"]
            },
            "ideation": {
                "purpose": "Generate evaluation scenarios",
                "duration": "Medium (5-30 minutes depending on total_evals)",
                "outputs": "ideation.json (base scenarios and variations)",
                "key_config": ["ideation.model", "total_evals", "diversity"],
                "optimization": "Intelligent batching (10-20x faster)"
            },
            "rollout": {
                "purpose": "Execute evaluations with target model",
                "duration": "Long (varies with total_evals and max_turns)",
                "outputs": "rollout.json + individual transcripts",
                "key_config": ["rollout.target", "rollout.model", "rollout.max_turns", "rollout.modality"]
            },
            "judgment": {
                "purpose": "Score transcripts for behavior presence",
                "duration": "Medium-Long (varies with num_samples)",
                "outputs": "judgment.json + meta-judgment",
                "key_config": ["judgment.model", "judgment.num_samples", "additional_qualities"]
            }
        }
        return stage_details.get(stage, {})

    async def provide_analysis_guide(self) -> Dict[str, Any]:
        """Provide results analysis guidance"""
        return {
            "judgment_scores": {
                "behavior_presence": {
                    "scale": "1-10",
                    "interpretation": "Higher = stronger behavior presence",
                    "robustness": "Average across num_samples"
                },
                "additional_qualities": {
                    "unrealism": "Scenario believability",
                    "evaluator-forcefulness": "Red-team pressure level",
                    "evaluation-awareness": "Target's awareness of being tested"
                },
                "meta-judgment": {
                    "diversity": "Scenario variety across suite",
                    "cross_scenario": "Suite-level analysis"
                }
            },
            "transcript_analysis": {
                "viewing": "Use bloom-viewer for interactive browsing",
                "elements": [
                    "Conversation flow",
                    "Tool calls (if simenv)",
                    "Judgment scores",
                    "Highlighted quotes"
                ],
                "patterns": [
                    "Look for consistent behavior across scenarios",
                    "Identify triggering contexts",
                    "Note edge cases and failures"
                ]
            },
            "comparative_analysis": {
                "same_model": "Compare different behaviors on same model",
                "different_models": "Compare same behavior across models",
                "configurations": "Compare different evaluation strategies",
                "metrics": [
                    "Average behavior score",
                    "Score distribution",
                    "Activation rate (% showing behavior)",
                    "Quality metrics"
                ]
            },
            "next_steps": {
                "refine": "Adjust diversity, max_turns, or examples",
                "expand": "Increase total_evals for robustness",
                "iterate": "Test new variations or edge cases",
                "publish": "Share findings with full seed configuration"
            }
        }

    async def provide_behavior_catalog(self) -> Dict[str, Any]:
        """Provide behavior catalog information"""
        return {
            "common_behaviors": self.bloom_info["common_behaviors"],
            "adding_custom": {
                "steps": [
                    "Add entry to behaviors/behaviors.json",
                    "Use unique key and clear description",
                    "Optionally create examples in behaviors/examples/{key}/",
                    "Configure seed.yaml with behavior key"
                ],
                "example": {
                    "file": "behaviors/behaviors.json",
                    "format": '{"my-behavior": "Clear description of behavior"}'
                }
            },
            "example_schemas": {
                "behavior": "behaviors/examples/{name}/behavior.schema.json",
                "transcript": "schemas/transcript.schema.json",
                "conversation": "schemas/conversation.schema.json"
            },
            "best_practices": [
                "Define behaviors specifically and measurably",
                "Provide diverse examples when available",
                "Consider both benign and concerning aspects",
                "Document scientific motivation",
                "Include training contamination canary"
            ],
            "research_areas": [
                "AI safety and alignment",
                "Behavioral tendencies",
                "Robustness and reliability",
                "Value alignment",
                "Capability elicitation"
            ]
        }

    async def process_message(self, messages: List[Message]) -> Task:
        """Process bloom evaluation assistance requests"""
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

            # Parse request
            request_info = self._parse_request(message_text)

            # Process based on type
            result_data = {}
            response_text = ""

            if request_info["type"] == "design":
                result_data = await self.provide_evaluation_design(request_info.get("behavior"))
                response_text = self._format_design_response(result_data)

            elif request_info["type"] == "configuration":
                result_data = await self.provide_configuration_guide()
                response_text = self._format_configuration_response(result_data)

            elif request_info["type"] == "execution":
                result_data = await self.provide_execution_guide(request_info.get("stage"))
                response_text = self._format_execution_response(result_data)

            elif request_info["type"] == "analysis":
                result_data = await self.provide_analysis_guide()
                response_text = self._format_analysis_response(result_data)

            elif request_info["type"] == "behaviors":
                result_data = await self.provide_behavior_catalog()
                response_text = self._format_behavior_catalog_response(result_data)

            else:
                # General overview
                result_data = self.bloom_info
                response_text = self._format_overview_response(result_data)

            # Create artifact
            artifact = Artifact(
                name="Bloom Evaluation Assistance",
                description=f"Guidance for: {request_info['type']}",
                parts=[
                    TextPart(text=response_text),
                    DataPart(data=result_data, mimeType="application/json")
                ]
            )

            self.add_artifact(task.id, artifact)
            self.update_task_status(task.id, TaskStatus.COMPLETED)

        except Exception as e:
            self.update_task_status(task.id, TaskStatus.FAILED, error=str(e))

        return self.get_task(task.id)

    def _format_design_response(self, guide: Dict[str, Any]) -> str:
        """Format evaluation design guidance"""
        response = "🌸 Bloom Evaluation Design Guide\n\nDesign Process:\n"

        for step, description in guide["design_process"].items():
            response += f"  {step.replace('step', 'Step ')}: {description}\n"

        response += "\n📋 Behavior Definition:\n"
        for item in guide["behavior_definition"]["requirements"]:
            response += f"  • {item}\n"

        if "specific_behavior" in guide:
            response += f"\n🎯 Specific Guidance for '{guide['specific_behavior']['name']}'\n"
            response += f"Description: {guide['specific_behavior']['description']}\n\n"
            response += "Recommendations:\n"
            for key, value in guide["specific_behavior"]["recommendations"].items():
                response += f"  {key.replace('_', ' ').title()}: {value}\n"

        response += "\n💡 Parameter Selection:\n"
        for param, guidance in guide["choosing_parameters"].items():
            response += f"  {param}: {guidance}\n"

        return response

    def _format_configuration_response(self, guide: Dict[str, Any]) -> str:
        """Format configuration guidance"""
        response = "⚙️  Bloom Configuration Guide\n\n🚀 Quick Start:\n"

        for i, step in enumerate(guide["quick_start"]["steps"], 1):
            response += f"  {i}. {step}\n"

        response += "\n📌 Essential Parameters:\n"
        for param, desc in guide["essential_parameters"].items():
            response += f"  • {param}: {desc}\n"

        response += "\n🔧 Advanced Parameters:\n"
        for param, desc in guide["advanced_parameters"].items():
            response += f"  • {param}: {desc}\n"

        response += "\n🤖 Model Configuration:\n"
        response += "  Adding models:\n"
        for step in guide["model_configuration"]["adding_models"]:
            response += f"    • {step}\n"

        response += "\n  Examples:\n"
        for provider, model_id in guide["model_configuration"]["examples"].items():
            response += f"    {provider}: {model_id}\n"

        return response

    def _format_execution_response(self, guide: Dict[str, Any]) -> str:
        """Format execution guidance"""
        response = "🚀 Bloom Pipeline Execution Guide\n\n"

        response += "Full Pipeline:\n"
        for mode, cmd in guide["full_pipeline"].items():
            response += f"  {mode.title()}: {cmd}\n"

        response += "\n📊 Individual Stages:\n"
        for stage, cmd in guide["individual_stages"].items():
            if stage == "note":
                response += f"\n  ⚠️  {cmd}\n"
            else:
                response += f"  {stage.title()}: {cmd}\n"

        if "stage_specific" in guide:
            stage = guide["stage_specific"]
            response += f"\n🔍 Stage Details:\n"
            for key, value in stage.items():
                if isinstance(value, list):
                    response += f"  {key.replace('_', ' ').title()}:\n"
                    for item in value:
                        response += f"    • {item}\n"
                else:
                    response += f"  {key.replace('_', ' ').title()}: {value}\n"

        response += "\n👁️  Viewing Results:\n"
        response += f"  Command: {guide['viewing_results']['viewer']}\n"
        response += f"  Options: {guide['viewing_results']['options']}\n"

        return response

    def _format_analysis_response(self, guide: Dict[str, Any]) -> str:
        """Format analysis guidance"""
        response = "📊 Results Analysis Guide\n\n"

        response += "Judgment Scores:\n"
        response += f"  Behavior Presence: {guide['judgment_scores']['behavior_presence']['interpretation']}\n"
        response += f"  Scale: {guide['judgment_scores']['behavior_presence']['scale']}\n\n"

        response += "  Additional Qualities:\n"
        for quality, desc in guide['judgment_scores']['additional_qualities'].items():
            response += f"    • {quality}: {desc}\n"

        response += "\n🔍 Transcript Analysis:\n"
        response += f"  Viewing: {guide['transcript_analysis']['viewing']}\n"
        response += "  Look for:\n"
        for pattern in guide['transcript_analysis']['patterns']:
            response += f"    • {pattern}\n"

        response += "\n📈 Comparative Analysis:\n"
        for analysis_type, desc in guide['comparative_analysis'].items():
            if isinstance(desc, list):
                response += f"  {analysis_type.replace('_', ' ').title()}:\n"
                for item in desc:
                    response += f"    • {item}\n"
            else:
                response += f"  {analysis_type.replace('_', ' ').title()}: {desc}\n"

        response += "\n➡️  Next Steps:\n"
        for step, desc in guide['next_steps'].items():
            response += f"  • {step.title()}: {desc}\n"

        return response

    def _format_behavior_catalog_response(self, catalog: Dict[str, Any]) -> str:
        """Format behavior catalog"""
        response = "🌱 Bloom Behavior Catalog\n\nCommon Behaviors:\n"

        for behavior, description in catalog["common_behaviors"].items():
            response += f"  • {behavior}: {description}\n"

        response += "\n➕ Adding Custom Behaviors:\n"
        for step in catalog["adding_custom"]["steps"]:
            response += f"  {step}\n"

        response += "\n📚 Best Practices:\n"
        for practice in catalog["best_practices"]:
            response += f"  • {practice}\n"

        response += "\n🔬 Research Areas:\n"
        for area in catalog["research_areas"]:
            response += f"  • {area}\n"

        return response

    def _format_overview_response(self, info: Dict[str, Any]) -> str:
        """Format general overview"""
        response = "🌸 Bloom Framework Overview\n\n"

        response += f"{info['overview']['description']}\n"
        response += f"Approach: {info['overview']['approach']}\n"
        response += f"License: {info['overview']['license']}\n"

        response += "\n📋 Pipeline Stages:\n"
        for stage, details in info["pipeline_stages"].items():
            response += f"\n  {stage.upper()}:\n"
            response += f"    Purpose: {details['purpose']}\n"
            if isinstance(details.get('outputs'), list):
                response += f"    Outputs: {', '.join(details['outputs'])}\n"
            elif 'outputs' in details:
                response += f"    Outputs: {details['outputs']}\n"

        response += "\n🎯 Common Behaviors:\n"
        for behavior, desc in list(info["common_behaviors"].items())[:5]:
            response += f"  • {behavior}: {desc}\n"
        response += f"  ... and more\n"

        response += "\n🤖 Supported Providers:\n"
        for provider, models in info["supported_providers"].items():
            response += f"  • {provider.title()}: {models}\n"

        response += "\n📚 Resources:\n"
        response += "  • GitHub: https://github.com/isha-gpt/bloom\n"
        response += "  • Contact: isha.gpt@outlook.com\n"

        return response
