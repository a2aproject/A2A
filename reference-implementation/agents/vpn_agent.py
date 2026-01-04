"""
VPN Setup Agent - Outline SDK specialist for VPN and network circumvention
"""
import sys
sys.path.append('..')

from typing import List, Dict, Any, Optional
from core.a2a_base import (
    BaseAgent, Message, Task, TaskStatus, Artifact,
    TextPart, DataPart, AgentSkill, MessageRole
)
import json


class VPNAgent(BaseAgent):
    """
    Specialist agent for VPN setup and network circumvention using Outline SDK.
    Provides guidance on Outline deployment, configuration, and troubleshooting.
    """

    def __init__(self):
        super().__init__(
            name="VPN Setup Agent",
            description="Expert in VPN setup, Outline SDK, and network circumvention technologies",
            version="1.0.0"
        )

        # Register skills
        self.add_skill(AgentSkill(
            id="outline_setup",
            name="Outline VPN Setup",
            description="Guide users through Outline Server and Client setup",
            tags=["outline", "vpn", "setup", "deployment"],
            examples=[
                "How to set up Outline Server",
                "Deploy Outline on DigitalOcean",
                "Configure Outline Manager"
            ]
        ))

        self.add_skill(AgentSkill(
            id="sdk_integration",
            name="Outline SDK Integration",
            description="Integrate Outline SDK into applications for network protection",
            tags=["sdk", "integration", "development", "golang"],
            examples=[
                "Integrate Outline SDK in my app",
                "Use Outline SDK with Go",
                "Add circumvention to Android app"
            ]
        ))

        self.add_skill(AgentSkill(
            id="circumvention_strategies",
            name="Circumvention Strategies",
            description="Recommend strategies to bypass different types of network blocking",
            tags=["circumvention", "blocking", "strategies", "evasion"],
            examples=[
                "Bypass DNS blocking",
                "Evade SNI-based censorship",
                "Configure domain fronting"
            ]
        ))

        self.add_skill(AgentSkill(
            id="troubleshooting",
            name="VPN Troubleshooting",
            description="Diagnose and fix Outline and VPN connectivity issues",
            tags=["troubleshooting", "debugging", "connectivity"],
            examples=[
                "Outline server not connecting",
                "Debug connection issues",
                "Test proxy connectivity"
            ]
        ))

        self.add_skill(AgentSkill(
            id="platform_guidance",
            name="Multi-Platform Deployment",
            description="Platform-specific guidance for Android, iOS, Windows, macOS, Linux",
            tags=["platform", "deployment", "mobile", "desktop"],
            examples=[
                "Deploy on Android",
                "iOS Outline integration",
                "Linux VPN setup"
            ]
        ))

        # Outline SDK knowledge base
        self.outline_info = {
            "overview": {
                "description": "Open-source toolkit for network-level interference protection",
                "proven": "Field-tested by millions of Outline users",
                "multi_platform": ["Android", "iOS", "Windows", "macOS", "Linux"],
                "module_path": "golang.getoutline.org/sdk"
            },
            "core_concepts": {
                "connections": {
                    "StreamConn": "Stream-based (like TCP, SOCK_STREAM)",
                    "PacketConn": "Datagram-based (like UDP, SOCK_DGRAM)"
                },
                "dialers": {
                    "StreamDialer": "Creates StreamConn connections",
                    "PacketDialer": "Creates PacketConn connections",
                    "nesting": "Dialers can be nested for layered transports"
                },
                "resolvers": "DNS question answering (dns.Resolver)"
            },
            "bypass_strategies": {
                "dns_blocking": [
                    "Encrypted DNS over HTTPS (DoH) or TLS (DoT)",
                    "Alternative resolver hosts/ports",
                    "Address override configuration"
                ],
                "sni_blocking": [
                    "TCP stream fragmentation (transport/split)",
                    "TLS record fragmentation (transport/tlsfrag)",
                    "Domain fronting (transport/tls)",
                    "SNI hiding"
                ],
                "proxy_tunneling": [
                    "Shadowsocks (transport/shadowsocks)",
                    "SOCKS5 (transport/socks5)"
                ]
            },
            "integration_methods": {
                "mobile_library": {
                    "platforms": ["Android", "iOS", "macOS"],
                    "method": "gomobile bind",
                    "outputs": ["AAR (Android)", "Framework (Apple)"],
                    "note": "Easiest for mobile apps"
                },
                "side_service": {
                    "platforms": ["Windows", "Linux", "Android"],
                    "method": "Standalone Go binary with IPC",
                    "note": "Not available on iOS"
                },
                "go_library": {
                    "platforms": ["All"],
                    "method": "Direct Go import",
                    "note": "Best for Go applications"
                },
                "c_library": {
                    "platforms": ["All"],
                    "method": "CGo with //export",
                    "note": "For C/C++ applications"
                }
            }
        }

    def _parse_request(self, message_text: str) -> Dict[str, Any]:
        """Parse VPN/Outline request"""
        text_lower = message_text.lower()

        request_info = {
            "query": message_text,
            "type": "general",
            "platform": None,
            "technology": None
        }

        # Determine request type
        if any(word in text_lower for word in ["setup", "install", "deploy", "configure"]):
            request_info["type"] = "setup"
        elif any(word in text_lower for word in ["integrate", "sdk", "development", "code"]):
            request_info["type"] = "integration"
        elif any(word in text_lower for word in ["bypass", "circumvent", "evade", "block"]):
            request_info["type"] = "circumvention"
        elif any(word in text_lower for word in ["troubleshoot", "debug", "fix", "issue", "problem"]):
            request_info["type"] = "troubleshooting"

        # Identify platform
        platforms = {
            "android": ["android"],
            "ios": ["ios", "iphone", "ipad"],
            "macos": ["macos", "mac os", "osx"],
            "windows": ["windows", "win"],
            "linux": ["linux", "ubuntu", "debian"]
        }

        for platform, keywords in platforms.items():
            if any(keyword in text_lower for keyword in keywords):
                request_info["platform"] = platform
                break

        # Identify technology
        technologies = ["outline", "shadowsocks", "socks5", "dns", "sni", "tls", "vpn"]
        for tech in technologies:
            if tech in text_lower:
                request_info["technology"] = tech
                break

        return request_info

    async def provide_outline_setup(self, platform: Optional[str]) -> Dict[str, Any]:
        """Provide Outline setup instructions"""
        setup_guide = {
            "general": {
                "step1": "Install Outline Manager (on your computer)",
                "step2": "Deploy Outline Server (on cloud provider)",
                "step3": "Get access key from Manager",
                "step4": "Install Outline Client (on devices)",
                "step5": "Import access key and connect"
            },
            "server_deployment": {
                "supported_providers": [
                    "DigitalOcean",
                    "Google Cloud",
                    "Amazon EC2",
                    "Custom Server (Linux)"
                ],
                "quick_steps": [
                    "Open Outline Manager",
                    "Click 'Set up' or 'Add Server'",
                    "Choose provider or manual setup",
                    "Follow provider-specific instructions",
                    "Wait for server deployment (2-5 minutes)"
                ]
            },
            "client_installation": {
                "Android": {
                    "source": "Google Play Store or GitHub",
                    "package": "org.outline.android.client",
                    "manual": "https://github.com/Tuesdaythe13th/outline-apps"
                },
                "iOS": {
                    "source": "Apple App Store",
                    "search": "Outline VPN"
                },
                "Windows": {
                    "source": "https://getoutline.org/",
                    "installer": "Outline-Client.exe"
                },
                "macOS": {
                    "source": "https://getoutline.org/",
                    "installer": "Outline-Client.dmg"
                },
                "Linux": {
                    "source": "https://getoutline.org/",
                    "format": "AppImage"
                }
            },
            "access_keys": {
                "format": "ss://[base64]@[server]:[port]",
                "sharing": "Each user should have unique key (recommended)",
                "management": "Add/remove keys in Outline Manager",
                "security": "Keep keys private, don't share publicly"
            }
        }

        return setup_guide

    async def provide_sdk_integration(self, platform: Optional[str]) -> Dict[str, Any]:
        """Provide SDK integration guidance"""
        integration_guide = {
            "getting_started": {
                "module_path": "golang.getoutline.org/sdk",
                "installation": "go get golang.getoutline.org/sdk@v0.0.21-alpha.1",
                "documentation": "https://pkg.go.dev/golang.getoutline.org/sdk"
            },
            "mobile_integration": {
                "method": "Generated Mobile Library (recommended for mobile)",
                "steps": [
                    "Create Go package wrapping SDK functionality",
                    "Use 'gomobile bind' to generate bindings",
                    "Android: Generates AAR with Java bindings",
                    "iOS/macOS: Generates Framework with Objective-C bindings",
                    "Integrate generated library into app"
                ],
                "example": "See MobileProxy for easiest mobile integration",
                "note": "Must use gomobile bind on your package, not directly on SDK"
            },
            "desktop_integration": {
                "method": "Side Service (Electron/desktop apps)",
                "steps": [
                    "Build Go binary with SDK",
                    "Implement IPC mechanism (sockets/stdio)",
                    "Bundle binary with application",
                    "Launch as subprocess",
                    "Communicate via IPC"
                ],
                "examples": [
                    "Outline Electron backend",
                    "Outline Windows/Linux Client"
                ]
            },
            "go_integration": {
                "method": "Direct import",
                "example_code": """
import (
    "golang.getoutline.org/sdk/transport"
    "golang.getoutline.org/sdk/transport/shadowsocks"
)

// Create Shadowsocks dialer
dialer, err := shadowsocks.NewStreamDialer(&transport.TCPDialer{}, accessKey)

// Create connection
conn, err := dialer.Dial(ctx, "example.com:443")
""",
                "use_cases": [
                    "Command-line tools",
                    "Go-based servers",
                    "GUI apps with Go frameworks (Wails, Fyne)"
                ]
            },
            "key_packages": {
                "transport": "Core connection abstractions",
                "transport/shadowsocks": "Shadowsocks protocol",
                "transport/socks5": "SOCKS5 protocol",
                "transport/split": "TCP fragmentation",
                "transport/tlsfrag": "TLS fragmentation",
                "dns": "DNS resolution utilities",
                "network": "TUN-based VPN (tun2socks)"
            }
        }

        return integration_guide

    async def provide_circumvention_strategies(self, blocking_type: Optional[str]) -> Dict[str, Any]:
        """Recommend circumvention strategies"""
        strategies = {
            "dns_blocking": {
                "description": "ISP blocks DNS queries to prevent domain resolution",
                "solutions": [
                    {
                        "method": "Encrypted DNS (DoH/DoT)",
                        "implementation": "Use dns package with encrypted resolver",
                        "example": "DoH: https://8.8.8.8/dns-query, DoT: 8.8.8.8:853",
                        "effectiveness": "High"
                    },
                    {
                        "method": "Alternative Resolvers",
                        "implementation": "Configure alternative DNS hosts/ports",
                        "example": "Cloudflare 1.1.1.1, Google 8.8.8.8",
                        "effectiveness": "Medium"
                    },
                    {
                        "method": "Address Override",
                        "implementation": "Force specific IP addresses",
                        "example": "override:host=1.2.3.4",
                        "effectiveness": "High (if you know the IP)"
                    }
                ]
            },
            "sni_blocking": {
                "description": "Deep packet inspection blocks based on SNI in TLS handshake",
                "solutions": [
                    {
                        "method": "TCP Stream Fragmentation",
                        "package": "transport/split",
                        "description": "Split TCP packets to obscure SNI",
                        "effectiveness": "High"
                    },
                    {
                        "method": "TLS Record Fragmentation",
                        "package": "transport/tlsfrag",
                        "description": "Fragment TLS records containing SNI",
                        "effectiveness": "Very High"
                    },
                    {
                        "method": "Domain Fronting",
                        "package": "transport/tls",
                        "description": "Use CDN with different SNI and Host header",
                        "example": "SNI: cloudflare.net, Host: blocked-site.com",
                        "effectiveness": "Very High"
                    }
                ]
            },
            "ip_blocking": {
                "description": "ISP blocks connections to specific IP addresses",
                "solutions": [
                    {
                        "method": "Shadowsocks",
                        "package": "transport/shadowsocks",
                        "description": "Encrypted proxy protocol",
                        "setup": "Deploy Outline Server for easy Shadowsocks",
                        "effectiveness": "Very High"
                    },
                    {
                        "method": "SOCKS5 over SSH",
                        "package": "transport/socks5",
                        "description": "Tunnel through SSH connection",
                        "effectiveness": "High"
                    }
                ]
            },
            "combined_approach": {
                "description": "Layer multiple strategies for maximum effectiveness",
                "example": "override:host=cloudflare.net|tlsfrag:1",
                "note": "Outline SDK allows composition of transports"
            }
        }

        return strategies

    async def provide_troubleshooting(self) -> Dict[str, Any]:
        """Provide troubleshooting guidance"""
        return {
            "common_issues": {
                "cannot_connect": {
                    "symptoms": ["Connection timeout", "No response from server"],
                    "checks": [
                        "Verify server is running (check cloud provider)",
                        "Check firewall rules allow UDP and TCP",
                        "Confirm access key is correct",
                        "Test server from different network",
                        "Check server logs in Manager"
                    ],
                    "tools": [
                        "test-connectivity tool from SDK",
                        "Outline Manager diagnostics"
                    ]
                },
                "slow_connection": {
                    "symptoms": ["High latency", "Slow download speed"],
                    "checks": [
                        "Test without VPN to isolate issue",
                        "Try server in different region",
                        "Check server bandwidth limits",
                        "Verify server has enough resources",
                        "Test different circumvention strategies"
                    ],
                    "tools": [
                        "fetch-speed tool from SDK",
                        "Standard speedtest"
                    ]
                },
                "intermittent_drops": {
                    "symptoms": ["Connection drops randomly", "Must reconnect"],
                    "checks": [
                        "Check for ISP throttling or blocking",
                        "Verify server stability",
                        "Try different transport configurations",
                        "Check client device power settings",
                        "Monitor server resource usage"
                    ]
                },
                "app_integration_issues": {
                    "symptoms": ["SDK not working in app", "Build errors"],
                    "checks": [
                        "Verify module path (golang.getoutline.org/sdk)",
                        "Check Go version compatibility",
                        "Confirm proper gomobile setup (mobile)",
                        "Review integration method docs",
                        "Check SDK examples"
                    ]
                }
            },
            "diagnostic_tools": {
                "resolve": "Test DNS resolution",
                "fetch": "Test URL fetching with transport",
                "http2transport": "Run local forward proxy",
                "test-connectivity": "Test proxy connectivity",
                "fetch-speed": "Measure download speed"
            },
            "getting_help": {
                "github": "https://github.com/Jigsaw-Code/outline-sdk/issues",
                "outline_support": "https://support.getoutline.org/",
                "community": "GitHub Discussions"
            }
        }

    async def process_message(self, messages: List[Message]) -> Task:
        """Process VPN/Outline assistance requests"""
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

            if request_info["type"] == "setup":
                result_data = await self.provide_outline_setup(request_info.get("platform"))
                response_text = self._format_setup_response(result_data, request_info.get("platform"))

            elif request_info["type"] == "integration":
                result_data = await self.provide_sdk_integration(request_info.get("platform"))
                response_text = self._format_integration_response(result_data, request_info.get("platform"))

            elif request_info["type"] == "circumvention":
                result_data = await self.provide_circumvention_strategies(request_info.get("technology"))
                response_text = self._format_circumvention_response(result_data)

            elif request_info["type"] == "troubleshooting":
                result_data = await self.provide_troubleshooting()
                response_text = self._format_troubleshooting_response(result_data)

            else:
                # General overview
                result_data = self.outline_info
                response_text = self._format_overview_response(result_data)

            # Create artifact
            artifact = Artifact(
                name="VPN Setup Assistance",
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

    def _format_setup_response(self, guide: Dict[str, Any], platform: Optional[str]) -> str:
        """Format setup instructions"""
        response = """🔧 Outline VPN Setup Guide

General Setup Process:
"""
        for step, instruction in guide["general"].items():
            response += f"  {step.replace('step', 'Step ')}: {instruction}\n"

        response += "\n📡 Server Deployment:\n"
        response += f"  Supported Providers: {', '.join(guide['server_deployment']['supported_providers'])}\n\n"
        response += "  Quick Steps:\n"
        for step in guide["server_deployment"]["quick_steps"]:
            response += f"    • {step}\n"

        if platform:
            response += f"\n📱 Client Installation ({platform.title()}):\n"
            if platform in guide["client_installation"]:
                client_info = guide["client_installation"][platform]
                for key, value in client_info.items():
                    response += f"  {key.title()}: {value}\n"
        else:
            response += "\n📱 Client Installation:\n"
            for plat, info in guide["client_installation"].items():
                response += f"\n  {plat}:\n"
                response += f"    Source: {info['source']}\n"

        response += "\n🔑 Access Keys:\n"
        for key, value in guide["access_keys"].items():
            response += f"  {key.title()}: {value}\n"

        response += "\n🌐 Resources:\n"
        response += "  • Official Site: https://getoutline.org/\n"
        response += "  • GitHub: https://github.com/Tuesdaythe13th/outline-apps\n"

        return response

    def _format_integration_response(self, guide: Dict[str, Any], platform: Optional[str]) -> str:
        """Format SDK integration guidance"""
        response = """💻 Outline SDK Integration Guide

Getting Started:
"""
        for key, value in guide["getting_started"].items():
            response += f"  {key.replace('_', ' ').title()}: {value}\n"

        if platform in ["android", "ios", "macos"]:
            response += "\n📱 Mobile Integration (Recommended):\n"
            for key, value in guide["mobile_integration"].items():
                if isinstance(value, list):
                    response += f"  {key.title()}:\n"
                    for item in value:
                        response += f"    {item}\n"
                else:
                    response += f"  {key.title()}: {value}\n"

        elif platform in ["windows", "linux"]:
            response += "\n🖥️  Desktop Integration (Side Service):\n"
            for key, value in guide["desktop_integration"].items():
                if isinstance(value, list):
                    response += f"  {key.title()}:\n"
                    for item in value:
                        response += f"    • {item}\n"
                else:
                    response += f"  {key.title()}: {value}\n"

        else:
            response += "\n🔧 Go Integration:\n"
            response += f"  Method: {guide['go_integration']['method']}\n\n"
            response += "  Example Code:\n"
            response += guide['go_integration']['example_code']

        response += "\n\n📦 Key Packages:\n"
        for pkg, desc in guide["key_packages"].items():
            response += f"  • {pkg}: {desc}\n"

        return response

    def _format_circumvention_response(self, strategies: Dict[str, Any]) -> str:
        """Format circumvention strategies"""
        response = """🛡️  Network Circumvention Strategies

"""
        for block_type, info in strategies.items():
            if block_type == "combined_approach":
                continue

            response += f"\n{block_type.replace('_', ' ').upper()}:\n"
            response += f"{info['description']}\n\n"
            response += "Solutions:\n"

            for sol in info["solutions"]:
                response += f"\n  • {sol['method']}\n"
                for key, value in sol.items():
                    if key != "method":
                        response += f"    {key.title()}: {value}\n"

        if "combined_approach" in strategies:
            response += f"\n\n🔗 COMBINED APPROACH (Most Effective):\n"
            response += f"  {strategies['combined_approach']['description']}\n"
            response += f"  Example: {strategies['combined_approach']['example']}\n"
            response += f"  Note: {strategies['combined_approach']['note']}\n"

        return response

    def _format_troubleshooting_response(self, guide: Dict[str, Any]) -> str:
        """Format troubleshooting guide"""
        response = """🔍 Outline VPN Troubleshooting

Common Issues:
"""
        for issue, details in guide["common_issues"].items():
            response += f"\n{issue.replace('_', ' ').upper()}:\n"
            if "symptoms" in details:
                response += "  Symptoms:\n"
                for symptom in details["symptoms"]:
                    response += f"    • {symptom}\n"
            if "checks" in details:
                response += "  What to Check:\n"
                for check in details["checks"]:
                    response += f"    • {check}\n"
            if "tools" in details:
                response += "  Diagnostic Tools:\n"
                for tool in details["tools"]:
                    response += f"    • {tool}\n"

        response += "\n\n🛠️  Diagnostic Tools:\n"
        for tool, desc in guide["diagnostic_tools"].items():
            response += f"  • {tool}: {desc}\n"
            response += f"    Usage: go run golang.getoutline.org/sdk/x/tools/{tool}@latest\n"

        response += "\n\n💬 Getting Help:\n"
        for source, link in guide["getting_help"].items():
            response += f"  • {source.replace('_', ' ').title()}: {link}\n"

        return response

    def _format_overview_response(self, info: Dict[str, Any]) -> str:
        """Format general overview"""
        response = """🌐 Outline SDK Overview

"""
        response += f"Description: {info['overview']['description']}\n"
        response += f"Module Path: {info['overview']['module_path']}\n"
        response += f"Platforms: {', '.join(info['overview']['multi_platform'])}\n"

        response += "\n\nCore Concepts:\n"
        for concept, details in info["core_concepts"].items():
            response += f"\n{concept.title()}:\n"
            if isinstance(details, dict):
                for key, value in details.items():
                    response += f"  • {key}: {value}\n"
            else:
                response += f"  {details}\n"

        response += "\n\nBypass Strategies:\n"
        for strategy, methods in info["bypass_strategies"].items():
            response += f"\n{strategy.replace('_', ' ').title()}:\n"
            for method in methods:
                response += f"  • {method}\n"

        response += "\n\n📚 Learn More:\n"
        response += "  • Website: https://getoutline.org/\n"
        response += "  • SDK Docs: https://pkg.go.dev/golang.getoutline.org/sdk\n"
        response += "  • GitHub: https://github.com/Jigsaw-Code/outline-sdk\n"

        return response
