"""
Dataset Ingestion Agent - Specialized in loading and analyzing Hugging Face datasets
"""
import sys
sys.path.append('..')

from typing import List, Dict, Any, Optional
from core.a2a_base import (
    BaseAgent, Message, Task, TaskStatus, Artifact,
    TextPart, DataPart, AgentSkill, MessageRole
)
import json


class DatasetAgent(BaseAgent):
    """
    Specialized agent for ingesting and analyzing Hugging Face datasets.
    Handles dataset loading, metadata extraction, and basic analysis.
    """

    def __init__(self):
        super().__init__(
            name="Dataset Ingestion Agent",
            description="Specialized agent for loading and analyzing Hugging Face datasets with ease",
            version="1.0.0"
        )

        # Register skills
        self.add_skill(AgentSkill(
            id="load_dataset",
            name="Load Dataset",
            description="Load datasets from Hugging Face hub with support for various configurations",
            tags=["data", "huggingface", "loading", "etl"],
            examples=[
                "Load GLUE dataset cola configuration",
                "Load nyu-mll/glue ax dataset",
                "Load dataset squad"
            ]
        ))

        self.add_skill(AgentSkill(
            id="analyze_dataset",
            name="Analyze Dataset",
            description="Provide detailed analysis of dataset structure, size, and schema",
            tags=["data", "analysis", "metadata"],
            examples=[
                "Analyze GLUE cola dataset",
                "What's the structure of the MNLI dataset?",
                "Show dataset statistics"
            ]
        ))

        self.add_skill(AgentSkill(
            id="dataset_info",
            name="Dataset Information",
            description="Retrieve comprehensive metadata about available datasets",
            tags=["metadata", "info", "documentation"],
            examples=[
                "What datasets are available in GLUE?",
                "Show me information about the SQuAD dataset"
            ]
        ))

        # Cache for loaded datasets
        self.dataset_cache: Dict[str, Any] = {}

    def _parse_dataset_request(self, message_text: str) -> Optional[Dict[str, str]]:
        """Extract dataset name and configuration from user message"""
        # Simple parsing - in production, use NLP
        text_lower = message_text.lower()

        # Common GLUE datasets
        glue_configs = ["cola", "sst2", "mrpc", "qqp", "stsb", "mnli", "qnli", "rte", "wnli", "ax"]

        result = {}

        for config in glue_configs:
            if config in text_lower:
                result['dataset'] = "nyu-mll/glue"
                result['config'] = config
                return result

        # Generic pattern matching
        if "load" in text_lower and "dataset" in text_lower:
            words = message_text.split()
            for i, word in enumerate(words):
                if word.lower() in ["load", "dataset"]:
                    if i + 1 < len(words):
                        potential_name = words[i + 1].strip('",\'')
                        result['dataset'] = potential_name
                        if i + 2 < len(words):
                            result['config'] = words[i + 2].strip('",\'')
                        return result

        return None

    async def load_huggingface_dataset(self, dataset_name: str, config: Optional[str] = None) -> Dict[str, Any]:
        """
        Load a dataset from Hugging Face hub.
        Returns dataset info and sample data.
        """
        cache_key = f"{dataset_name}:{config}" if config else dataset_name

        # Check cache
        if cache_key in self.dataset_cache:
            return {
                "status": "success",
                "source": "cache",
                "dataset": dataset_name,
                "config": config,
                "message": f"Dataset loaded from cache"
            }

        try:
            # Simulate dataset loading (in production, actually use datasets library)
            # from datasets import load_dataset
            # ds = load_dataset(dataset_name, config)

            # For this reference implementation, return structured info
            dataset_info = {
                "status": "success",
                "source": "huggingface",
                "dataset": dataset_name,
                "config": config,
                "splits": ["train", "validation", "test"] if config != "ax" else ["test"],
                "features": self._get_dataset_features(dataset_name, config),
                "sample_count": self._get_sample_count(dataset_name, config),
                "loading_code": self._generate_loading_code(dataset_name, config)
            }

            # Cache the result
            self.dataset_cache[cache_key] = dataset_info

            return dataset_info

        except Exception as e:
            return {
                "status": "error",
                "dataset": dataset_name,
                "config": config,
                "error": str(e)
            }

    def _get_dataset_features(self, dataset_name: str, config: Optional[str]) -> Dict[str, str]:
        """Get feature schema for known datasets"""
        # Hardcoded for common GLUE datasets (in production, get from actual dataset)
        glue_features = {
            "cola": {"sentence": "string", "label": "int (0-1)"},
            "mnli": {"premise": "string", "hypothesis": "string", "label": "int (0-2)"},
            "ax": {"premise": "string", "hypothesis": "string", "label": "int"},
            "sst2": {"sentence": "string", "label": "int (0-1)"},
            "mrpc": {"sentence1": "string", "sentence2": "string", "label": "int (0-1)"}
        }

        if "glue" in dataset_name.lower() and config:
            return glue_features.get(config, {"text": "string", "label": "int"})

        return {"text": "string", "label": "int"}

    def _get_sample_count(self, dataset_name: str, config: Optional[str]) -> Dict[str, int]:
        """Get approximate sample counts for known datasets"""
        # Hardcoded for demonstration
        glue_counts = {
            "cola": {"train": 8551, "validation": 1043, "test": 1063},
            "mnli": {"train": 392702, "validation_matched": 9815, "validation_mismatched": 9832, "test_matched": 9796, "test_mismatched": 9847},
            "ax": {"test": 1104}
        }

        if "glue" in dataset_name.lower() and config:
            return glue_counts.get(config, {"train": 1000, "test": 500})

        return {"train": 1000, "test": 500}

    def _generate_loading_code(self, dataset_name: str, config: Optional[str]) -> str:
        """Generate Python code to load the dataset"""
        if config:
            return f'''from datasets import load_dataset

ds = load_dataset("{dataset_name}", "{config}")

# Access splits
train_data = ds["train"]
validation_data = ds["validation"]  # if available
test_data = ds["test"]  # if available

# Show first example
print(train_data[0])'''
        else:
            return f'''from datasets import load_dataset

ds = load_dataset("{dataset_name}")

# Access splits
train_data = ds["train"]

# Show first example
print(train_data[0])'''

    async def process_message(self, messages: List[Message]) -> Task:
        """Process incoming messages and handle dataset operations"""
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

            # Parse dataset request
            dataset_request = self._parse_dataset_request(message_text)

            if dataset_request:
                # Load the dataset
                dataset_info = await self.load_huggingface_dataset(
                    dataset_request['dataset'],
                    dataset_request.get('config')
                )

                # Create response
                response_text = self._format_dataset_response(dataset_info)

                # Create artifact with dataset info
                artifact = Artifact(
                    name="Dataset Information",
                    description=f"Information about {dataset_request['dataset']}",
                    parts=[
                        TextPart(text=response_text),
                        DataPart(data=dataset_info, mimeType="application/json")
                    ]
                )

                self.add_artifact(task.id, artifact)
                self.update_task_status(task.id, TaskStatus.COMPLETED)

            else:
                # Provide general help
                help_text = self._generate_help_text()
                artifact = Artifact(
                    name="Dataset Agent Help",
                    description="How to use the Dataset Ingestion Agent",
                    parts=[TextPart(text=help_text)]
                )
                self.add_artifact(task.id, artifact)
                self.update_task_status(task.id, TaskStatus.COMPLETED)

        except Exception as e:
            self.update_task_status(task.id, TaskStatus.FAILED, error=str(e))

        return self.get_task(task.id)

    def _format_dataset_response(self, dataset_info: Dict[str, Any]) -> str:
        """Format dataset information into readable text"""
        if dataset_info['status'] == 'error':
            return f"❌ Error loading dataset: {dataset_info['error']}"

        response = f"""✓ Dataset Loaded Successfully

📊 Dataset: {dataset_info['dataset']}
⚙️  Configuration: {dataset_info['config']}
📁 Splits: {', '.join(dataset_info['splits'])}

📋 Features:
"""
        for feature, dtype in dataset_info['features'].items():
            response += f"  - {feature}: {dtype}\n"

        response += f"\n📈 Sample Counts:\n"
        for split, count in dataset_info['sample_count'].items():
            response += f"  - {split}: {count:,} examples\n"

        response += f"\n💻 Loading Code:\n```python\n{dataset_info['loading_code']}\n```"

        return response

    def _generate_help_text(self) -> str:
        """Generate help text for using this agent"""
        return """🤖 Dataset Ingestion Agent

I can help you load and analyze Hugging Face datasets with ease!

Available Skills:
1. Load Dataset - Load any dataset from Hugging Face hub
2. Analyze Dataset - Get detailed analysis of dataset structure
3. Dataset Info - Retrieve metadata about datasets

Example requests:
- "Load GLUE cola dataset"
- "Load nyu-mll/glue mnli"
- "Analyze the ax dataset"
- "What's in the GLUE benchmark?"

Supported GLUE datasets: cola, sst2, mrpc, qqp, stsb, mnli, qnli, rte, wnli, ax
"""
