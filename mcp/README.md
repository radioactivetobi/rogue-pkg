# 🛡️ RoguePkg MCP Server

Model Context Protocol (MCP) integration for RoguePkg - Interactive security scanning via AI assistants.

## 📁 Folder Structure

```
mcp/
├── mcp_server.py              # Main MCP server implementation
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── config/                    # Configuration files
│   ├── mcp_config.json       # MCP server configuration template
│   └── pyproject.toml        # Python project configuration
│
├── docs/                      # Documentation
│   ├── README.md             # Main MCP documentation
│   ├── QUICKSTART.md         # 5-minute quick start guide
│   ├── SETUP.md              # Detailed setup instructions
│   ├── INTEGRATION_GUIDE.md  # Advanced integration patterns
│   ├── SUMMARY.md            # Implementation summary
│   ├── FILE_STRUCTURE.md     # Complete file structure
│   └── GET_STARTED.md        # Starting point guide
│
├── examples/                  # Examples and tests
│   ├── usage_examples.md     # Usage patterns and examples
│   └── test_mcp_tools.py     # Automated test suite
│
└── tools/                     # Utility tools
    └── verify_setup.py       # Setup verification script
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd mcp
pip install -r requirements.txt
```

### 2. Get GitHub Token (Optional)
Visit: https://github.com/settings/tokens/new
- Scopes: `repo`, `read:org`

### 3. Configure Your AI Assistant
See `docs/QUICKSTART.md` for detailed instructions.

Example configuration:
```json
{
  "mcpServers": {
    "roguepkg": {
      "command": "python",
      "args": ["/full/path/to/rogue-pkg/mcp/mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "your_token_here"
      }
    }
  }
}
```

### 4. Verify Setup
```bash
python tools/verify_setup.py
```

### 5. Test
```bash
python examples/test_mcp_tools.py
```

## 📚 Documentation

- **[Quick Start](docs/QUICKSTART.md)** - Get running in 5 minutes
- **[Setup Guide](docs/SETUP.md)** - Detailed setup for all AI assistants
- **[Main Documentation](docs/README.md)** - Complete feature documentation
- **[Integration Guide](docs/INTEGRATION_GUIDE.md)** - Advanced workflows
- **[Examples](examples/usage_examples.md)** - Usage patterns

## 🎯 What You Can Do

Once configured, ask your AI assistant:

- ✅ "Check if lodash@4.17.21 has any malware"
- ✅ "Scan the facebook/react repository for vulnerabilities"
- ✅ "Check all repositories in my-org for malicious packages"
- ✅ "Is express safe to use in production?"

## 🛠️ Available Tools

### 1. `scan_package`
Scan individual npm packages for vulnerabilities and malware.

### 2. `scan_github_repository`
Scan a GitHub repository's dependencies.

### 3. `scan_github_organization`
Bulk scan all repositories in a GitHub organization.

### 4. `scan_dependencies`
Scan a list of dependencies in batch.

## 🔧 Configuration Files

### `config/mcp_config.json`
Template MCP configuration for AI assistants.

### `config/pyproject.toml`
Python project metadata and dependencies.

### `requirements.txt`
Minimal Python dependencies:
- `requests>=2.31.0`

## 🧪 Testing & Verification

### Verify Setup
```bash
cd mcp
python tools/verify_setup.py
```

### Run Tests
```bash
cd mcp
python examples/test_mcp_tools.py
```

## 📖 Where to Start

1. **New Users**: Start with `docs/GET_STARTED.md`
2. **Quick Setup**: Follow `docs/QUICKSTART.md`
3. **Detailed Setup**: Read `docs/SETUP.md`
4. **Advanced Usage**: Check `docs/INTEGRATION_GUIDE.md`
5. **Examples**: See `examples/usage_examples.md`

## 🤝 Integration with Main RoguePkg

The MCP server uses the core `roguepkg.py` scanner from the parent directory:

```
rogue-pkg/
├── roguepkg.py          # Core scanner (used by MCP)
├── mcp/                 # MCP integration
│   └── mcp_server.py    # Imports from ../roguepkg.py
```

## 🆘 Troubleshooting

If you encounter issues:

1. Run `python tools/verify_setup.py` for diagnostics
2. Check `docs/SETUP.md` for troubleshooting guide
3. Verify paths in your MCP configuration
4. Ensure `roguepkg.py` is in parent directory

## 📞 Support

- **Documentation**: See `docs/` folder
- **Issues**: https://github.com/radioactivetobi/roguepkg/issues
- **Examples**: `examples/usage_examples.md`

## 📄 License

MIT License - Same as main RoguePkg project

---

**Ready to start? See [docs/GET_STARTED.md](docs/GET_STARTED.md)!**

