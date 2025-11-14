#!/usr/bin/env python3
"""
ULTRON Component Mapper
Visualizes system architecture and connections
"""
import json
from pathlib import Path
from collections import defaultdict

class ComponentMapper:
    def __init__(self):
        self.root = Path(".")
        self.report_file = self.root / 'SYSTEM_AUDIT_REPORT.json'
        
    def create_visual_map(self):
        """Create visual component map"""
        if not self.report_file.exists():
            print("❌ Run SYSTEM_AUDIT_AND_FIX.py first!")
            return
        
        with open(self.report_file) as f:
            report = json.load(f)
        
        print("=" * 70)
        print("  ULTRON COMPONENT MAP")
        print("=" * 70)
        print()
        
        # Group by category
        categories = defaultdict(list)
        for comp_path, comp_info in report['components'].items():
            categories[comp_info['category']].append(comp_path)
        
        # Print tree structure
        for category, components in sorted(categories.items()):
            print(f"📦 {category.upper()} ({len(components)} components)")
            for comp in sorted(components):
                connections = report['connections'].get(comp, [])
                status = "🔗" if connections else "⚠️ "
                print(f"   {status} {Path(comp).name}")
                if connections:
                    for conn in connections[:3]:
                        print(f"      └─> {Path(conn).name}")
                    if len(connections) > 3:
                        print(f"      └─> ... and {len(connections) - 3} more")
            print()
        
        # Create Mermaid diagram
        self.create_mermaid_diagram(report)
        
        # Create connection matrix
        self.create_connection_matrix(report)
    
    def create_mermaid_diagram(self, report):
        """Create Mermaid flowchart"""
        diagram_file = self.root / "SYSTEM_ARCHITECTURE.md"
        
        content = '''# ULTRON System Architecture

## Component Diagram

```mermaid
graph TD
    Core[Agent Core] --> Brain[Brain/AI]
    Core --> Voice[Voice Manager]
    Core --> Tools[Tool System]
    Core --> GUI[Web GUI]
    
    Brain --> Ollama[Ollama Backend]
    Brain --> Memory[Memory System]
    
    Voice --> ElevenLabs[ElevenLabs]
    Voice --> Pyttsx3[Pyttsx3]
    
    Tools --> ToolLoader[Tool Loader]
    ToolLoader --> Tool1[Tool 1]
    ToolLoader --> Tool2[Tool 2]
    ToolLoader --> ToolN[Tool N...]
    
    GUI --> Flask[Flask Server]
    GUI --> WebSocket[WebSocket]
    
    style Core fill:#f9f,stroke:#333,stroke-width:4px
    style Brain fill:#bbf,stroke:#333,stroke-width:2px
    style Voice fill:#bfb,stroke:#333,stroke-width:2px
    style Tools fill:#fbb,stroke:#333,stroke-width:2px
    style GUI fill:#ffb,stroke:#333,stroke-width:2px
```

## Connection Statistics

'''
        
        # Add statistics
        total_components = len(report['components'])
        total_connections = sum(len(v) for v in report['connections'].values())
        
        content += f"- **Total Components**: {total_components}\n"
        content += f"- **Total Connections**: {total_connections}\n"
        content += f"- **Average Connections per Component**: {total_connections / max(total_components, 1):.1f}\n\n"
        
        # Add component list
        content += "## Components by Category\n\n"
        categories = defaultdict(list)
        for comp_path, comp_info in report['components'].items():
            categories[comp_info['category']].append(comp_path)
        
        for category, components in sorted(categories.items()):
            content += f"### {category.title()}\n\n"
            for comp in sorted(components):
                connections = report['connections'].get(comp, [])
                status = "✅" if connections else "⚠️"
                content += f"- {status} `{comp}` ({len(connections)} connections)\n"
            content += "\n"
        
        diagram_file.write_text(content, encoding='utf-8')
        print(f"📄 Architecture diagram saved: {diagram_file}")
    
    def create_connection_matrix(self, report):
        """Create connection matrix"""
        matrix_file = self.root / "CONNECTION_MATRIX.txt"
        
        components = sorted(report['components'].keys())
        connections = report['connections']
        
        # Create matrix
        lines = []
        lines.append("ULTRON Component Connection Matrix")
        lines.append("=" * 70)
        lines.append()
        
        for comp in components:
            comp_name = Path(comp).stem
            conns = connections.get(comp, [])
            if conns:
                lines.append(f"{comp_name}:")
                for conn in sorted(conns):
                    conn_name = Path(conn).stem
                    lines.append(f"  └─> {conn_name}")
                lines.append("")
        
        matrix_file.write_text('\n'.join(lines), encoding='utf-8')
        print(f"📄 Connection matrix saved: {matrix_file}")

def main():
    mapper = ComponentMapper()
    mapper.create_visual_map()
    print()
    print("=" * 70)
    print("  FILES CREATED")
    print("=" * 70)
    print()
    print("1. SYSTEM_ARCHITECTURE.md - Visual component diagram")
    print("2. CONNECTION_MATRIX.txt - Detailed connection matrix")
    print()

if __name__ == '__main__':
    main()
