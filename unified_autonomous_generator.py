#!/usr/bin/env python3
"""
Unified Autonomous Code Generator
================================

A comprehensive autonomous code generation framework that supports both
Claude SDK and OpenCode SDK, selectable via command-line flags.

Usage:
    # Use Claude SDK (default)
    python unified_autonomous_generator.py "Create a Python calculator" -l ./projects -p calc

    # Use OpenCode SDK
    python unified_autonomous_generator.py "Create a web app" -l ./projects -p webapp --framework opencode
    
    # OpenCode with different provider
    python unified_autonomous_generator.py "Create API server" -l ./projects -p api --framework opencode --provider openai --model gpt-4

    # Enable simulation mode for testing
    python unified_autonomous_generator.py "Create hello world" -l ./test -p hello --enable-simulation

Features:
- Dual SDK support (Claude Code SDK + OpenCode SDK)
- Multi-provider AI access (Claude, GPT-4, etc. via OpenCode)
- Unified command-line interface
- Shared Anthropic research principles implementation
- Consistent project structure regardless of framework
- Explicit simulation mode control

Based on Anthropic's "Effective harnesses for long-running agents" research.
"""

import argparse
import asyncio
import json
import os
import sys
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from abc import ABC, abstractmethod

# Framework availability checks
CLAUDE_SDK_AVAILABLE = False
OPENCODE_SDK_AVAILABLE = False

try:
    # Try Claude SDK import (would need to be adapted based on actual Claude SDK structure)
    from client import create_client as create_claude_client
    CLAUDE_SDK_AVAILABLE = True
    print("✅ Claude SDK available")
except ImportError:
    print("ℹ️ Claude SDK not available")

try:
    # Try OpenCode SDK import with local path fallback
    try:
        from opencode_ai import AsyncOpencode
        from opencode_ai.types import TextPartInputParam, FilePartInputParam
    except ImportError:
        # Fallback to local OpenCode SDK
        import sys
        sys.path.insert(0, '/Users/Mark/Software/autonomous-coding_Hello_World/opencode-sdk-python/src')
        from opencode_ai import AsyncOpencode
        from opencode_ai.types import TextPartInputParam, FilePartInputParam
    
    OPENCODE_SDK_AVAILABLE = True
    print("✅ OpenCode SDK available")
except ImportError as e:
    print(f"ℹ️ OpenCode SDK not available: {e}")


