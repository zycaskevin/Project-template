#!/usr/bin/env python3
"""
Handoff Template Generator

Purpose: Generate Enhanced Handoff Protocol v2.0 JSON templates
Features:
  - Generate templates based on agent type
  - Include domain-specific extensions
  - Pre-fill common fields
  - Support different transition types

Usage:
  python generate_handoff_template.py --from research --to implementation
  python generate_handoff_template.py --from tdd.red --to tdd.green --output handoff.json
  python generate_handoff_template.py --list-agents

Version: 1.0
Author: Claude Code + zycaskevin
"""

import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

# Schema version
SCHEMA_VERSION = "2.0.0"

# Agent configurations
AGENTS = {
    "research": {
        "agentType": "小研 (Research Analyst)",
        "stageType": "planning.pre-business",
        "requiredContext": ["industryTrends", "competitorAnalysis", "marketSize"],
        "expectedOutputs": ["industry_analysis.md", "market_research.md"],
        "domainExtensions": ["businessContext"]
    },
    "marketing": {
        "agentType": "小市 (Market Strategist)",
        "stageType": "planning.pre-business",
        "requiredContext": ["targetAudience", "competitiveAdvantage", "marketingChannels"],
        "expectedOutputs": ["marketing_strategy.md", "go_to_market_plan.md"],
        "domainExtensions": ["businessContext"]
    },
    "product": {
        "agentType": "小品 (Product Manager)",
        "stageType": "planning.pre-business",
        "requiredContext": ["userStories", "featurePriority", "successMetrics"],
        "expectedOutputs": ["PRD.md", "feature_specs.md"],
        "domainExtensions": ["businessContext", "productContext"]
    },
    "architect": {
        "agentType": "小架 (Architect)",
        "stageType": "planning.architecture",
        "requiredContext": ["systemRequirements", "scalabilityNeeds", "techStack"],
        "expectedOutputs": ["architecture_design.md", "system_diagram.md"],
        "domainExtensions": ["productContext", "technicalContext"]
    },
    "developer": {
        "agentType": "小程 (Developer)",
        "stageType": "tdd.green",
        "requiredContext": ["failingTests", "implementationGuidelines", "codeStandards"],
        "expectedOutputs": ["src/**/*.py", "implementation.md"],
        "domainExtensions": ["technicalContext", "developmentContext"]
    },
    "qa": {
        "agentType": "小質 (QA Expert)",
        "stageType": "tdd.red",
        "requiredContext": ["featureSpecs", "acceptanceCriteria", "edgeCases"],
        "expectedOutputs": ["tests/**/*.py", "features/*.feature"],
        "domainExtensions": ["developmentContext"]
    },
    "implementation": {
        "agentType": "實作階段",
        "stageType": "tdd.green",
        "requiredContext": ["coreProtocolChanges", "remainingP0Tasks", "toolImplementationPriority"],
        "expectedOutputs": ["validate_handoff.py", "generate_handoff_template.py"],
        "domainExtensions": ["technicalContext", "developmentContext"]
    },
    "tdd.red": {
        "agentType": "TDD Red Phase",
        "stageType": "tdd.red",
        "requiredContext": ["featureSpecs", "testCases", "edgeCases"],
        "expectedOutputs": ["tests/**/*.py", "features/*.feature"],
        "domainExtensions": ["developmentContext"]
    },
    "tdd.green": {
        "agentType": "TDD Green Phase",
        "stageType": "tdd.green",
        "requiredContext": ["failingTests", "implementationPlan", "codeStandards"],
        "expectedOutputs": ["src/**/*.py"],
        "domainExtensions": ["technicalContext", "developmentContext"]
    },
    "tdd.refactor": {
        "agentType": "TDD Refactor Phase",
        "stageType": "tdd.refactor",
        "requiredContext": ["passingTests", "refactoringOpportunities", "qualityMetrics"],
        "expectedOutputs": ["src/**/*.py (refactored)"],
        "domainExtensions": ["technicalContext", "developmentContext"]
    },
    "delivery": {
        "agentType": "交付階段",
        "stageType": "delivery",
        "requiredContext": ["completedFeatures", "testResults", "performanceMetrics"],
        "expectedOutputs": ["README.md", "CHANGELOG.md", "RELEASE_NOTES.md"],
        "domainExtensions": ["developmentContext"]
    }
}


