"""
AWS Lambda Handler for MCP Auto-Compression Server

Endpoints:
  - POST /mcp: Main MCP server endpoint (Streamable HTTP protocol)
  - POST /compress: Compress conversation context
  - POST /handoff: Generate handoff.json
  - GET /mcp/health: Health check

Version: 1.0
Author: Claude Code + zycaskevin
Based on: MCP Streamable HTTP Protocol (2025-03-26)
"""

import json
import os
import boto3
from datetime import datetime
from typing import Dict, List, Any
import hashlib

# Initialize S3 client
s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'mcp-compression-dev')

# Configuration
TOKEN_THRESHOLD = int(os.environ.get('TOKEN_THRESHOLD', 70))
CONTEXT_WINDOW = int(os.environ.get('CONTEXT_WINDOW', 200000))


# ============================================================
# Token Estimation
# ============================================================
def estimate_tokens(text: str) -> int:
    """Estimate token count (4 chars ≈ 1 token)"""
    return len(text) // 4


# ============================================================
# Context Compression (Factory.ai 2025 Strategy)
# ============================================================
class ContextCompressor:
    """
    Compress context based on Factory.ai 2025 best practices:
    - Session intent (what are we trying to accomplish)
    - High-level play-by-play (key steps taken)
    - Artifact trails (files created/modified)
    - Breadcrumbs (file paths, function names, identifiers)
    """

    def compress(self, conversation: str) -> Dict:
        """Compress conversation into essential components"""

        # Extract session intent (simplified for Lambda)
        session_intent = self._extract_intent(conversation)

        # Extract key actions
        play_by_play = self._extract_actions(conversation)

        # Extract artifacts
        artifacts = self._extract_artifacts(conversation)

        # Extract breadcrumbs
        breadcrumbs = self._extract_breadcrumbs(conversation)

        original_tokens = estimate_tokens(conversation)
        compressed_data = {
            "sessionIntent": session_intent,
            "playByPlay": play_by_play,
            "artifacts": artifacts,
            "breadcrumbs": breadcrumbs
        }
        compressed_tokens = estimate_tokens(json.dumps(compressed_data))

        return {
            "compressed": compressed_data,
            "metadata": {
                "originalTokens": original_tokens,
                "compressedTokens": compressed_tokens,
                "compressionRate": 1.0 - (compressed_tokens / original_tokens) if original_tokens > 0 else 0.0,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }

    def _extract_intent(self, text: str) -> List[str]:
        """Extract session intent"""
        lines = text.split('\n')
        user_messages = [line for line in lines if 'user:' in line.lower()][:3]
        return [msg.split(':', 1)[1].strip() for msg in user_messages if ':' in msg]

    def _extract_actions(self, text: str) -> List[str]:
        """Extract key actions"""
        keywords = ['created', 'modified', 'deleted', 'fixed', 'implemented', 'commit']
        lines = text.split('\n')
        actions = []
        for line in lines:
            if any(kw in line.lower() for kw in keywords):
                actions.append(line.strip()[:100])
        return list(dict.fromkeys(actions))[:20]  # Top 20, deduplicated

    def _extract_artifacts(self, text: str) -> List[str]:
        """Extract file artifacts"""
        extensions = ['.py', '.js', '.ts', '.md', '.json', '.yaml', '.sh']
        artifacts = []
        for ext in extensions:
            if ext in text:
                words = text.split()
                for word in words:
                    if ext in word and ('/' in word or '\\' in word):
                        artifacts.append(word.strip(',:;()[]{}"\' '))
        return list(dict.fromkeys(artifacts))

    def _extract_breadcrumbs(self, text: str) -> List[str]:
        """Extract code breadcrumbs"""
        patterns = ['def ', 'class ', 'function ', 'const ']
        breadcrumbs = []
        for pattern in patterns:
            if pattern in text:
                lines = text.split('\n')
                for line in lines:
                    if pattern in line:
                        identifier = line.split(pattern, 1)[1].split('(')[0].strip()
                        if identifier:
                            breadcrumbs.append(f"{pattern.strip()}: {identifier}")
        return list(dict.fromkeys(breadcrumbs))[:30]


# ============================================================
# Lambda Handlers
# ============================================================
def health_handler(event, context):
    """Health check endpoint"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'healthy',
            'service': 'mcp-auto-compression',
            'version': '1.0',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
    }


def compress_handler(event, context):
    """Handle /compress endpoint"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        conversation = body.get('conversation', '')

        if not conversation:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing conversation field'})
            }

        # Compress context
        compressor = ContextCompressor()
        result = compressor.compress(conversation)

        # Store compressed result in S3 (optional)
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        s3_key = f"compressed/{timestamp}.json"

        try:
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=json.dumps(result),
                ContentType='application/json'
            )
        except Exception as e:
            print(f"Warning: Failed to store in S3: {e}")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'compressed': result['compressed'],
                'metadata': result['metadata'],
                's3_location': f"s3://{BUCKET_NAME}/{s3_key}"
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def handoff_handler(event, context):
    """Handle /handoff endpoint - Generate handoff.json"""
    try:
        body = json.loads(event.get('body', '{}'))
        from_agent = body.get('from_agent')
        to_agent = body.get('to_agent')
        compressed_context = body.get('compressed_context', {})

        if not from_agent or not to_agent:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing from_agent or to_agent'})
            }

        # Generate handoff template
        handoff = {
            "schemaVersion": "2.0.0",
            "from": {
                "agentType": from_agent,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "stageType": "planning"
            },
            "to": {
                "agentType": to_agent,
                "requiredContext": [],
                "expectedOutputs": []
            },
            "summary": {
                "keyFindings": compressed_context.get("sessionIntent", []),
                "compressedContext": compressed_context
            },
            "metadata": {
                "tokensUsed": compressed_context.get("compressedTokens", 0),
                "compressionRate": compressed_context.get("compressionRate", 0.0)
            }
        }

        # Store handoff in S3
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        s3_key = f"handoffs/{from_agent}-to-{to_agent}-{timestamp}.json"

        try:
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=json.dumps(handoff, indent=2),
                ContentType='application/json'
            )
        except Exception as e:
            print(f"Warning: Failed to store handoff in S3: {e}")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'handoff': handoff,
                's3_location': f"s3://{BUCKET_NAME}/{s3_key}"
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def mcp_handler(event, context):
    """Main MCP Server endpoint (Streamable HTTP protocol)"""

    # Handle health check
    if event.get('rawPath') == '/mcp/health':
        return health_handler(event, context)

    try:
        body = json.loads(event.get('body', '{}'))
        method = body.get('method')
        params = body.get('params', {})

        # MCP Protocol: Handle different methods
        if method == 'compress':
            return compress_handler(event, context)
        elif method == 'handoff':
            return handoff_handler(event, context)
        elif method == 'ping':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'result': 'pong'})
            }
        else:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'Unknown method: {method}'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
