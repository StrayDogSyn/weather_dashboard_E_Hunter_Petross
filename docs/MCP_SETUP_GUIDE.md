# MCP Server Setup Guide

This guide covers the installation and configuration of Blender and Fetch MCP servers for the Weather Dashboard project.

## Prerequisites

- **Blender 3.0 or newer** (for Blender MCP)
- **Python 3.10 or newer**
- **UV package manager** (already installed)
- **Claude Desktop** or **Cursor IDE**

## Installed Components

✅ **UV Package Manager** - Installed and configured  
✅ **MCP Core Package** - Version 1.12.2  
✅ **Blender MCP Server** - Version 1.2  
✅ **Fetch MCP Server** - Version 2025.4.7  
✅ **MCP Configuration File** - Created at `.claude/mcp_config.json`

## Configuration

The MCP configuration has been created with the following servers:

### Blender MCP Server
- **Command**: `uvx blender-mcp`
- **Features**: 
  - AI-powered 3D modeling with Claude
  - Object manipulation and material control
  - Scene inspection and Python code execution
  - Poly Haven asset integration
  - Hyper3D model generation
- **API Keys**: Configured for Hyper3D and Rodin services

### Fetch MCP Server
- **Command**: `uvx mcp-server-fetch`
- **Features**:
  - Web content fetching and processing
  - HTML, JSON, text, and markdown extraction
  - Content splitting for large responses
  - Browser mode support

## Next Steps

### For Blender MCP

1. **Download Blender Addon**:
   ```bash
   # Download from: https://github.com/ahujasid/blender-mcp/blob/main/addon.py
   ```

2. **Install Blender Addon**:
   - Open Blender
   - Go to `Edit > Preferences > Add-ons`
   - Click "Install..." and select the `addon.py` file
   - Enable the addon by checking "Interface: Blender MCP"

3. **Connect to Claude**:
   - In Blender's 3D View sidebar (press N)
   - Find the "BlenderMCP" tab
   - Click "Connect to Claude"

### For Claude Desktop Integration

Add this configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"],
      "env": {
        "HYPER3D_API_KEY": "k9TcfFoEhNd9cCPP2guHAHHHkctZHIRhZDywZ1euGUXwihbYLpOjQhofby80NJez",
        "RODIN_FREE_TRIAL_KEY": "k9TcfFoEhNd9cCPP2guHAHHHkctZHIRhZDywZ1euGUXwihbYLpOjQhofby80NJez"
      }
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

### For Cursor IDE Integration

Create `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"],
      "env": {
        "HYPER3D_API_KEY": "k9TcfFoEhNd9cCPP2guHAHHHkctZHIRhZDywZ1euGUXwihbYLpOjQhofby80NJez",
        "RODIN_FREE_TRIAL_KEY": "k9TcfFoEhNd9cCPP2guHAHHHkctZHIRhZDywZ1euGUXwihbYLpOjQhofby80NJez"
      }
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

## Usage Examples

### Blender MCP Commands
- "Create a low poly dungeon scene with a dragon guarding treasure"
- "Make this car red and metallic"
- "Generate a 3D model of a garden gnome using Hyper3D"
- "Create a beach scene using Poly Haven assets"
- "Point the camera at the scene and make it isometric"

### Fetch MCP Commands
- Fetch website content as HTML, text, or markdown
- Extract main article content using Readability
- Download JSON data from APIs
- Process large content with chunking support

## Troubleshooting

### Blender Connection Issues
- Ensure Blender addon is installed and enabled
- Check that Blender addon server is running
- Restart both Claude and Blender if needed

### UV Path Issues
- Verify UV is in PATH: `C:\Users\Petro\.local\bin`
- Restart terminal or IDE after UV installation

### API Key Issues
- Hyper3D free trial allows limited models per day
- Get your own keys from hyper3d.ai and fal.ai if needed

## Status

- ✅ **Environment Setup**: Complete
- ✅ **Package Installation**: Complete
- ✅ **Configuration Files**: Created
- ⏳ **Blender Addon**: Requires manual installation
- ⏳ **IDE Integration**: Requires configuration

## Resources

- [Blender MCP GitHub](https://github.com/ahujasid/blender-mcp)
- [Blender MCP PyPI](https://pypi.org/project/blender-mcp/)
- [MCP Server Fetch](https://pypi.org/project/mcp-server-fetch/)
- [UV Package Manager](https://astral.sh/uv/)