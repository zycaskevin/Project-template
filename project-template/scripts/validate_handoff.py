#!/usr/bin/env python3
"""
Handoff JSON Validation Script

Purpose: Validate Enhanced Handoff Protocol v2.0 JSON files
Features:
  - JSON Schema validation
  - Auto-complete timestamp, hash
  - Token count check
  - Domain-specific extension validation

Usage:
  python validate_handoff.py path/to/handoff.json
  python validate_handoff.py path/to/handoff.json --auto-fix
  python validate_handoff.py path/to/handoff.json --strict

Version: 1.0
Author: Claude Code + zycaskevin
"""

import json
import hashlib
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Schema version
SCHEMA_VERSION = "2.0.0"

# Token limits
TOKEN_LIMITS = {
    "summary.keyFindings": 500,
    "summary.cumulativeSummary": 300,
    "memoryChain[].cumulativeSummary": 400,
    "memoryChain": 1500,  # Total memoryChain limit
    "businessContext": 800,
    "productContext": 600,
    "technicalContext": 700,
    "developmentContext": 600,
}


def estimate_tokens(text: str) -> int:
    """Estimate token count (rough approximation: 4 chars = 1 token)"""
    return len(text) // 4


def calculate_hash(content: str) -> str:
    """Calculate SHA-256 hash for content"""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def get_current_timestamp() -> str:
    """Get current UTC timestamp in ISO format"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_schema_structure(data: Dict) -> List[str]:
    """Validate basic JSON schema structure"""
    errors = []

    # Required top-level fields
    required_fields = ["schemaVersion", "from", "to", "summary", "artifacts", "metadata"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Check schemaVersion
    if "schemaVersion" in data and data["schemaVersion"] != SCHEMA_VERSION:
        errors.append(f"Schema version mismatch: expected {SCHEMA_VERSION}, got {data['schemaVersion']}")

    # Validate 'from' structure
    if "from" in data:
        from_data = data["from"]
        if "agentType" not in from_data:
            errors.append("'from.agentType' is required")
        if "timestamp" not in from_data:
            errors.append("'from.timestamp' is required")
        if "stageType" not in from_data:
            errors.append("'from.stageType' is required")

    # Validate 'to' structure
    if "to" in data:
        to_data = data["to"]
        if "agentType" not in to_data:
            errors.append("'to.agentType' is required")
        if "requiredContext" not in to_data or not isinstance(to_data["requiredContext"], list):
            errors.append("'to.requiredContext' must be an array")

    # Validate 'summary' structure
    if "summary" in data:
        summary = data["summary"]
        if "keyFindings" not in summary or not isinstance(summary["keyFindings"], list):
            errors.append("'summary.keyFindings' must be an array")
        if "decisions" not in summary or not isinstance(summary["decisions"], list):
            errors.append("'summary.decisions' must be an array")

    # Validate 'artifacts' structure
    if "artifacts" in data:
        if not isinstance(data["artifacts"], list):
            errors.append("'artifacts' must be an array")
        else:
            for i, artifact in enumerate(data["artifacts"]):
                if "type" not in artifact:
                    errors.append(f"artifacts[{i}]: 'type' is required")
                if "path" not in artifact:
                    errors.append(f"artifacts[{i}]: 'path' is required")

    # Validate 'metadata' structure
    if "metadata" in data:
        metadata = data["metadata"]
        if "tokensUsed" not in metadata:
            errors.append("'metadata.tokensUsed' is required")

    return errors


def validate_decisions(decisions: List[Dict]) -> List[str]:
    """Validate decision structure"""
    errors = []

    for i, decision in enumerate(decisions):
        if "decision" not in decision:
            errors.append(f"decisions[{i}]: 'decision' is required")
        if "rationale" not in decision:
            errors.append(f"decisions[{i}]: 'rationale' is required")
        if "source" not in decision:
            errors.append(f"decisions[{i}]: 'source' is required (for traceability)")
        # alternatives is optional but recommended
        if "alternatives" in decision and not isinstance(decision["alternatives"], list):
            errors.append(f"decisions[{i}]: 'alternatives' must be an array")

    return errors


def validate_assumptions(assumptions: List[Dict]) -> List[str]:
    """Validate assumptions structure"""
    errors = []

    for i, assumption in enumerate(assumptions):
        if "assumption" not in assumption:
            errors.append(f"assumptions[{i}]: 'assumption' is required")
        if "needsValidation" not in assumption:
            errors.append(f"assumptions[{i}]: 'needsValidation' is required")
        if "priority" not in assumption:
            errors.append(f"assumptions[{i}]: 'priority' is required (high/medium/low)")
        elif assumption["priority"] not in ["high", "medium", "low"]:
            errors.append(f"assumptions[{i}]: 'priority' must be high/medium/low")

    return errors


def validate_token_limits(data: Dict) -> List[str]:
    """Validate token count limits"""
    warnings = []

    # Check summary.keyFindings
    if "summary" in data and "keyFindings" in data["summary"]:
        findings_text = " ".join(data["summary"]["keyFindings"])
        tokens = estimate_tokens(findings_text)
        limit = TOKEN_LIMITS["summary.keyFindings"]
        if tokens > limit:
            warnings.append(f"summary.keyFindings exceeds token limit: {tokens} > {limit}")

    # Check memoryChain total
    if "memoryChain" in data:
        total_tokens = 0
        for i, stage in enumerate(data["memoryChain"]):
            if "cumulativeSummary" in stage:
                tokens = estimate_tokens(stage["cumulativeSummary"])
                total_tokens += tokens
                limit = TOKEN_LIMITS["memoryChain[].cumulativeSummary"]
                if tokens > limit:
                    warnings.append(f"memoryChain[{i}].cumulativeSummary exceeds limit: {tokens} > {limit}")

        limit = TOKEN_LIMITS["memoryChain"]
        if total_tokens > limit:
            warnings.append(f"memoryChain total tokens exceed limit: {total_tokens} > {limit}")

    # Check domain-specific contexts
    for context_key in ["businessContext", "productContext", "technicalContext", "developmentContext"]:
        if context_key in data:
            context_text = json.dumps(data[context_key])
            tokens = estimate_tokens(context_text)
            limit = TOKEN_LIMITS.get(context_key, 800)
            if tokens > limit:
                warnings.append(f"{context_key} exceeds token limit: {tokens} > {limit}")

    return warnings


def auto_fix_handoff(data: Dict, handoff_file_path: str = None) -> Tuple[Dict, List[str]]:
    """Auto-fix missing fields

    Args:
        data: Handoff JSON data
        handoff_file_path: Path to the handoff JSON file (for resolving relative paths)
    """
    fixes = []

    # Auto-complete timestamp if missing
    if "from" in data and "timestamp" not in data["from"]:
        data["from"]["timestamp"] = get_current_timestamp()
        fixes.append("Added 'from.timestamp'")

    # Auto-complete hash for artifacts
    if "artifacts" in data:
        # Get handoff directory for resolving relative paths
        handoff_dir = Path(handoff_file_path).parent.absolute() if handoff_file_path else Path.cwd()

        for i, artifact in enumerate(data["artifacts"]):
            if "hash" not in artifact and "path" in artifact:
                try:
                    artifact_path = artifact["path"]
                    file_path = Path(artifact_path)

                    # If path is not absolute, resolve it relative to handoff directory
                    if not file_path.is_absolute():
                        file_path = (handoff_dir / artifact_path).resolve()

                    if file_path.exists():
                        content = file_path.read_text(encoding="utf-8")
                        artifact["hash"] = f"sha256:{calculate_hash(content)}"
                        fixes.append(f"Added hash for artifacts[{i}]: {artifact['path']}")
                except Exception as e:
                    fixes.append(f"Could not generate hash for artifacts[{i}]: {e}")

    # Auto-calculate tokensUsed if missing
    if "metadata" in data and "tokensUsed" not in data["metadata"]:
        total_tokens = estimate_tokens(json.dumps(data))
        data["metadata"]["tokensUsed"] = total_tokens
        fixes.append(f"Added 'metadata.tokensUsed': {total_tokens}")

    # Set schemaVersion if missing
    if "schemaVersion" not in data:
        data["schemaVersion"] = SCHEMA_VERSION
        fixes.append(f"Added 'schemaVersion': {SCHEMA_VERSION}")

    return data, fixes


def validate_handoff_file(file_path: str, auto_fix: bool = False, strict: bool = False) -> bool:
    """
    Validate a handoff JSON file

    Args:
        file_path: Path to the JSON file
        auto_fix: Automatically fix missing fields
        strict: Treat warnings as errors

    Returns:
        True if validation passes, False otherwise
    """
    try:
        # Read JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"\n🔍 Validating: {file_path}")
        print(f"Schema Version: {data.get('schemaVersion', 'MISSING')}\n")

        # Auto-fix if requested
        if auto_fix:
            data, fixes = auto_fix_handoff(data, file_path)
            if fixes:
                print("🔧 Auto-fixes applied:")
                for fix in fixes:
                    print(f"  - {fix}")
                print()

                # Write back fixed data
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"✅ Updated: {file_path}\n")

        # Validate schema structure
        errors = validate_schema_structure(data)

        # Validate decisions
        if "summary" in data and "decisions" in data["summary"]:
            errors.extend(validate_decisions(data["summary"]["decisions"]))

        # Validate assumptions
        if "summary" in data and "assumptions" in data["summary"]:
            errors.extend(validate_assumptions(data["summary"]["assumptions"]))

        # Check token limits (warnings)
        warnings = validate_token_limits(data)

        # Print results
        if errors:
            print("❌ Validation Errors:")
            for error in errors:
                print(f"  - {error}")
            print()

        if warnings:
            severity = "❌ Errors" if strict else "⚠️  Warnings"
            print(f"{severity} (Token Limits):")
            for warning in warnings:
                print(f"  - {warning}")
            print()

        # Determine pass/fail
        has_errors = len(errors) > 0
        has_warnings = len(warnings) > 0

        if has_errors:
            print(f"❌ Validation FAILED: {len(errors)} error(s)")
            return False
        elif has_warnings and strict:
            print(f"❌ Validation FAILED (strict mode): {len(warnings)} warning(s)")
            return False
        elif has_warnings:
            print(f"⚠️  Validation PASSED with {len(warnings)} warning(s)")
            return True
        else:
            print("✅ Validation PASSED: No errors or warnings")
            return True

    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Validate Enhanced Handoff Protocol v2.0 JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_handoff.py handoff.json
  python validate_handoff.py handoff.json --auto-fix
  python validate_handoff.py handoff.json --strict

Exit codes:
  0 - Validation passed
  1 - Validation failed
        """
    )
    parser.add_argument("file", help="Path to handoff JSON file")
    parser.add_argument("--auto-fix", action="store_true", help="Automatically fix missing fields")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    args = parser.parse_args()

    success = validate_handoff_file(args.file, auto_fix=args.auto_fix, strict=args.strict)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