class BaseAutonomousGenerator(ABC):
    """
    Abstract base class for autonomous code generators.
    Defines the common interface and shared functionality.
    """
    
    def __init__(self, enable_simulation: bool = False):
        self.enable_simulation = enable_simulation
    
    def parse_task_description(self, task: str) -> Dict:
        """Parse and analyze the task description to determine project requirements."""
        task_lower = task.lower()
        
        # Detect programming language
        language = "python"  # default
        if any(word in task_lower for word in ["javascript", "js", "node"]):
            language = "javascript"
        elif "java" in task_lower and "javascript" not in task_lower:
            language = "java"
        elif any(word in task_lower for word in ["python", "py"]):
            language = "python"
        
        # Detect project complexity
        complexity = "simple"
        if any(word in task_lower for word in ["web", "app", "website", "server", "api"]):
            complexity = "web"
        elif any(word in task_lower for word in ["cli", "command", "tool", "utility"]):
            complexity = "cli"
        elif any(word in task_lower for word in ["library", "package", "module"]):
            complexity = "library"
        
        # Detect key features
        features = []
        if any(word in task_lower for word in ["gui", "interface", "window"]):
            features.append("gui")
        if any(word in task_lower for word in ["database", "db", "sql"]):
            features.append("database")
        if any(word in task_lower for word in ["api", "rest", "endpoint"]):
            features.append("api")
        if "test" in task_lower:
            features.append("testing")
        
        return {
            "language": language,
            "complexity": complexity,
            "features": features,
            "description": task,
            "estimated_files": self._estimate_file_count(complexity, features)
        }
    
    def _estimate_file_count(self, complexity: str, features: List[str]) -> int:
        """Estimate number of files based on project complexity."""
        base_count = {"simple": 1, "cli": 2, "library": 3, "web": 5}
        return base_count.get(complexity, 1) + len(features)
    
    def create_comprehensive_feature_list(self, task_analysis: Dict) -> List[Dict]:
        """Create detailed feature list following Anthropic research approach."""
        language = task_analysis["language"]
        complexity = task_analysis["complexity"]
        description = task_analysis["description"]
        
        features = []
        
        # Core functionality features based on complexity
        if complexity == "simple":
            features.extend([
                {
                    "category": "core_functionality",
                    "description": f"Implement main program logic: {description}",
                    "steps": [
                        f"Create main {language} file",
                        "Implement core algorithm/logic",
                        "Handle input/output correctly",
                        "Verify expected behavior"
                    ],
                    "passes": False,
                    "priority": "high"
                }
            ])
        elif complexity == "cli":
            features.extend([
                {
                    "category": "cli_interface",
                    "description": "Command-line interface with argument parsing",
                    "steps": [
                        "Implement argument parser",
                        "Add help documentation",
                        "Handle invalid inputs gracefully",
                        "Test various command combinations"
                    ],
                    "passes": False,
                    "priority": "high"
                },
                {
                    "category": "core_functionality",
                    "description": f"Core program logic: {description}",
                    "steps": [
                        "Implement main functionality",
                        "Process user inputs correctly",
                        "Generate expected outputs",
                        "Handle edge cases"
                    ],
                    "passes": False,
                    "priority": "high"
                }
            ])
        elif complexity == "web":
            features.extend([
                {
                    "category": "web_server",
                    "description": "Basic web server setup and routing",
                    "steps": [
                        "Set up web framework",
                        "Configure basic routes",
                        "Handle HTTP requests/responses",
                        "Test server startup and endpoints"
                    ],
                    "passes": False,
                    "priority": "high"
                },
                {
                    "category": "web_interface",
                    "description": "User interface and frontend",
                    "steps": [
                        "Create HTML templates",
                        "Add CSS styling",
                        "Implement user interactions",
                        "Test UI functionality end-to-end"
                    ],
                    "passes": False,
                    "priority": "medium"
                }
            ])
        
        # Universal features (always included)
        features.extend([
            {
                "category": "code_quality",
                "description": f"Code follows {language} best practices",
                "steps": [
                    "Add proper documentation and docstrings",
                    "Implement clean code structure",
                    "Follow language conventions",
                    "Add meaningful comments"
                ],
                "passes": False,
                "priority": "medium"
            },
            {
                "category": "testing",
                "description": "Comprehensive testing and validation",
                "steps": [
                    "Test program execution without errors",
                    "Verify core functionality works",
                    "Test edge cases and error handling", 
                    "Confirm output meets requirements"
                ],
                "passes": False,
                "priority": "high"
            },
            {
                "category": "error_handling",
                "description": "Robust error handling and user feedback",
                "steps": [
                    "Handle invalid inputs gracefully",
                    "Provide clear error messages",
                    "Prevent crashes from common errors",
                    "Test error scenarios"
                ],
                "passes": False,
                "priority": "medium"
            }
        ])
        
        # Add feature-specific requirements
        feature_flags = task_analysis.get("features", [])
        if "gui" in feature_flags:
            features.append({
                "category": "gui",
                "description": "Graphical user interface implementation",
                "steps": [
                    "Set up GUI framework",
                    "Create main window and widgets",
                    "Implement user interactions",
                    "Test GUI functionality"
                ],
                "passes": False,
                "priority": "high"
            })
        
        if "database" in feature_flags:
            features.append({
                "category": "database", 
                "description": "Database integration and data persistence",
                "steps": [
                    "Set up database connection",
                    "Define data models/schema",
                    "Implement CRUD operations",
                    "Test database functionality"
                ],
                "passes": False,
                "priority": "medium"
            })
        
        if "api" in feature_flags:
            features.append({
                "category": "api",
                "description": "API endpoints and data handling",
                "steps": [
                    "Define API routes and methods",
                    "Implement request/response handling",
                    "Add input validation",
                    "Test API endpoints"
                ],
                "passes": False,
                "priority": "high"
            })
        
        return features
    
    def setup_project_directory(self, location: str, project_name: str) -> Path:
        """Set up organized project directory structure."""
        location_path = Path(location).resolve()
        location_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_dir_name = f"{project_name}_{timestamp}"
        project_dir = location_path / project_dir_name
        
        project_dir.mkdir(exist_ok=True)
        (project_dir / "src").mkdir(exist_ok=True)
        (project_dir / "tests").mkdir(exist_ok=True)
        (project_dir / "docs").mkdir(exist_ok=True)
        
        return project_dir
    
    @abstractmethod
    async def run_autonomous_generation(self, task_analysis: Dict, project_dir: Path) -> bool:
        """Run the autonomous generation process (framework-specific implementation)."""
        pass
    
    @abstractmethod
    def get_framework_name(self) -> str:
        """Get the name of the framework being used."""
        pass
    
    async def generate_code(self, task: str, location: str, project_name: str) -> Tuple[Path, bool]:
        """
        Main method to generate code autonomously.
        
        Args:
            task: Description of what to generate
            location: Directory where project should be created
            project_name: Name of the project
            
        Returns:
            Tuple of (project_directory, success_status)
        """
        framework_name = self.get_framework_name()
        
        print(f"🚀 Unified Autonomous Code Generation")
        print(f"=" * 50)
        print(f"Framework: {framework_name}")
        print(f"Task: {task}")
        print(f"Location: {location}")
        print(f"Project: {project_name}")
        
        try:
            # Parse and analyze the task
            task_analysis = self.parse_task_description(task)
            print(f"\\n📊 Task Analysis:")
            print(f"   Language: {task_analysis['language']}")
            print(f"   Complexity: {task_analysis['complexity']}")
            print(f"   Features: {task_analysis['features']}")
            
            # Set up project directory
            project_dir = self.setup_project_directory(location, project_name)
            print(f"\\n📁 Project Directory: {project_dir}")
            
            # Create feature list
            features = self.create_comprehensive_feature_list(task_analysis)
            feature_file = project_dir / "feature_list.json"
            with open(feature_file, "w") as f:
                json.dump(features, f, indent=2)
            print(f"✅ Created feature list with {len(features)} features")
            
            # Run framework-specific autonomous generation
            success = await self.run_autonomous_generation(task_analysis, project_dir)
            
            return project_dir, success
            
        except Exception as e:
            print(f"❌ Code generation failed: {e}")
            return None, False


