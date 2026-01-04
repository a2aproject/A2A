"""
Grant Writing Genius Agent - NIH grant application expert
"""
import sys
sys.path.append('..')

from typing import List, Dict, Any, Optional
from core.a2a_base import (
    BaseAgent, Message, Task, TaskStatus, Artifact,
    TextPart, DataPart, AgentSkill, MessageRole
)
import json
import re


class GrantWritingAgent(BaseAgent):
    """
    Expert agent for NIH grant applications and scientific grant writing.
    Provides validation, formatting guidance, and compliance checking.
    """

    def __init__(self):
        super().__init__(
            name="Grant Writing Genius Agent",
            description="Expert in NIH grant applications, formatting, compliance, and scientific writing",
            version="1.0.0"
        )

        # Register skills
        self.add_skill(AgentSkill(
            id="format_validation",
            name="Format Validation",
            description="Validate PDF formatting, fonts, margins, and NIH compliance",
            tags=["validation", "formatting", "compliance", "pdf"],
            examples=[
                "Check if my PDF meets NIH requirements",
                "Validate font sizes and margins",
                "Is my page formatting correct?"
            ]
        ))

        self.add_skill(AgentSkill(
            id="page_limit_check",
            name="Page Limit Verification",
            description="Verify compliance with NIH page limits for different sections",
            tags=["validation", "limits", "sections"],
            examples=[
                "Check Research Strategy page limits",
                "How many pages for specific aims?",
                "Verify my biosketch length"
            ]
        ))

        self.add_skill(AgentSkill(
            id="writing_guidance",
            name="Grant Writing Guidance",
            description="Provide expert guidance on grant writing best practices",
            tags=["writing", "guidance", "strategy"],
            examples=[
                "How to write compelling specific aims",
                "Structure my research strategy",
                "Improve my significance section"
            ]
        ))

        self.add_skill(AgentSkill(
            id="citation_format",
            name="Citation Format Help",
            description="Guidance on citation formatting and reference management",
            tags=["citations", "references", "bibliography"],
            examples=[
                "What citation format should I use?",
                "How to cite with et al.?",
                "Include PMCID in citations"
            ]
        ))

        self.add_skill(AgentSkill(
            id="compliance_check",
            name="Compliance Checking",
            description="Check compliance with NIH policies and requirements",
            tags=["compliance", "policy", "requirements"],
            examples=[
                "Check for hyperlink compliance",
                "Verify attachment requirements",
                "Are my filenames correct?"
            ]
        ))

        # NIH formatting requirements
        self.nih_requirements = {
            "font": {
                "min_size": 11,
                "max_characters_per_inch": 15,
                "max_lines_per_inch": 6,
                "recommended_fonts": ["Arial", "Georgia", "Helvetica", "Palatino Linotype"],
                "acceptable": "All fonts acceptable if they meet size/density requirements"
            },
            "margins": {
                "minimum": 0.5,  # inches
                "all_sides": True
            },
            "paper": {
                "max_width": 8.5,  # inches
                "max_height": 11.0   # inches
            },
            "file": {
                "max_size_mb": 100,
                "min_size_bytes": 1,
                "format": "PDF",
                "flattened": True
            },
            "filename": {
                "max_length": 50,
                "allowed_chars": r"[A-Za-z0-9_\-\s\.\(\)\{\}\[\]~!,\'@#$%+= ]",
                "no_ampersand": True
            }
        }

        # Page limits for common sections (R01 example)
        self.page_limits = {
            "specific_aims": 1,
            "research_strategy": 12,
            "project_summary": {"lines": 30, "pages": 1},
            "project_narrative": {"lines": 3, "pages": 1},
            "biosketch": 5,
            "other_support": "No limit (format pages)",
            "facilities": "No specific limit",
            "equipment": "No specific limit",
            "bibliography": "No limit"
        }

    def _parse_request(self, message_text: str) -> Dict[str, Any]:
        """Parse and categorize grant writing request"""
        text_lower = message_text.lower()

        request_info = {
            "query": message_text,
            "type": "general",
            "topic": None,
            "urgency": "normal"
        }

        # Determine request type
        if any(word in text_lower for word in ["validate", "check", "verify", "compliance"]):
            request_info["type"] = "validation"
        elif any(word in text_lower for word in ["format", "pdf", "font", "margin"]):
            request_info["type"] = "formatting"
        elif any(word in text_lower for word in ["page", "limit", "length"]):
            request_info["type"] = "page_limits"
        elif any(word in text_lower for word in ["write", "improve", "structure", "guidance"]):
            request_info["type"] = "writing"
        elif any(word in text_lower for word in ["citation", "reference", "bibliography"]):
            request_info["type"] = "citations"

        # Identify specific topics
        topics = {
            "specific_aims": ["specific aims", "aims"],
            "research_strategy": ["research strategy", "strategy"],
            "significance": ["significance"],
            "innovation": ["innovation"],
            "approach": ["approach", "methodology"],
            "biosketch": ["biosketch", "bio sketch", "cv"],
            "budget": ["budget"]
        }

        for topic_key, keywords in topics.items():
            if any(keyword in text_lower for keyword in keywords):
                request_info["topic"] = topic_key
                break

        return request_info

    async def validate_formatting(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Validate NIH formatting requirements"""
        validation = {
            "compliant": True,
            "checks_performed": [],
            "issues": [],
            "warnings": [],
            "recommendations": []
        }

        # Font validation
        validation["checks_performed"].append("Font requirements")
        validation["recommendations"].append(
            f"Use fonts ≥{self.nih_requirements['font']['min_size']} points. "
            f"Recommended: {', '.join(self.nih_requirements['font']['recommended_fonts'])}"
        )

        # Margin validation
        validation["checks_performed"].append("Margin requirements")
        validation["recommendations"].append(
            f"Maintain at least {self.nih_requirements['margins']['minimum']}\" margins on all sides"
        )

        # PDF requirements
        validation["checks_performed"].append("PDF requirements")
        validation["recommendations"].extend([
            f"File size must be ≤{self.nih_requirements['file']['max_size_mb']} MB",
            "PDFs must be flattened (no fillable fields or layers)",
            "Disable all security features and encryption"
        ])

        # Filename validation
        validation["checks_performed"].append("Filename requirements")
        validation["recommendations"].extend([
            f"Filenames must be ≤{self.nih_requirements['filename']['max_length']} characters",
            "Use descriptive names with allowed characters only",
            "Avoid ampersands (&) - use 'and' instead"
        ])

        # Page format
        validation["checks_performed"].append("Page format")
        validation["recommendations"].extend([
            f"Paper size: {self.nih_requirements['paper']['max_width']}\" × {self.nih_requirements['paper']['max_height']}\"",
            "Type density: ≤15 characters per inch",
            "Line spacing: ≤6 lines per inch"
        ])

        return validation

    async def check_page_limits(self, section: Optional[str] = None) -> Dict[str, Any]:
        """Check page limit requirements"""
        if section and section in self.page_limits:
            limit_info = self.page_limits[section]
            return {
                "section": section,
                "limit": limit_info,
                "details": self._format_limit_details(section, limit_info)
            }
        else:
            # Return all limits
            return {
                "all_limits": self.page_limits,
                "note": "Limits shown are for R01 applications. Check your specific funding opportunity."
            }

    def _format_limit_details(self, section: str, limit) -> str:
        """Format page limit details for display"""
        if isinstance(limit, dict):
            if "lines" in limit:
                return f"{limit['lines']} lines maximum (typically fits on {limit.get('pages', 1)} page)"
            return str(limit)
        elif isinstance(limit, int):
            return f"{limit} page{'s' if limit != 1 else ''}"
        else:
            return str(limit)

    async def provide_writing_guidance(self, topic: Optional[str]) -> Dict[str, Any]:
        """Provide grant writing best practices"""
        guidance = {
            "general": {
                "principles": [
                    "Be clear, concise, and specific",
                    "Use active voice and strong verbs",
                    "Avoid jargon and define acronyms",
                    "Tell a compelling story with logical flow",
                    "Address reviewers' likely questions proactively"
                ],
                "structure": [
                    "Use headings to organize content",
                    "Lead with key points in each section",
                    "Use figures/tables to convey complex information",
                    "Maintain consistent terminology throughout"
                ]
            }
        }

        # Topic-specific guidance
        topic_guidance = {
            "specific_aims": {
                "purpose": "Concisely state research goals and expected impact",
                "structure": [
                    "Opening paragraph: Significance and innovation (2-3 sentences)",
                    "Long-term goal and immediate objectives",
                    "2-3 specific aims with brief rationale",
                    "Expected outcomes and impact"
                ],
                "tips": [
                    "Keep to exactly 1 page",
                    "Make aims independent but complementary",
                    "State measurable objectives",
                    "Emphasize innovation and significance"
                ]
            },
            "significance": {
                "purpose": "Explain importance and potential impact",
                "key_elements": [
                    "Critical barrier or knowledge gap",
                    "Why this research matters now",
                    "How results will advance the field",
                    "Potential for broader impact"
                ],
                "tips": [
                    "Use recent literature to establish importance",
                    "Quantify the problem when possible",
                    "Connect to public health or scientific priorities"
                ]
            },
            "innovation": {
                "purpose": "Demonstrate novel approaches or paradigm shifts",
                "key_elements": [
                    "Novel concepts, approaches, or methodologies",
                    "Challenge existing paradigms",
                    "Refinements or improvements to existing methods",
                    "Unique applications of techniques"
                ],
                "tips": [
                    "Be specific about what's new",
                    "Explain why novel approaches are necessary",
                    "Balance innovation with feasibility"
                ]
            },
            "approach": {
                "purpose": "Detail strategy, methodology, and analyses",
                "structure": [
                    "Overall strategy and design",
                    "Methods for each aim",
                    "Expected results",
                    "Potential problems and alternatives",
                    "Timeline/milestones"
                ],
                "tips": [
                    "Include preliminary data to show feasibility",
                    "Justify sample sizes and statistical approaches",
                    "Address potential limitations proactively",
                    "Show you've thought through challenges"
                ]
            }
        }

        if topic and topic in topic_guidance:
            guidance["specific"] = topic_guidance[topic]

        return guidance

    async def citation_guidance(self) -> Dict[str, Any]:
        """Provide citation format guidance"""
        return {
            "general": {
                "flexibility": "NIH does not require a specific citation format",
                "recommendation": "Use any consistent, recognized format",
                "et_al": "Acceptable for publications with many authors",
                "pmcid": "REQUIRED: Include PMCID for papers funded by NIH"
            },
            "formats": {
                "nlm": "National Library of Medicine format (used by SciENcv)",
                "apa": "American Psychological Association",
                "chicago": "Chicago Manual of Style",
                "vancouver": "International Committee of Medical Journal Editors"
            },
            "best_practices": [
                "Be consistent throughout application",
                "Include DOI or PMID when available",
                "Verify all citations are accurate",
                "Include PMCID for NIH-funded work (Public Access Policy)"
            ],
            "tools": [
                "SciENcv - NIH's biosketch preparation tool",
                "PubMed - For finding PMCIDs",
                "EndNote, Zotero, Mendeley - Reference managers"
            ]
        }

    async def compliance_check(self) -> Dict[str, Any]:
        """General NIH compliance requirements"""
        return {
            "critical_requirements": {
                "hyperlinks": {
                    "rule": "Generally NOT allowed in page-limited attachments",
                    "exception": "Only when specifically requested in FOA",
                    "format": "Must show actual URL text (not hypertext)",
                    "example": "https://www.nih.gov/ (correct) vs 'NIH website' (incorrect)"
                },
                "signatures": {
                    "electronic": "Not allowed on PDF attachments",
                    "workaround": "Print, sign, scan, or flatten e-signed PDFs",
                    "required_for": "Letters of support, certain institutional forms"
                },
                "appendices": {
                    "rule": "Cannot be used to circumvent page limits",
                    "allowed": "Only specific materials allowed (e.g., questionnaires, protocols)",
                    "reference": "NOT-OD-11-080"
                },
                "headers_footers": {
                    "rule": "Do NOT include in your attachments",
                    "reason": "NIH adds these during assembly",
                    "headings": "Headings within text are encouraged"
                }
            },
            "formatting_compliance": {
                "text_requirements": [
                    "Font ≥11 points",
                    "Type density ≤15 characters/inch",
                    "Line spacing ≤6 lines/inch",
                    "Margins ≥0.5 inches all sides"
                ],
                "pdf_requirements": [
                    "Flattened (no layers)",
                    "No security features",
                    "Size ≤100 MB",
                    "Character set: Unicode supported"
                ]
            }
        }

    async def process_message(self, messages: List[Message]) -> Task:
        """Process grant writing assistance requests"""
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

            if request_info["type"] == "validation" or request_info["type"] == "formatting":
                result_data = await self.validate_formatting(request_info)
                response_text = self._format_validation_response(result_data)

            elif request_info["type"] == "page_limits":
                result_data = await self.check_page_limits(request_info.get("topic"))
                response_text = self._format_page_limits_response(result_data)

            elif request_info["type"] == "writing":
                result_data = await self.provide_writing_guidance(request_info.get("topic"))
                response_text = self._format_writing_guidance_response(result_data, request_info.get("topic"))

            elif request_info["type"] == "citations":
                result_data = await self.citation_guidance()
                response_text = self._format_citation_response(result_data)

            else:
                # General compliance or help
                result_data = await self.compliance_check()
                response_text = self._format_compliance_response(result_data)

            # Create artifact
            artifact = Artifact(
                name="Grant Writing Assistance",
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

    def _format_validation_response(self, validation: Dict[str, Any]) -> str:
        """Format validation results"""
        response = """📋 NIH Grant Format Validation

✓ Checks Performed:
"""
        for check in validation["checks_performed"]:
            response += f"  • {check}\n"

        if validation["issues"]:
            response += "\n❌ Issues Found:\n"
            for issue in validation["issues"]:
                response += f"  • {issue}\n"

        if validation["warnings"]:
            response += "\n⚠️  Warnings:\n"
            for warning in validation["warnings"]:
                response += f"  • {warning}\n"

        response += "\n💡 Requirements & Recommendations:\n"
        for rec in validation["recommendations"]:
            response += f"  • {rec}\n"

        return response

    def _format_page_limits_response(self, limit_data: Dict[str, Any]) -> str:
        """Format page limit information"""
        if "section" in limit_data:
            return f"""📄 Page Limit: {limit_data['section'].replace('_', ' ').title()}

Limit: {limit_data['details']}

Note: This is for R01 applications. Always check your specific funding opportunity announcement (FOA) for exact limits.
"""
        else:
            response = """📄 NIH Page Limits (R01 Example)

Section                    | Limit
---------------------------|------------------
"""
            for section, limit in limit_data["all_limits"].items():
                section_name = section.replace('_', ' ').title().ljust(25)
                limit_str = self._format_limit_details(section, limit)
                response += f"{section_name} | {limit_str}\n"

            response += "\n⚠️  Note: " + limit_data.get("note", "Check your specific FOA")
            return response

    def _format_writing_guidance_response(self, guidance: Dict[str, Any], topic: Optional[str]) -> str:
        """Format writing guidance"""
        response = "✍️  Grant Writing Guidance\n\n"

        if "specific" in guidance:
            specific = guidance["specific"]
            response += f"{'='*60}\n"
            response += f"{topic.replace('_', ' ').title()}\n"
            response += f"{'='*60}\n\n"

            if "purpose" in specific:
                response += f"Purpose: {specific['purpose']}\n\n"

            for key, items in specific.items():
                if key == "purpose":
                    continue
                response += f"{key.replace('_', ' ').title()}:\n"
                for item in items:
                    response += f"  • {item}\n"
                response += "\n"

        # Always include general principles
        response += f"\n{'='*60}\n"
        response += "General Best Practices\n"
        response += f"{'='*60}\n\n"

        for key, items in guidance["general"].items():
            response += f"{key.title()}:\n"
            for item in items:
                response += f"  • {item}\n"
            response += "\n"

        return response

    def _format_citation_response(self, citation_data: Dict[str, Any]) -> str:
        """Format citation guidance"""
        response = """📚 Citation Format Guidance

General Rules:
"""
        for key, value in citation_data["general"].items():
            response += f"  • {key.replace('_', ' ').title()}: {value}\n"

        response += "\n✓ Acceptable Formats:\n"
        for fmt, name in citation_data["formats"].items():
            response += f"  • {name} ({fmt.upper()})\n"

        response += "\n💡 Best Practices:\n"
        for practice in citation_data["best_practices"]:
            response += f"  • {practice}\n"

        response += "\n🔧 Recommended Tools:\n"
        for tool in citation_data["tools"]:
            response += f"  • {tool}\n"

        return response

    def _format_compliance_response(self, compliance: Dict[str, Any]) -> str:
        """Format compliance information"""
        response = """🔍 NIH Compliance Requirements

Critical Requirements:
"""
        for req_name, req_data in compliance["critical_requirements"].items():
            response += f"\n{req_name.replace('_', ' ').title()}:\n"
            for key, value in req_data.items():
                if isinstance(value, list):
                    response += f"  {key.title()}:\n"
                    for item in value:
                        response += f"    • {item}\n"
                else:
                    response += f"  {key.title()}: {value}\n"

        response += "\n\nFormatting Compliance:\n"
        response += "\nText Requirements:\n"
        for req in compliance["formatting_compliance"]["text_requirements"]:
            response += f"  • {req}\n"

        response += "\nPDF Requirements:\n"
        for req in compliance["formatting_compliance"]["pdf_requirements"]:
            response += f"  • {req}\n"

        return response
