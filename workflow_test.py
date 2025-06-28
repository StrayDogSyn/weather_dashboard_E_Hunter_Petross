#!/usr/bin/env python3
"""
GitHub Workflow Testing Script for Weather Dashboard

This script demonstrates how to trigger and test GitHub Actions workflows
for the Weather Dashboard project.

Usage:
    python workflow_test.py [workflow_name] [branch]
"""

import subprocess
import sys
import os
from typing import Optional


class WorkflowTester:
    """GitHub Actions workflow testing utility."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.workflows = {
            "ci-cd": "ci-cd.yml",
            "quick-test": "quick-test.yml", 
            "pr-validation": "pr-validation.yml"
        }
    
    def check_gh_cli(self) -> bool:
        """Check if GitHub CLI is installed."""
        try:
            result = subprocess.run(
                ["gh", "--version"], 
                capture_output=True, 
                text=True, 
                cwd=self.repo_path
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def list_workflows(self) -> None:
        """List available workflows."""
        print("📋 Available Workflows:")
        print("=" * 50)
        for name, file in self.workflows.items():
            print(f"  • {name:<15} -> .github/workflows/{file}")
        print()
    
    def run_workflow(self, workflow_name: str, branch: str = "main", inputs: Optional[dict] = None) -> bool:
        """
        Trigger a GitHub Actions workflow.
        
        Args:
            workflow_name: Name of the workflow to run
            branch: Branch to run the workflow on
            inputs: Optional workflow inputs
            
        Returns:
            True if workflow was triggered successfully
        """
        if workflow_name not in self.workflows:
            print(f"❌ Unknown workflow: {workflow_name}")
            self.list_workflows()
            return False
        
        workflow_file = self.workflows[workflow_name]
        
        # Build command
        cmd = ["gh", "workflow", "run", workflow_file, "--ref", branch]
        
        # Add inputs if provided
        if inputs:
            for key, value in inputs.items():
                cmd.extend(["-f", f"{key}={value}"])
        
        try:
            print(f"🚀 Triggering workflow: {workflow_name}")
            print(f"📁 File: {workflow_file}")
            print(f"🌿 Branch: {branch}")
            if inputs:
                print(f"⚙️ Inputs: {inputs}")
            print()
            
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Workflow triggered successfully!")
                print(result.stdout)
                return True
            else:
                print("❌ Failed to trigger workflow:")
                print(result.stderr)
                return False
                
        except FileNotFoundError:
            print("❌ GitHub CLI (gh) not found. Please install it first:")
            print("   https://cli.github.com/")
            return False
    
    def watch_workflow(self, workflow_name: Optional[str] = None) -> None:
        """Watch workflow runs."""
        cmd = ["gh", "run", "list"]
        if workflow_name and workflow_name in self.workflows:
            cmd.extend(["--workflow", self.workflows[workflow_name]])
        
        try:
            print("👀 Recent workflow runs:")
            result = subprocess.run(cmd, cwd=self.repo_path)
        except FileNotFoundError:
            print("❌ GitHub CLI (gh) not found.")
    
    def test_all_workflows(self, branch: str = "main") -> None:
        """Test all available workflows."""
        print("🧪 Testing all workflows...")
        print("=" * 50)
        
        results = {}
        
        # Test quick-test with different types
        for test_type in ["basic", "full"]:
            name = f"quick-test-{test_type}"
            print(f"\n📋 Testing: {name}")
            success = self.run_workflow("quick-test", branch, {"test_type": test_type})
            results[name] = success
        
        # Test CI/CD workflow
        print(f"\n📋 Testing: ci-cd")
        success = self.run_workflow("ci-cd", branch)
        results["ci-cd"] = success
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        for workflow, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {workflow:<20} {status}")


def main():
    """Main entry point."""
    tester = WorkflowTester()
    
    print("🌤️ Weather Dashboard - GitHub Workflow Tester")
    print("=" * 55)
    
    # Check if GitHub CLI is available
    if not tester.check_gh_cli():
        print("❌ GitHub CLI not found. Please install it first:")
        print("   https://cli.github.com/")
        print("\nAlternatively, you can run workflows manually:")
        print("   gh workflow run WORKFLOW_FILE.yml --ref BRANCH")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage examples:")
        print("  python workflow_test.py list")
        print("  python workflow_test.py quick-test")
        print("  python workflow_test.py ci-cd main")
        print("  python workflow_test.py test-all")
        print("  python workflow_test.py watch")
        print()
        tester.list_workflows()
        return
    
    command = sys.argv[1]
    branch = sys.argv[2] if len(sys.argv) > 2 else "main"
    
    if command == "list":
        tester.list_workflows()
    elif command == "watch":
        tester.watch_workflow()
    elif command == "test-all":
        tester.test_all_workflows(branch)
    elif command in tester.workflows:
        # Handle specific workflow inputs
        inputs = {}
        if command == "quick-test":
            test_type = input("Enter test type (basic/full/integration) [basic]: ").strip()
            if test_type:
                inputs["test_type"] = test_type
            else:
                inputs["test_type"] = "basic"
        
        success = tester.run_workflow(command, branch, inputs if inputs else None)
        if success:
            print("\n💡 To watch the workflow progress:")
            print(f"   gh run watch")
    else:
        print(f"❌ Unknown command: {command}")
        tester.list_workflows()


if __name__ == "__main__":
    main()