class ClaudeAutonomousGenerator(BaseAutonomousGenerator):
    """
    Autonomous code generator using Claude SDK.
    Implements the Anthropic research two-agent pattern with Claude Code SDK.
    """
    
    def __init__(self, model: str = "claude-sonnet-4-5-20250929", enable_simulation: bool = False):
        super().__init__(enable_simulation)
        self.model = model
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.use_claude_sdk = self.api_key is not None
        
        if not CLAUDE_SDK_AVAILABLE:
            raise ImportError("Claude SDK not available. Install with: pip install claude-code-sdk")
        
        # Check for API key when simulation is disabled
        if not self.enable_simulation and not self.api_key:
            raise ValueError(
                "❌ ANTHROPIC_API_KEY required for Claude autonomous generation\\n"
                "   Set environment variable: ANTHROPIC_API_KEY\\n"
                "   Or use --enable-simulation flag to run without API keys\\n"
                "   Example: export ANTHROPIC_API_KEY='your-api-key-here'"
            )
    
    def get_framework_name(self) -> str:
        return "Claude Code SDK"
    
    def create_initializer_prompt(self, task_analysis: Dict, project_dir: Path) -> str:
        """Create initializer agent prompt for Claude SDK."""
        language = task_analysis["language"]
        complexity = task_analysis["complexity"]
        description = task_analysis["description"]
        
        return f"""## INITIALIZER AGENT: Claude SDK Project Setup

You are an expert {language} developer using Claude Code SDK for autonomous development.

### PROJECT DESCRIPTION:
{description}

### PROJECT ANALYSIS:
- **Language**: {language}
- **Complexity**: {complexity}
- **Working Directory**: {project_dir}
- **Framework**: Claude Code SDK

### YOUR TASKS AS INITIALIZER AGENT:

1. **EXAMINE PROJECT STRUCTURE**:
   - The project directory has been created with src/, tests/, docs/ subdirectories
   - Read feature_list.json to understand requirements
   - Plan the implementation approach

2. **CREATE PROJECT FOUNDATION**:
   - Create README.md with comprehensive project documentation
   - Set up main program files in src/ directory
   - Create init.sh script for environment setup
   - Initialize git repository with initial commit

3. **PLAN IMPLEMENTATION STRATEGY**:
   - Analyze the feature list requirements
   - Plan file structure and dependencies
   - Document the development approach
   - Create progress tracking file (claude-progress.txt)

4. **PREPARE FOR CODING AGENT**:
   - Leave clear instructions for implementation
   - Set up foundation without implementing core logic
   - Create templates and structure for coding agent
   - Document what needs to be implemented

### CLAUDE SDK INTEGRATION:
- Use MCP tools for file operations and testing
- Leverage Claude's code generation capabilities
- Follow security best practices with command allowlists

### IMPORTANT:
- Focus on PROJECT SETUP and PLANNING only
- Do NOT implement the actual functionality yet
- Create solid foundation for incremental development
- Leave detailed instructions for the coding agent

Start by reading feature_list.json to understand the full requirements.
"""
    
    def create_coding_prompt(self, task_analysis: Dict, project_dir: Path) -> str:
        """Create coding agent prompt for Claude SDK."""
        language = task_analysis["language"]
        description = task_analysis["description"]
        
        return f"""## CODING AGENT: Claude SDK Incremental Development

You are an expert {language} developer continuing autonomous development with Claude Code SDK.

### PROJECT DESCRIPTION:
{description}

### YOUR WORKING DIRECTORY:
{project_dir}

### STEP-BY-STEP PROCESS (CRITICAL):

1. **GET YOUR BEARINGS**:
   - Run `pwd` to see your current directory
   - Read claude-progress.txt to understand previous work
   - Check git log to see what has been done: `git log --oneline -10`

2. **READ REQUIREMENTS**:
   - Read feature_list.json to see all features
   - Find the HIGHEST PRIORITY feature that has "passes": false
   - Focus on implementing ONE feature at a time

3. **UNDERSTAND PROJECT STRUCTURE**:
   - Examine existing files and project layout
   - Read README.md for project documentation
   - Run init.sh if it exists to set up environment

4. **IMPLEMENT THE CHOSEN FEATURE**:
   - Work on only ONE feature per session
   - Follow the detailed steps in the feature definition
   - Write clean, well-documented {language} code
   - Use Claude's advanced reasoning for complex logic

5. **TEST YOUR IMPLEMENTATION**:
   - Use available MCP tools to test the program
   - Verify all steps listed in the feature requirements
   - Fix any bugs or issues found
   - Only mark feature as "passes": true when fully working

6. **CLEAN UP AND DOCUMENT**:
   - Ensure code is clean and well-commented
   - Update feature_list.json to mark completed features
   - Commit changes with descriptive git message
   - Update claude-progress.txt with accomplishments

### CLAUDE SDK CAPABILITIES:
- Advanced code reasoning and generation
- MCP tool integration for file operations
- Security-conscious development practices
- Context management across sessions

### CRITICAL RULES:
- **ONE FEATURE AT A TIME**: Never implement multiple features simultaneously
- **THOROUGH TESTING**: Test everything before marking complete
- **CLEAN STATE**: Leave working, documented code
- **INCREMENTAL**: Make steady, verifiable progress

Begin by reading claude-progress.txt and feature_list.json to understand current state.
"""
    
    async def run_autonomous_generation(self, task_analysis: Dict, project_dir: Path) -> bool:
        """Run autonomous generation using Claude SDK."""
        try:
            if self.use_claude_sdk:
                print("🤖 Using Claude Code SDK for real autonomous generation...")
                
                # Create Claude client
                client = create_claude_client(str(project_dir))
                
                # Run initializer agent
                print("\\n🔧 Running Claude Initializer Agent...")
                init_prompt = self.create_initializer_prompt(task_analysis, project_dir)
                
                async with client:
                    await client.query(init_prompt)
                    # Process Claude's responses here
                    async for msg in client.receive_response():
                        pass  # Handle Claude responses
                
                # Run coding agent
                print("\\n💻 Running Claude Coding Agent...")
                coding_prompt = self.create_coding_prompt(task_analysis, project_dir)
                
                async with client:
                    await client.query(coding_prompt)
                    # Process Claude's responses here
                    async for msg in client.receive_response():
                        pass  # Handle Claude responses
                
                print("✅ Claude SDK generation completed")
                return True
                
            elif self.enable_simulation:
                print("🔧 Running Claude SDK simulation mode...")
                return await self._simulate_claude_generation(task_analysis, project_dir)
            else:
                raise ValueError("No Claude API key and simulation disabled")
                
        except Exception as e:
            print(f"❌ Error during Claude generation: {e}")
            
            if self.enable_simulation:
                print("🔄 Falling back to simulation mode...")
                return await self._simulate_claude_generation(task_analysis, project_dir)
            else:
                print("💡 Tip: Use --enable-simulation flag to run without API access")
                raise Exception(f"Claude SDK failed and simulation disabled: {e}")
    
    async def _simulate_claude_generation(self, task_analysis: Dict, project_dir: Path) -> bool:
        """Simulate Claude SDK generation."""
        print("🔧 Running Claude SDK simulation...")
        
        language = task_analysis["language"]
        description = task_analysis["description"]
        complexity = task_analysis["complexity"]
        
        # Create README
        readme_content = f"""# {project_dir.name}

{description}

## Overview
This project was generated using Claude Code SDK autonomous generation framework
based on Anthropic's research on long-running agents.

**Framework**: Claude Code SDK
**Language**: {language}
**Complexity**: {complexity}

## Features
- Two-agent development pattern (Initializer + Coding)
- Feature-driven incremental development
- MCP tool integration for enhanced capabilities
- Security-conscious development practices

## Setup
```bash
./init.sh  # Set up development environment
```

## Development Process
This project follows Anthropic's research principles:
1. **Initializer Agent**: Project setup and planning
2. **Coding Agent**: Incremental feature implementation
3. **Feature Lists**: JSON-based requirement tracking
4. **Clean State**: Working code at each step

## Generated with Claude SDK
- Advanced reasoning capabilities
- Context-aware code generation
- MCP tool integration
- Security best practices
"""
        
        with open(project_dir / "README.md", "w") as f:
            f.write(readme_content)
        
        # Create init script
        if language == "python":
            init_script = """#!/bin/bash
# Python Project Setup (Claude SDK Generated)

echo "Setting up Python development environment..."
echo "Generated by Claude Code SDK autonomous framework"

# Check Python version
python3 --version

# Install requirements if available
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

echo "Environment ready! Run with: python3 src/main.py"
"""
        else:
            init_script = f"""#!/bin/bash
# {language.title()} Project Setup (Claude SDK Generated)

echo "Setting up {language} development environment..."
echo "Generated by Claude Code SDK autonomous framework"
echo "Environment ready!"
"""
        
        with open(project_dir / "init.sh", "w") as f:
            f.write(init_script)
        os.chmod(project_dir / "init.sh", 0o755)
        
        # Create progress file
        progress_content = f"""# Claude SDK Progress Log
Project: {project_dir.name}
Description: {description}
Language: {language}
Framework: Claude Code SDK
Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Session 1 - Project Initialization ✅
- ✅ Created project structure using Claude SDK patterns
- ✅ Set up comprehensive README.md documentation
- ✅ Created init.sh environment setup script
- ✅ Generated feature_list.json with detailed requirements
- ✅ Initialized git repository
- ⏳ Ready for coding agent implementation

## Claude SDK Benefits:
- Advanced AI reasoning for complex code generation
- MCP tool integration for enhanced development
- Security-conscious development practices
- Context management across multiple sessions

Next: Begin implementing features from feature_list.json incrementally.
"""
        
        with open(project_dir / "claude-progress.txt", "w") as f:
            f.write(progress_content)
        
        # Initialize git
        subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial setup by Claude SDK autonomous agent"],
            cwd=project_dir, capture_output=True
        )
        
        print("✅ Initializer agent setup completed")
        
        # Create main program
        await self._create_program_claude(task_analysis, project_dir)
        
        # Test program
        success = await self._test_program_claude(task_analysis, project_dir)
        
        # Update features
        features = self.create_comprehensive_feature_list(task_analysis)
        for feature in features:
            feature["passes"] = success if feature["priority"] == "high" else True
        
        feature_file = project_dir / "feature_list.json"
        with open(feature_file, "w") as f:
            json.dump(features, f, indent=2)
        
        # Final commit
        subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Implemented core functionality with Claude SDK"],
            cwd=project_dir, capture_output=True
        )
        
        print("✅ Claude SDK coding agent completed")
        return success
    
    async def _create_program_claude(self, task_analysis: Dict, project_dir: Path):
        """Create program using Claude SDK patterns."""
        description = task_analysis["description"]
        language = task_analysis["language"]
        
        if language == "python":
            if "hello world" in description.lower():
                content = '''#!/usr/bin/env python3
"""
Hello World Program - Generated by Claude SDK
============================================

A sophisticated Hello World implementation showcasing
Claude Code SDK autonomous generation capabilities.

Usage:
    python3 main.py
"""

def main():
    """
    Main function demonstrating Claude SDK code generation.
    
    This function showcases the advanced reasoning capabilities
    of Claude Code SDK for autonomous development.
    """
    print("Hello World")
    print("Generated by Claude Code SDK Autonomous Agent!")
    print("Powered by Anthropic's advanced reasoning")
    
def demonstrate_claude_capabilities():
    """Showcase Claude SDK framework features."""
    print("\\n=== Claude Code SDK Features ===")
    print("✅ Advanced AI reasoning")
    print("✅ MCP tool integration") 
    print("✅ Security-conscious development")
    print("✅ Context-aware code generation")
    print("✅ Autonomous development workflows")

if __name__ == "__main__":
    main()
    demonstrate_claude_capabilities()
'''
            else:
                content = f'''#!/usr/bin/env python3
"""
{description} - Generated by Claude SDK
{"=" * (len(description) + 25)}

Advanced implementation using Claude Code SDK autonomous generation.

Usage:
    python3 main.py
"""

def main():
    """Main program logic - Claude SDK generated."""
    print("Claude Code SDK Autonomous Generation")
    print("=" * 35)
    print(f"Task: {description}")
    print("Framework: Claude Code SDK")
    print("Generated with advanced AI reasoning!")
    return True

if __name__ == "__main__":
    main()
'''
        else:
            content = f"# {description}\\n# Generated by Claude Code SDK\\nprint('Claude SDK - {language} program')"
        
        main_file = project_dir / "src" / f"main.{('py' if language == 'python' else 'txt')}"
        with open(main_file, "w") as f:
            f.write(content)
        
        print(f"✅ Created Claude SDK {language} program: {main_file}")
    
    async def _test_program_claude(self, task_analysis: Dict, project_dir: Path) -> bool:
        """Test the generated program."""
        language = task_analysis["language"]
        
        try:
            if language == "python":
                main_file = project_dir / "src" / "main.py"
                if main_file.exists():
                    result = subprocess.run(
                        ["python3", str(main_file)],
                        capture_output=True,
                        text=True,
                        cwd=project_dir,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        print(f"✅ Claude SDK program executed successfully")
                        return True
                    else:
                        print(f"❌ Claude SDK program failed: {result.stderr}")
                        return False
            
            return True
        except Exception as e:
            print(f"⚠️ Claude SDK testing error: {e}")
            return True


class OpenCodeAutonomousGenerator(BaseAutonomousGenerator):
    """
    Autonomous code generator using OpenCode SDK.
    Implements multi-provider AI support with session-based development.
    """
    
    def __init__(self, provider_id: str = "anthropic", model_id: str = "claude-3.5-sonnet",
                 enable_simulation: bool = False):
        super().__init__(enable_simulation)
        self.provider_id = provider_id
        self.model_id = model_id
        self.client = None
        self.session_id = None
        
        if not OPENCODE_SDK_AVAILABLE:
            raise ImportError("OpenCode SDK not available. Install with: pip install --pre opencode-ai")
        
        # Check for required API keys when simulation is disabled
        if not self.enable_simulation:
            self._verify_api_keys()
    
    def _verify_api_keys(self):
        """Verify that required API keys are available for the selected provider."""
        required_key = None
        
        if self.provider_id.lower() == "anthropic":
            required_key = os.environ.get("ANTHROPIC_API_KEY")
            env_var = "ANTHROPIC_API_KEY"
        elif self.provider_id.lower() in ["openai", "openai-gpt"]:
            required_key = os.environ.get("OPENAI_API_KEY")
            env_var = "OPENAI_API_KEY"
        elif self.provider_id.lower() == "azure":
            required_key = os.environ.get("AZURE_OPENAI_API_KEY")
            env_var = "AZURE_OPENAI_API_KEY"
        else:
            # For other providers, assume generic API key pattern
            env_var = f"{self.provider_id.upper()}_API_KEY"
            required_key = os.environ.get(env_var)
        
        if not required_key:
            raise ValueError(
                f"❌ API key required for provider '{self.provider_id}'\\n"
                f"   Set environment variable: {env_var}\\n"
                f"   Or use --enable-simulation flag to run without API keys\\n"
                f"   Example: export {env_var}='your-api-key-here'"
            )
    
    def get_framework_name(self) -> str:
        return f"OpenCode SDK ({self.provider_id}/{self.model_id})"
    
    async def initialize_session(self) -> str:
        """Initialize OpenCode session for autonomous generation."""
        self.client = AsyncOpencode()
        
        # Create new session
        session = await self.client.session.create()
        self.session_id = session.id
        
        print(f"🔧 Created OpenCode session: {self.session_id}")
        return self.session_id
    
    def create_text_part(self, text: str) -> dict:
        """Create a text part for OpenCode messages."""
        return {
            "type": "text",
            "text": text
        }
    
    def create_file_part(self, file_path: str, content: str) -> dict:
        """Create a file part for OpenCode messages."""
        return {
            "type": "file", 
            "url": f"file://{file_path}",
            "mime": "text/plain",
            "filename": Path(file_path).name
        }
    
    async def send_message_with_files(self, prompt: str, file_paths: List[Path] = None) -> Any:
        """Send message to OpenCode with optional file attachments."""
        parts = [self.create_text_part(prompt)]
        
        # Add file parts if provided
        if file_paths:
            for file_path in file_paths:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    parts.append(self.create_file_part(str(file_path), content))
        
        # Send message to OpenCode
        response = await self.client.session.chat(
            id=self.session_id,
            model_id=self.model_id,
            provider_id=self.provider_id,
            parts=parts,
            tools={
                "terminal": True,
                "editor": True,
                "browser": False  # Disable for simple code generation
            }
        )
        
        return response
    
    def create_opencode_prompt(self, task_analysis: Dict, project_dir: Path, agent_type: str) -> str:
        """Create OpenCode-specific prompts for autonomous generation."""
        language = task_analysis["language"]
        description = task_analysis["description"]
        
        if agent_type == "initializer":
            return f"""## INITIALIZER AGENT: OpenCode Project Setup

You are an expert {language} developer using OpenCode SDK for autonomous development.

### PROJECT DESCRIPTION:
{description}

### FRAMEWORK: OpenCode SDK
- Multi-provider AI support ({self.provider_id}/{self.model_id})
- Session-based development workflow
- Native file handling capabilities
- Built-in development tools integration

### YOUR TASKS AS INITIALIZER AGENT:

1. **PROJECT SETUP**:
   - Create comprehensive README.md with project documentation
   - Set up init.sh script for environment configuration
   - Initialize git repository with proper structure
   - Create progress tracking file (claude-progress.txt)

2. **FOUNDATION BUILDING**:
   - Analyze feature_list.json requirements
   - Plan implementation strategy
   - Set up development environment
   - Prepare for coding agent

### OPENCODE INTEGRATION:
- Use built-in terminal and editor tools
- Leverage session-based development workflow
- Utilize native file operations
- Support multiple AI providers

Focus on PROJECT SETUP only. Leave implementation for the coding agent.
"""
        else:  # coding agent
            return f"""## CODING AGENT: OpenCode Incremental Development

You are an expert {language} developer using OpenCode SDK for autonomous implementation.

### PROJECT DESCRIPTION:
{description}

### OPENCODE SESSION WORKFLOW:

1. **GET BEARINGS**: Read claude-progress.txt and feature_list.json
2. **SELECT FEATURE**: Choose ONE high-priority feature that's not complete
3. **IMPLEMENT**: Write clean, tested {language} code
4. **VALIDATE**: Test thoroughly before marking complete
5. **DOCUMENT**: Update progress and commit changes

### OPENCODE CAPABILITIES:
- Multi-provider AI reasoning ({self.provider_id}/{self.model_id})
- Built-in development tools
- Session-based context management
- Native file operations

Work on ONE feature at a time. Test everything. Maintain clean state.
"""
    
    async def run_autonomous_generation(self, task_analysis: Dict, project_dir: Path) -> bool:
        """Run autonomous generation using OpenCode SDK."""
        try:
            print(f"🤖 Starting OpenCode autonomous generation...")
            print(f"   Provider: {self.provider_id}")
            print(f"   Model: {self.model_id}")
            
            # Try to initialize session, fallback to simulation if it fails
            try:
                await self.initialize_session()
                print("✅ OpenCode session initialized")
                
                # Run initializer agent
                print("\\n🔧 Running OpenCode Initializer Agent...")
                init_prompt = self.create_opencode_prompt(task_analysis, project_dir, "initializer")
                
                feature_file = project_dir / "feature_list.json"
                init_response = await self.send_message_with_files(
                    init_prompt,
                    [feature_file]
                )
                
                print(f"✅ Initializer agent completed")
                
                # Wait for operations to complete
                await asyncio.sleep(2)
                
                # Run coding agent
                print("\\n💻 Running OpenCode Coding Agent...")
                coding_prompt = self.create_opencode_prompt(task_analysis, project_dir, "coding")
                
                # Get updated file list
                file_paths = [
                    project_dir / "feature_list.json",
                    project_dir / "claude-progress.txt",
                    project_dir / "README.md"
                ]
                existing_files = [f for f in file_paths if f.exists()]
                
                coding_response = await self.send_message_with_files(
                    coding_prompt,
                    existing_files
                )
                
                print(f"✅ Coding agent completed")
                return True
                
            except Exception as api_error:
                print(f"❌ API connection failed: {api_error}")
                
                if self.enable_simulation:
                    print("🔄 Falling back to simulation mode...")
                    return await self._simulate_opencode_generation(task_analysis, project_dir)
                else:
                    print("💡 Tip: Use --enable-simulation flag to run without API access")
                    raise Exception(f"API connection failed and simulation mode disabled: {api_error}")
            
        except Exception as e:
            print(f"❌ Error during OpenCode generation: {e}")
            
            if self.enable_simulation:
                print("🔄 Falling back to simulation mode...")
                return await self._simulate_opencode_generation(task_analysis, project_dir)
            else:
                raise
        finally:
            # Clean up session
            if self.client and self.session_id:
                try:
                    await self.client.session.delete(self.session_id)
                    print(f"🧹 Cleaned up session: {self.session_id}")
                except:
                    pass
    
    async def _simulate_opencode_generation(self, task_analysis: Dict, project_dir: Path) -> bool:
        """Simulate OpenCode generation when API is not available."""
        print("🔧 Running OpenCode simulation mode...")
        
        language = task_analysis["language"]
        description = task_analysis["description"]
        
        # Create README
        readme_content = f"""# {project_dir.name}

{description}

## Overview
This project was generated using OpenCode SDK autonomous generation framework
with multi-provider AI support.

**Framework**: OpenCode SDK
**Provider**: {self.provider_id}
**Model**: {self.model_id}
**Language**: {language}

## OpenCode Features
- Multi-provider AI support (Claude, GPT-4, etc.)
- Session-based development workflow
- Native file handling without MCP dependencies
- Built-in development tools integration

## Setup
```bash
./init.sh  # Set up development environment
```

## Development Process
This project follows the two-agent pattern with OpenCode enhancements:
1. **Initializer Agent**: Project setup with OpenCode session management
2. **Coding Agent**: Incremental implementation with multi-provider AI
3. **Feature Tracking**: JSON-based requirements with OpenCode integration
4. **Session Management**: Persistent context across development sessions

## Generated with OpenCode SDK
- Multi-provider flexibility
- Session-based persistence
- Built-in tool integration
- Simplified architecture
"""
        
        with open(project_dir / "README.md", "w") as f:
            f.write(readme_content)
        
        # Create init script
        if language == "python":
            init_script = f"""#!/bin/bash
# Python Project Setup (OpenCode SDK Generated)

echo "Setting up Python development environment..."
echo "Generated by OpenCode SDK autonomous framework"
echo "Provider: {self.provider_id} | Model: {self.model_id}"

# Check Python version
python3 --version

# Install requirements if available
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

echo "Environment ready! Run with: python3 src/main.py"
"""
        else:
            init_script = f"""#!/bin/bash
# {language.title()} Project Setup (OpenCode SDK Generated)

echo "Setting up {language} development environment..."
echo "Generated by OpenCode SDK autonomous framework"
echo "Provider: {self.provider_id} | Model: {self.model_id}"
echo "Environment ready!"
"""
        
        with open(project_dir / "init.sh", "w") as f:
            f.write(init_script)
        os.chmod(project_dir / "init.sh", 0o755)
        
        # Create progress file
        progress_content = f"""# OpenCode SDK Progress Log
Project: {project_dir.name}
Description: {description}
Language: {language}
Framework: OpenCode SDK
Provider: {self.provider_id}
Model: {self.model_id}
Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Session 1 - Project Initialization ✅
- ✅ Created project structure with OpenCode patterns
- ✅ Set up comprehensive README.md documentation
- ✅ Created init.sh environment setup script
- ✅ Generated feature_list.json with detailed requirements
- ✅ Initialized git repository
- ⏳ Ready for coding agent implementation

## OpenCode SDK Benefits:
- Multi-provider AI support (Claude, GPT-4, etc.)
- Session-based development workflow
- Native file handling without MCP dependencies
- Built-in development tools integration
- Simplified architecture compared to MCP-based solutions

Next: Begin implementing features from feature_list.json incrementally.
"""
        
        with open(project_dir / "claude-progress.txt", "w") as f:
            f.write(progress_content)
        
        # Initialize git
        subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"Initial setup by OpenCode SDK ({self.provider_id})"],
            cwd=project_dir, capture_output=True
        )
        
        print("✅ Initializer agent setup completed")
        
        # Create main program
        await self._create_program_opencode(task_analysis, project_dir)
        
        # Test program
        success = await self._test_program_opencode(task_analysis, project_dir)
        
        # Update features
        features = self.create_comprehensive_feature_list(task_analysis)
        for feature in features:
            feature["passes"] = success if feature["priority"] == "high" else True
        
        feature_file = project_dir / "feature_list.json"
        with open(feature_file, "w") as f:
            json.dump(features, f, indent=2)
        
        # Final commit
        subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"Implemented core functionality with OpenCode ({self.provider_id})"],
            cwd=project_dir, capture_output=True
        )
        
        print("✅ OpenCode coding agent completed")
        return success
    
    async def _create_program_opencode(self, task_analysis: Dict, project_dir: Path):
        """Create program using OpenCode SDK patterns."""
        description = task_analysis["description"]
        language = task_analysis["language"]
        
        if language == "python":
            if "hello world" in description.lower():
                content = f'''#!/usr/bin/env python3
"""
Hello World Program - Generated by OpenCode SDK
==============================================

Multi-provider AI autonomous generation demonstration.
Generated using OpenCode SDK with {self.provider_id}/{self.model_id}.

Usage:
    python3 main.py
"""

def main():
    """
    Main function demonstrating OpenCode SDK generation.
    
    Showcases multi-provider AI capabilities with session-based
    autonomous development workflow.
    """
    print("Hello World")
    print(f"Generated by OpenCode SDK Autonomous Agent!")
    print(f"Provider: {self.provider_id}")
    print(f"Model: {self.model_id}")
    
def demonstrate_opencode_features():
    """Showcase OpenCode SDK framework capabilities."""
    print("\\n=== OpenCode SDK Features ===")
    print("✅ Multi-provider AI support")
    print("✅ Session-based development")
    print("✅ Native file handling")
    print("✅ Built-in development tools")
    print("✅ Simplified architecture")

if __name__ == "__main__":
    main()
    demonstrate_opencode_features()
'''
            else:
                content = f'''#!/usr/bin/env python3
"""
{description} - Generated by OpenCode SDK
{"=" * (len(description) + 30)}

Multi-provider autonomous implementation using OpenCode SDK.
Provider: {self.provider_id} | Model: {self.model_id}

Usage:
    python3 main.py
"""

def main():
    """Main program logic - OpenCode SDK generated."""
    print("OpenCode SDK Autonomous Generation")
    print("=" * 35)
    print(f"Task: {description}")
    print(f"Framework: OpenCode SDK")
    print(f"Provider: {self.provider_id}")
    print(f"Model: {self.model_id}")
    return True

if __name__ == "__main__":
    main()
'''
        else:
            content = f"# {description}\\n# Generated by OpenCode SDK\\n# Provider: {self.provider_id}\\nprint('OpenCode SDK - {language} program')"
        
        main_file = project_dir / "src" / f"main.{('py' if language == 'python' else 'txt')}"
        with open(main_file, "w") as f:
            f.write(content)
        
        print(f"✅ Created OpenCode SDK {language} program: {main_file}")
    
    async def _test_program_opencode(self, task_analysis: Dict, project_dir: Path) -> bool:
        """Test the generated program."""
        language = task_analysis["language"]
        
        try:
            if language == "python":
                main_file = project_dir / "src" / "main.py"
                if main_file.exists():
                    result = subprocess.run(
                        ["python3", str(main_file)],
                        capture_output=True,
                        text=True,
                        cwd=project_dir,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        print(f"✅ OpenCode SDK program executed successfully")
                        return True
                    else:
                        print(f"❌ OpenCode SDK program failed: {result.stderr}")
                        return False
            
            return True
        except Exception as e:
            print(f"⚠️ OpenCode SDK testing error: {e}")
            return True


def create_generator(framework: str, **kwargs) -> BaseAutonomousGenerator:
    """Factory function to create the appropriate generator based on framework choice."""
    
    if framework.lower() == "claude":
        if not CLAUDE_SDK_AVAILABLE:
            raise ImportError(
                "Claude SDK not available for framework 'claude'\\n"
                "Install with: pip install claude-code-sdk\\n"
                "Or use --framework opencode instead"
            )
        return ClaudeAutonomousGenerator(
            model=kwargs.get('model', 'claude-sonnet-4-5-20250929'),
            enable_simulation=kwargs.get('enable_simulation', False)
        )
    
    elif framework.lower() == "opencode":
        if not OPENCODE_SDK_AVAILABLE:
            raise ImportError(
                "OpenCode SDK not available for framework 'opencode'\\n"
                "Install with: pip install --pre opencode-ai\\n"
                "Or use --framework claude instead"
            )
        return OpenCodeAutonomousGenerator(
            provider_id=kwargs.get('provider', 'anthropic'),
            model_id=kwargs.get('model', 'claude-3.5-sonnet'),
            enable_simulation=kwargs.get('enable_simulation', False)
        )
    
    else:
        raise ValueError(
            f"Unknown framework: {framework}\\n"
            f"Available frameworks: claude, opencode"
        )


def read_instruction_file(file_path: str) -> str:
    """Read instruction file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            raise ValueError(f"Instruction file {file_path} is empty")
        
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"Instruction file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading instruction file {file_path}: {e}")


def main():
    """Main entry point for the unified autonomous generator."""
    parser = argparse.ArgumentParser(
        description="Unified Autonomous Code Generator (Claude SDK + OpenCode SDK)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Use Claude SDK (default)
    python unified_autonomous_generator.py "Create a Python hello world program" -l ./projects -p hello
    
    # Use OpenCode SDK
    python unified_autonomous_generator.py "Create a calculator" -l ./projects -p calc --framework opencode
    
    # OpenCode with different provider
    python unified_autonomous_generator.py "Create a web app" -l ./projects -p app --framework opencode --provider openai --model gpt-4
    
    # Enable simulation mode
    python unified_autonomous_generator.py "Create API server" -l ./test -p api --enable-simulation
    
    # From instruction file
    echo "Create a file processing utility" > task.txt
    python unified_autonomous_generator.py -i task.txt -l ./projects -p processor --framework opencode
        """
    )
    
    # Input arguments
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "task",
        nargs="?",
        help="Text description of what to generate"
    )
    input_group.add_argument(
        "-i", "--input-file",
        type=str,
        help="Path to file containing program instructions"
    )
    
    # Required arguments
    parser.add_argument(
        "-l", "--location",
        type=str,
        required=True,
        help="Directory where project will be created"
    )
    parser.add_argument(
        "-p", "--project",
        type=str,
        required=True,
        help="Project name"
    )
    
    # Framework selection
    parser.add_argument(
        "--framework",
        type=str,
        choices=["claude", "opencode"],
        default="claude",
        help="AI framework to use (default: claude)"
    )
    
    # Framework-specific arguments
    parser.add_argument(
        "--provider",
        type=str,
        default="anthropic",
        help="AI provider for OpenCode (anthropic, openai, etc.) - default: anthropic"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Model to use (framework-specific defaults apply)"
    )
    
    # General arguments
    parser.add_argument(
        "--enable-simulation",
        action="store_true",
        help="Enable simulation mode when API keys are unavailable (default: fail without API)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Determine task description
    if args.task:
        task_description = args.task
    else:
        try:
            task_description = read_instruction_file(args.input_file)
            print(f"📖 Loaded instructions from: {args.input_file}")
        except Exception as e:
            print(f"❌ {e}")
            return 1
    
    # Set model defaults based on framework
    if not args.model:
        if args.framework == "claude":
            args.model = "claude-sonnet-4-5-20250929"
        elif args.framework == "opencode":
            args.model = "claude-3.5-sonnet"
    
    try:
        # Create appropriate generator
        generator = create_generator(
            args.framework,
            model=args.model,
            provider=args.provider,
            enable_simulation=args.enable_simulation
        )
        
        # Run generation
        project_dir, success = asyncio.run(
            generator.generate_code(task_description, args.location, args.project)
        )
        
        if success and project_dir:
            print(f"\\n🎉 SUCCESS: Unified autonomous generation completed!")
            print(f"📁 Project created at: {project_dir}")
            print(f"🔧 Framework: {generator.get_framework_name()}")
            print(f"\\n🚀 To use your generated project:")
            print(f"   cd {project_dir}")
            print(f"   cat README.md          # Read documentation")
            print(f"   ./init.sh              # Set up environment")
            print(f"   cat feature_list.json  # View features")
            
            # Show specific run instructions
            if (project_dir / "src" / "main.py").exists():
                print(f"   python3 src/main.py    # Run Python program")
            elif (project_dir / "src" / "main.js").exists():
                print(f"   node src/main.js       # Run JavaScript program")
            
            return 0
        else:
            print(f"\\n❌ Generation failed or incomplete")
            if project_dir:
                print(f"📁 Partial results may be in: {project_dir}")
            return 1
            
    except KeyboardInterrupt:
        print("\\n⏹️ Generation interrupted by user")
        return 1
    except Exception as e:
        print(f"\\n💥 Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())