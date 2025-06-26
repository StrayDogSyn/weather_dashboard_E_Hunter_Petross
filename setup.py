#!/usr/bin/env python3
"""
Setup script for Weather Dashboard - Secure Environment Configuration

This script helps set up the development environment with proper security practices.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description, check=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=check, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return result
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return None
    except Exception as e:
        print(f"❌ {description} failed with unexpected error: {e}")
        return None


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ required")
        return False


def setup_virtual_environment():
    """Set up Python virtual environment."""
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    result = run_command([sys.executable, "-m", "venv", ".venv"], "Creating virtual environment")
    return result is not None


def get_activation_command():
    """Get the activation command for the current platform."""
    if os.name == 'nt':  # Windows
        return ".venv\\Scripts\\activate"
    else:  # macOS/Linux
        return "source .venv/bin/activate"


def install_dependencies():
    """Install project dependencies."""
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        pip_command = "pip"
    else:
        # Use virtual environment pip
        if os.name == 'nt':  # Windows
            pip_command = ".venv\\Scripts\\pip"
        else:  # macOS/Linux
            pip_command = ".venv/bin/pip"
    
    result = run_command(f"{pip_command} install -r requirements.txt", "Installing dependencies")
    return result is not None


def setup_environment_file():
    """Set up the .env file."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Remember to add your OpenWeatherMap API key to .env")
        return True
    else:
        print("❌ .env.example not found")
        return False


def check_api_key():
    """Check if API key is configured."""
    env_file = Path(".env")
    if env_file.exists():
        content = env_file.read_text()
        if "your_api_key_here" in content:
            print("⚠️  Please update your API key in .env file")
            print("   Get your free API key from: https://openweathermap.org/api")
            return False
        else:
            print("✅ API key appears to be configured")
            return True
    return False


def setup_directories():
    """Create necessary directories."""
    directories = ["data", "logs", "cache", "exports"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")


def run_configuration_test():
    """Run configuration test."""
    print("\n🧪 Running configuration test...")
    result = run_command([sys.executable, "config.py"], "Testing configuration")
    return result is not None


def main():
    """Main setup routine."""
    print("🌤️  Weather Dashboard Setup - Secure Configuration")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python 3.8+ required")
        return False
    
    # Setup virtual environment
    if not setup_virtual_environment():
        print("\n❌ Setup failed: Could not create virtual environment")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed: Could not install dependencies")
        return False
    
    # Setup environment file
    if not setup_environment_file():
        print("\n❌ Setup failed: Could not create .env file")
        return False
    
    # Create directories
    setup_directories()
    
    # Test configuration
    if not run_configuration_test():
        print("\n⚠️  Configuration test failed, but setup can continue")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print(f"   1. Activate virtual environment: {get_activation_command()}")
    print(f"   2. Get API key from: https://openweathermap.org/api")
    print(f"   3. Edit .env file and set OPENWEATHER_API_KEY=your_actual_api_key")
    print(f"   4. Run the application: python main.py")
    
    print("\n📚 Documentation:")
    print("   - README.md: Project overview and features")
    print("   - SECURITY.md: Security guidelines and best practices")
    print("   - docs/user_guide.md: Detailed user guide")
    
    print("\n🔒 Security Reminders:")
    print("   - Never commit your .env file")
    print("   - Keep your API key secure")
    print("   - Rotate API keys regularly")
    print("   - Review SECURITY.md for best practices")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with unexpected error: {e}")
        sys.exit(1)