def get_current_timestamp() -> str:
    """Get current UTC timestamp in ISO format"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_base_template(from_agent: str, to_agent: str) -> Dict:
    """Generate base handoff template structure"""
    from_config = AGENTS.get(from_agent, {})
    to_config = AGENTS.get(to_agent, {})

    template = {
        "schemaVersion": SCHEMA_VERSION,
        "from": {
            "agentType": from_config.get("agentType", from_agent),
            "timestamp": get_current_timestamp(),
            "stageType": from_config.get("stageType", "planning")
        },
        "to": {
            "agentType": to_config.get("agentType", to_agent),
            "requiredContext": to_config.get("requiredContext", []),
            "expectedOutputs": to_config.get("expectedOutputs", [])
        },
        "summary": {
            "keyFindings": [
                "TODO: Add key finding 1",
                "TODO: Add key finding 2",
                "TODO: Add key finding 3"
            ],
            "decisions": [
                {
                    "decision": "TODO: Describe the decision made",
                    "rationale": "TODO: Explain why this decision was made",
                    "source": "TODO: Reference source (e.g., file:line or meeting notes)",
                    "alternatives": [
                        "TODO: Alternative 1 (explain why not chosen)",
                        "TODO: Alternative 2 (explain why not chosen)"
                    ]
                }
            ],
            "assumptions": [
                {
                    "assumption": "TODO: State the assumption",
                    "needsValidation": True,
                    "priority": "high",
                    "validationMethod": "TODO: How to validate this assumption"
                }
            ]
        },
        "artifacts": [
            {
                "type": "markdown",
                "path": "TODO: path/to/file.md",
                "sections": ["TODO: Section 1", "TODO: Section 2"],
                "hash": "TODO: sha256:... (auto-generated by validate_handoff.py --auto-fix)",
                "changes": ["TODO: Describe changes made"]
            }
        ],
        "metadata": {
            "tokensUsed": 0,  # Will be auto-calculated
            "fullOutputPath": "TODO: data/handoffs/full_output.jsonl (optional)",
            "compressionRate": 0.0,
            "protectedContent": [
                "TODO: Content that must not be compressed"
            ]
        }
    }

    return template


def add_domain_extensions(template: Dict, from_agent: str, to_agent: str) -> Dict:
    """Add domain-specific extensions based on agent types"""
    from_extensions = AGENTS.get(from_agent, {}).get("domainExtensions", [])
    to_extensions = AGENTS.get(to_agent, {}).get("domainExtensions", [])

    # Combine unique extensions
    extensions = list(set(from_extensions + to_extensions))

    # Add businessContext if needed
    if "businessContext" in extensions:
        template["businessContext"] = {
            "industryInsights": "TODO: Key industry trends and insights",
            "competitors": [
                {
                    "name": "TODO: Competitor name",
                    "strengths": "TODO: Their strengths",
                    "weaknesses": "TODO: Their weaknesses"
                }
            ],
            "userPersonas": [
                {
                    "type": "TODO: Persona type (e.g., Enterprise IT Manager)",
                    "painPoints": "TODO: Key pain points",
                    "goals": "TODO: User goals"
                }
            ]
        }

    # Add productContext if needed
    if "productContext" in extensions:
        template["productContext"] = {
            "requirements": [
                {
                    "id": "REQ-001",
                    "description": "TODO: Requirement description",
                    "priority": "high"
                }
            ],
            "constraints": [
                "TODO: Technical constraint 1",
                "TODO: Business constraint 2"
            ],
            "apiContracts": [
                {
                    "endpoint": "TODO: /api/v1/endpoint",
                    "method": "GET",
                    "description": "TODO: Endpoint description"
                }
            ]
        }

    # Add technicalContext if needed
    if "technicalContext" in extensions:
        template["technicalContext"] = {
            "architectureDecisions": [
                {
                    "decision": "TODO: Architecture decision",
                    "rationale": "TODO: Why this was chosen",
                    "tradeoffs": "TODO: Tradeoffs considered"
                }
            ],
            "designPatterns": [
                "TODO: Pattern 1 (e.g., Repository Pattern)",
                "TODO: Pattern 2 (e.g., Factory Pattern)"
            ],
            "technicalDebt": [
                {
                    "description": "TODO: Technical debt item",
                    "impact": "medium",
                    "proposedSolution": "TODO: How to address it"
                }
            ]
        }

    # Add developmentContext if needed
    if "developmentContext" in extensions:
        template["developmentContext"] = {
            "codeChanges": [
                {
                    "file": "TODO: src/module/file.py",
                    "linesChanged": 0,
                    "changeType": "added/modified/deleted",
                    "description": "TODO: What was changed and why"
                }
            ],
            "testCases": [
                {
                    "name": "TODO: test_feature_name",
                    "status": "passing/failing",
                    "coverage": "TODO: 85%"
                }
            ],
            "qualityMetrics": {
                "cyclomaticComplexity": 0.0,
                "testCoverage": 0.0,
                "codeSmells": 0
            }
        }

    # Add memoryChain for cumulative context
    template["memoryChain"] = [
        {
            "stage": from_agent,
            "agents": [template["from"]["agentType"]],
            "cumulativeSummary": "TODO: Cumulative summary of this stage (<300 tokens)",
            "artifacts": [
                "TODO: path/to/artifact1.md",
                "TODO: path/to/artifact2.json"
            ],
            "extendsFrom": None  # Or previous stage name
        }
    ]

    return template


def list_available_agents():
    """List all available agent types"""
    print("\n📋 Available Agent Types:\n")
    print(f"{'Agent ID':<20} {'Agent Type':<30} {'Stage':<30}")
    print("-" * 80)
    for agent_id, config in AGENTS.items():
        print(f"{agent_id:<20} {config['agentType']:<30} {config['stageType']:<30}")
    print("\nUsage:")
    print("  python generate_handoff_template.py --from research --to product")
    print("  python generate_handoff_template.py --from tdd.red --to tdd.green\n")


def generate_handoff_template(from_agent: str, to_agent: str, output_path: str = None) -> Dict:
    """
    Generate a complete handoff template

    Args:
        from_agent: Source agent ID
        to_agent: Target agent ID
        output_path: Optional output file path

    Returns:
        Generated template dictionary
    """
    # Validate agents
    if from_agent not in AGENTS:
        print(f"❌ Unknown 'from' agent: {from_agent}")
        print("Run with --list-agents to see available agents")
        return None

    if to_agent not in AGENTS:
        print(f"❌ Unknown 'to' agent: {to_agent}")
        print("Run with --list-agents to see available agents")
        return None

    # Generate base template
    template = generate_base_template(from_agent, to_agent)

    # Add domain extensions
    template = add_domain_extensions(template, from_agent, to_agent)

    # Save to file if output path specified
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Generated handoff template: {output_file}")
        print(f"   From: {AGENTS[from_agent]['agentType']}")
        print(f"   To: {AGENTS[to_agent]['agentType']}")
        print(f"\n📝 Next steps:")
        print(f"   1. Edit {output_file} and replace all 'TODO' placeholders")
        print(f"   2. Run: python validate_handoff.py {output_file} --auto-fix")
        print(f"   3. Verify: python validate_handoff.py {output_file}\n")
    else:
        print("\n✅ Generated handoff template (printed to stdout):")
        print(json.dumps(template, indent=2, ensure_ascii=False))

    return template


def main():
    parser = argparse.ArgumentParser(
        description="Generate Enhanced Handoff Protocol v2.0 JSON templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available agents
  python generate_handoff_template.py --list-agents

  # Generate template and save to file
  python generate_handoff_template.py --from research --to product --output handoff.json

  # Generate template to stdout
  python generate_handoff_template.py --from tdd.red --to tdd.green

Common workflows:
  Pre-Business: research → marketing → product → architect
  TDD Cycle: tdd.red → tdd.green → tdd.refactor
  Delivery: tdd.refactor → delivery
        """
    )
    parser.add_argument("--from", dest="from_agent", help="Source agent ID")
    parser.add_argument("--to", dest="to_agent", help="Target agent ID")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    parser.add_argument("--list-agents", action="store_true", help="List available agent types")

    args = parser.parse_args()

    if args.list_agents:
        list_available_agents()
        return

    if not args.from_agent or not args.to_agent:
        parser.print_help()
        print("\n❌ Error: Both --from and --to are required (or use --list-agents)")
        return

    generate_handoff_template(args.from_agent, args.to_agent, args.output)


if __name__ == "__main__":
    main()
