#!/usr/bin/env python3
"""Remove Lumina/LAM References - Replace with Agentify

This script replaces all references to Lumina, Agentify, and LAM with Agentify equivalents.
"""

import os
import re
from pathlib import Path
from typing import Dict

# Define replacements
REPLACEMENTS: Dict[str, str] = {
    # Lumina replacements
    "Agentify": "Agentify",
    "Agentify": "Agentify",
    "agentify.dev": "agentify.dev",
    "licensing@agentify.dev": "licensing@agentify.dev",
    "support@agentify.dev": "support@agentify.dev",
    "https://agentify.dev": "https://agentify.dev",
    "Moßler GmbH / Agentify": "Moßler GmbH / Agentify",
    
    # Agent Communication Protocol replacements
    "Agent Communication Protocol": "Agent Communication Protocol",
    "Agent Gateway": "Agent Gateway",
    "Agent Message": "Agent Message",
    "Agent Communication Protocol": "Agent Communication Protocol",
    "agent-gateway": "agent-gateway",
    "agent_protocol": "agent_protocol",
    "agent message": "agent message",
    
    # Config replacements
    "agentify_config": "agentify_config",
    "AgentifyConfig": "AgentifyConfig",
    "AGENTIFY_": "AGENTIFY_",
    
    # URL replacements
    "agentify.dev": "agentify.dev",
}

# File extensions to process
EXTENSIONS = {
    ".py", ".md", ".ts", ".tsx", ".js", ".jsx", 
    ".json", ".yaml", ".yml", ".toml", ".txt"
}

# Directories to exclude
EXCLUDE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", 
    "venv", "dist", "build", ".pytest_cache"
}


def should_process_file(file_path: Path) -> bool:
    """Check if file should be processed."""
    # Check extension
    if file_path.suffix not in EXTENSIONS:
        return False
    
    # Check if in excluded directory
    for part in file_path.parts:
        if part in EXCLUDE_DIRS:
            return False
    
    return True


def process_file(file_path: Path) -> int:
    """Process a single file and return number of replacements."""
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        replacements_count = 0
        
        # Apply all replacements
        for old, new in REPLACEMENTS.items():
            # Escape special regex characters
            pattern = re.escape(old)
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, new, content)
                replacements_count += len(matches)
        
        # Save if modified
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return replacements_count
        
        return 0
    
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return 0


def main():
    """Main function."""
    print("🔄 Removing Lumina/LAM references and replacing with Agentify...")
    print()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Find all files
    print("📂 Scanning files...")
    files = [
        f for f in project_root.rglob("*")
        if f.is_file() and should_process_file(f)
    ]
    
    print(f"📝 Found {len(files)} files to process")
    print()
    
    # Process files
    total_replacements = 0
    files_modified = 0
    
    for file_path in files:
        replacements = process_file(file_path)
        if replacements > 0:
            files_modified += 1
            total_replacements += replacements
            relative_path = file_path.relative_to(project_root)
            print(f"  ✅ {relative_path}: {replacements} replacements")
    
    # Summary
    print()
    print("✨ Complete!")
    print(f"  📝 Files modified: {files_modified}")
    print(f"  🔄 Total replacements: {total_replacements}")
    print()
    print("⚠️  Manual review recommended for:")
    print("  - agents/desktop_rpa/config/agentify_config.py (rename file)")
    print("  - Any hardcoded URLs or API endpoints")
    print("  - Documentation that references specific Lumina features")
    print()
    print("📋 Next steps:")
    print("  1. Review changes: git diff")
    print("  2. Test the application")
    print("  3. Commit changes: git add . && git commit -m 'Remove Lumina/LAM references, replace with Agentify'")
    print()


if __name__ == "__main__":
    main()

