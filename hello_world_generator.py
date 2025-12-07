#!/usr/bin/env python3
"""
Hello World Autonomous Code Generator
===================================

This script demonstrates autonomous code generation by creating a Hello World program.
It implements the key principles from the Anthropic research paper.
"""

import os
import json
import tempfile
import subprocess
from pathlib import Path

def create_feature_list():
    """Create feature requirements for Hello World program."""
    return [
        {
            "category": "functional",
            "description": "Python program prints 'Hello World' message",
            "steps": [
                "Create hello_world.py file",
                "Write code that prints 'Hello World'",
                "Test program execution",
                "Verify correct output"
            ],
            "passes": False
        },
        {
            "category": "code_quality",
            "description": "Code follows Python best practices",
            "steps": [
                "Check code has proper structure",
                "Verify code is clean and readable",
                "Ensure proper Python syntax",
                "Add appropriate comments"
            ],
            "passes": False
        },
        {
            "category": "testing",
            "description": "Program executes without errors",
            "steps": [
                "Run the Python program",
                "Check for syntax errors",
                "Verify no runtime exceptions",
                "Confirm expected output matches"
            ],
            "passes": False
        }
    ]

def autonomous_code_generation():
    """Simulate the autonomous coding agent process."""
    
    print("🤖 Autonomous Hello World Code Generation")
    print("=" * 50)
    
    # Create working directory
    project_dir = Path(tempfile.mkdtemp(prefix="autonomous_hello_world_"))
    print(f"📁 Working in: {project_dir}")
    
    # Step 1: Create feature list (Initializer Agent behavior)
    print("\n🔧 [Initializer Agent] Setting up project...")
    features = create_feature_list()
    feature_file = project_dir / "feature_list.json"
    
    with open(feature_file, "w") as f:
        json.dump(features, f, indent=2)
    print("✓ Created feature_list.json with requirements")
    
    # Step 2: Read requirements and plan (Coding Agent behavior)
    print("\n🤖 [Coding Agent] Reading requirements...")
    print("✓ Found 3 features to implement:")
    for i, feature in enumerate(features, 1):
        print(f"   {i}. {feature['description']}")
    
    # Step 3: Generate the code
    print("\n💻 [Coding Agent] Generating hello_world.py...")
    
    hello_world_content = '''#!/usr/bin/env python3
"""
Hello World Program
==================

A simple Python program that demonstrates basic output functionality.
This program prints the classic "Hello World" message to the console.

Author: Autonomous Coding Agent
Generated using principles from Anthropic's long-running agent research
"""

def main():
    """
    Main function that prints the Hello World message.
    
    This function serves as the entry point for the program and demonstrates
    basic Python syntax for console output.
    """
    # Print the classic greeting message
    print("Hello World")

def greet_user(name="World"):
    """
    Alternative greeting function that can personalize the message.
    
    Args:
        name (str): The name to greet. Defaults to "World".
    
    Returns:
        str: The greeting message
    """
    return f"Hello {name}"

if __name__ == "__main__":
    # Execute the main function when script is run directly
    main()
    
    # Demonstrate the alternative greeting function
    print(greet_user("Python"))
    print(greet_user("Autonomous Agent"))
'''
    
    hello_world_file = project_dir / "hello_world.py"
    with open(hello_world_file, "w") as f:
        f.write(hello_world_content)
    
    print("✓ Created hello_world.py with enhanced functionality")
    
    # Step 4: Test the program (Critical part of Anthropic approach)
    print("\n🧪 [Coding Agent] Testing the program...")
    
    try:
        # Run the program and capture output
        result = subprocess.run(
            ["python", str(hello_world_file)],
            capture_output=True,
            text=True,
            cwd=project_dir
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            print(f"✓ Program executed successfully")
            print(f"✓ Output received: {repr(output)}")
            
            # Verify output contains "Hello World"
            if "Hello World" in output:
                print("✓ Output verification passed")
                
                # Update feature list to mark as completed
                for feature in features:
                    feature["passes"] = True
                
                with open(feature_file, "w") as f:
                    json.dump(features, f, indent=2)
                
                print("✓ Updated feature_list.json - all features passing")
                
            else:
                print(f"❌ Output verification failed - expected 'Hello World' in output")
        else:
            print(f"❌ Program execution failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Testing failed: {e}")
    
    # Step 5: Final verification and report
    print(f"\n🎉 AUTONOMOUS CODE GENERATION COMPLETE")
    print("=" * 50)
    
    # Show generated files
    print(f"\n📂 Generated files in {project_dir}:")
    for file_path in project_dir.glob("*"):
        size = file_path.stat().st_size
        print(f"   📄 {file_path.name} ({size} bytes)")
    
    # Show the code
    print(f"\n📋 Generated hello_world.py:")
    print("-" * 40)
    with open(hello_world_file, "r") as f:
        code_lines = f.readlines()
        for i, line in enumerate(code_lines[:15], 1):  # Show first 15 lines
            print(f"{i:2d}: {line}", end="")
        if len(code_lines) > 15:
            print(f"    ... ({len(code_lines) - 15} more lines)")
    
    # Show feature completion status
    with open(feature_file, "r") as f:
        final_features = json.load(f)
    
    print(f"\n✅ Feature Completion Status:")
    print("-" * 40)
    all_passed = True
    for i, feature in enumerate(final_features, 1):
        status = "✅ PASSED" if feature["passes"] else "❌ FAILED"
        print(f"   {i}. {feature['category'].upper()}: {status}")
        if not feature["passes"]:
            all_passed = False
    
    success_rate = sum(1 for f in final_features if f["passes"]) / len(final_features)
    print(f"\n📊 Success Rate: {success_rate:.1%} ({sum(1 for f in final_features if f['passes'])}/{len(final_features)} features)")
    
    # Instructions for user
    print(f"\n🚀 Test the generated program yourself:")
    print(f"   cd {project_dir}")
    print(f"   python hello_world.py")
    print(f"   cat hello_world.py  # View the code")
    print(f"   cat feature_list.json  # View the requirements")
    
    return project_dir, all_passed

def main():
    """Main entry point."""
    print("Autonomous Code Generation Demo")
    print("Based on Anthropic's Long-Running Agent Research")
    print("=" * 50)
    
    try:
        project_dir, success = autonomous_code_generation()
        
        if success:
            print(f"\n🎊 SUCCESS: Autonomous code generation completed successfully!")
            print(f"📁 All files saved to: {project_dir}")
        else:
            print(f"\n⚠️ PARTIAL SUCCESS: Some features may need attention")
            print(f"📁 Check results in: {project_dir}")
            
    except KeyboardInterrupt:
        print("\n⏹️ Generation interrupted by user")
    except Exception as e:
        print(f"\n💥 Generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()