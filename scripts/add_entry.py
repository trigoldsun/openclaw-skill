#!/usr/bin/env python3
"""
Personal Knowledge Base Entry Creator
=====================================
Add new knowledge entries to the KB with automatic indexing and relationship tracking.

Usage:
    python add_entry.py --title "My Note" --type note [options]
    python add_entry.py --interactive              # Interactive mode
    python add_entry.py --list-types               # Show entry types
"""

import os
import sys
import json
import uuid
import argparse
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Any


class KnowledgeEntryManager:
    """Manages knowledge entry creation and indexing."""
    
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    INDEX_DIR = BASE_DIR / "index"
    
    def __init__(self):
        self.entries_dir = self.DATA_DIR / "notes"  # Default to notes
        
        # Ensure directories exist
        for subdir in ["notes", "meetings", "decisions", "projects"]:
            (self.DATA_DIR / subdir).mkdir(parents=True, exist_ok=True)
        
        self.INDEX_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load existing indices
        self.load_indices()
    
    def load_indices(self):
        """Load all index files into memory."""
        self.indices = {
            "topic": {},
            "project": {},
            "person": {},
            "date": {},
            "status": {},
            "relationships": {}
        }
        
        try:
            for idx_file in self.INDEX_DIR.glob("*.json"):
                if idx_file.name != "relationships.json":
                    dimension = idx_file.stem
                    with open(idx_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.indices[dimension] = data.get('entries', {})
                
            # Load relationships separately
            rel_file = self.INDEX_DIR / "relationships.json"
            if rel_file.exists():
                with open(rel_file, 'r', encoding='utf-8') as f:
                    self.indices["relationships"] = json.load(f).get('graph', {})
                    
        except FileNotFoundError:
            pass
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse index file: {e}")
    
    def save_index(self, dimension: str):
        """Save a specific index to disk."""
        index_data = {"entries": self.indices[dimension]}
        index_file = self.INDEX_DIR / f"{dimension}.json"
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    def save_relationships(self):
        """Save relationship graph to disk."""
        rel_data = {"graph": self.indices["relationships"]}
        rel_file = self.INDEX_DIR / "relationships.json"
        
        with open(rel_file, 'w', encoding='utf-8') as f:
            json.dump(rel_data, f, indent=2, ensure_ascii=False)
    
    def create_entry(
        self,
        title: str,
        entry_type: str,
        topics: List[str] = None,
        projects: List[str] = None,
        persons: List[str] = None,
        summary: str = "",
        content: str = "",
        tags: List[str] = None,
        status: str = "draft",
        references: List[str] = None,
        depends_on: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new knowledge entry."""
        
        # Generate ID
        entry_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        # Determine storage path based on type
        type_subdir = {
            "note": "notes",
            "meeting": "meetings",
            "decision": "decisions",
            "project": "projects",
            "reference": "references"
        }.get(entry_type, "notes")
        
        entry_path = self.DATA_DIR / type_subdir / f"{entry_id}.json"
        
        # Build entry structure
        today = date.today()
        
        entry = {
            "id": entry_id,
            "title": title,
            "type": entry_type,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            
            "dimensions": {
                "topic": topics or [],
                "project": projects or [],
                "person": persons or [],
                "time": {
                    "date": today.isoformat(),
                    "week": f"{today.year}-W{today.isocalendar()[1]:02d}",
                    "quarter": f"{today.year}-Q{(today.month - 1) // 3 + 1}",
                    "year": today.year
                },
                "status": status
            },
            
            "content": {
                "summary": summary,
                "body": content,
                "tags": tags or []
            },
            
            "relationships": {
                "references": references or [],
                "referenced_by": [],
                "depends_on": depends_on or [],
                "blocks": []
            },
            
            "metadata": {
                "source": "Manual entry via CLI",
                "last_reviewed_at": None,
                "review_count": 0,
                "version": 1
            }
        }
        
        # Save entry
        with open(entry_path, 'w', encoding='utf-8') as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Entry created: {entry_id}")
        print(f"   Title: {title}")
        print(f"   Type: {entry_type}")
        print(f"   Location: {entry_path}")
        
        # Update indices
        self.update_dimensions_index(entry_id, entry)
        self.update_relationships(entry_id, entry)
        
        return entry
    
    def update_dimensions_index(self, entry_id: str, entry: Dict):
        """Update all dimension indexes with new entry."""
        
        dims = entry["dimensions"]
        
        # Topic index
        for topic in dims.get("topic", []):
            if topic not in self.indices["topic"]:
                self.indices["topic"][topic] = []
            if entry_id not in self.indices["topic"][topic]:
                self.indices["topic"][topic].append(entry_id)
        
        # Project index
        for project in dims.get("project", []):
            if project not in self.indices["project"]:
                self.indices["project"][project] = []
            if entry_id not in self.indices["project"][project]:
                self.indices["project"][project].append(entry_id)
        
        # Person index
        for person in dims.get("person", []):
            if person not in self.indices["person"]:
                self.indices["person"][person] = []
            if entry_id not in self.indices["person"][person]:
                self.indices["person"][person].append(entry_id)
        
        # Date index
        date_str = dims.get("time", {}).get("date", "")
        if date_str:
            if date_str not in self.indices["date"]:
                self.indices["date"][date_str] = []
            if entry_id not in self.indices["date"][date_str]:
                self.indices["date"][date_str].append(entry_id)
        
        # Status index
        status = dims.get("status", "draft")
        if status not in self.indices["status"]:
            self.indices["status"][status] = []
        if entry_id not in self.indices["status"][status]:
            self.indices["status"][status].append(entry_id)
        
        # Save all modified indices
        for dim in ["topic", "project", "person", "date", "status"]:
            self.save_index(dim)
    
    def update_relationships(self, entry_id: str, entry: Dict):
        """Update relationship graph."""
        
        if "relationships" not in self.indices["relationships"]:
            self.indices["relationships"] = {}
        
        # Add outgoing references
        for ref_id in entry["relationships"].get("references", []):
            if "outgoing" not in self.indices["relationships"]:
                self.indices["relationships"]["outgoing"] = {}
            if entry_id not in self.indices["relationships"]["outgoing"]:
                self.indices["relationships"]["outgoing"][entry_id] = []
            if ref_id not in self.indices["relationships"]["outgoing"][entry_id]:
                self.indices["relationships"]["outgoing"][entry_id].append(ref_id)
        
        # Add incoming references (auto-populated)
        for ref_id in entry["relationships"].get("references", []):
            if "incoming" not in self.indices["relationships"]:
                self.indices["relationships"]["incoming"] = {}
            if ref_id not in self.indices["relationships"]["incoming"]:
                self.indices["relationships"]["incoming"][ref_id] = []
            if entry_id not in self.indices["relationships"]["incoming"][ref_id]:
                self.indices["relationships"]["incoming"][ref_id].append(entry_id)
        
        self.save_relationships()
    
    def list_entry_types(self):
        """Print available entry types."""
        print("Available entry types:")
        types = {
            "note": "Individual knowledge notes",
            "meeting": "Meeting records with participants",
            "decision": "Important decisions made",
            "project": "Project summaries and status",
            "reference": "External references and resources"
        }
        
        for t, desc in types.items():
            print(f"  {t:15} → {desc}")


def main():
    parser = argparse.ArgumentParser(description="Personal Knowledge Base Entry Creator")
    parser.add_argument("--title", "-t", required=False, help="Entry title")
    parser.add_argument("--type", "-ty", choices=["note", "meeting", "decision", "project", "reference"], 
                       default="note", help="Entry type")
    parser.add_argument("--topics", "-tp", nargs="+", help="Topic categories")
    parser.add_argument("--projects", "-pr", nargs="+", help="Projects this belongs to")
    parser.add_argument("--persons", "-p", nargs="+", help="People involved/mentioned")
    parser.add_argument("--summary", "-s", help="Brief summary")
    parser.add_argument("--content", "-c", help="Full content (supports markdown)")
    parser.add_argument("--tags", "-tg", nargs="+", help="Tags")
    parser.add_argument("--status", "-st", choices=["draft", "review", "approved", "published", "archived"],
                       default="draft", help="Status")
    parser.add_argument("--references", "-r", nargs="+", help="IDs of referenced entries")
    parser.add_argument("--depends-on", "-do", nargs="+", help="Entry IDs this depends on")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--list-types", "-lt", action="store_true", help="List entry types")
    parser.add_argument("--path", "--data-path", help="Override data directory path")
    
    args = parser.parse_args()
    
    manager = KnowledgeEntryManager()
    
    if args.list_types:
        manager.list_entry_types()
        return
    
    if args.interactive:
        # Interactive mode
        print("=== Interactive Knowledge Entry Creator ===\n")
        
        title = input("Title: ").strip()
        if not title:
            print("❌ Title is required!")
            sys.exit(1)
        
        print("\nEntry types:")
        types_map = {1: "note", 2: "meeting", 3: "decision", 4: "project", 5: "reference"}
        for i, name in enumerate(types_map.values(), 1):
            print(f"  {i}. {name}")
        
        type_choice = int(input("Type (1-5, default=1): ") or "1")
        entry_type = types_map.get(type_choice, "note")
        
        topics_input = input("Topics (comma-separated): ")
        topics = [t.strip() for t in topics_input.split(",") if t.strip()] if topics_input else None
        
        projects_input = input("Projects (comma-separated): ")
        projects = [p.strip() for p in projects_input.split(",") if p.strip()] if projects_input else None
        
        persons_input = input("Persons (comma-separated, use 'myself' for yourself): ")
        persons = [p.strip() for p in persons_input.split(",") if p.strip()] if persons_input else None
        
        summary = input("Summary (optional): ").strip()
        
        print("\nEnter content (end with Ctrl+D or . on separate line):")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == '.':
                    break
                lines.append(line)
            except EOFError:
                break
        
        content = "\n".join(lines) if lines else ""
        
        tags_input = input("Tags (comma-separated, optional): ")
        tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else None
        
        manager.create_entry(
            title=title,
            entry_type=entry_type,
            topics=topics,
            projects=projects,
            persons=persons,
            summary=summary,
            content=content,
            tags=tags
        )
        
        print("\n✅ Entry saved successfully!")
        return
    
    # Non-interactive mode
    if not args.title:
        print("❌ Error: --title is required (or use --interactive mode)")
        sys.exit(1)
    
    entry = manager.create_entry(
        title=args.title,
        entry_type=args.type,
        topics=args.topics,
        projects=args.projects,
        persons=args.persons,
        summary=args.summary or "",
        content=args.content or "",
        tags=args.tags,
        status=args.status,
        references=args.references,
        depends_on=args.depends_on
    )
    
    print(f"\n📝 Next steps:")
    print(f"  1. Edit the entry at: {manager.DATA_DIR / (args.type + 's')}/{entry['id']}.json")
    print(f"  2. Search all entries: python scripts/search_kb.py --all")
    print(f"  3. Generate report: python scripts/generate_report.py")


if __name__ == "__main__":
    main()
