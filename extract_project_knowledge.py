r"""
Project Knowledge Extractor & AI Training Dataset Builder
Scans projects across G:\My Drive\Antigravity\Projects, analyzes structures,
and produces fine-tuning JSONL pairs and system prompt context files.
"""

import os
import json
from pathlib import Path

PROJECTS_DIR = Path(r"G:\My Drive\Antigravity\Projects")
OUTPUT_DIR = Path(__file__).parent / "datasets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIES = {
    "game_dev": ["game studio", "game mods", "monopoly", "chess", "VR creation apps"],
    "income_and_views": ["using ai agents for profit", "youtube shorts edit for gaming", "portfolio", "deploy"],
    "automation_and_tech": ["automate my day", "scheduled task", "google drive organizer", "email organizer", "screen reader", "Choogle"],
    "security_and_systems": ["MY Security", "vulnerability management", "bot finder", "reverse engineer applications", "RHCSA Exam200", "comptia exam simulator"],
    "ai_and_learning": ["How to train your AI", "is this AI", "personal training", "1st grade learning"]
}

def scan_projects():
    dataset_records = []
    summary_catalog = {}

    print(f"Scanning projects in: {PROJECTS_DIR}")
    if not PROJECTS_DIR.exists():
        print(f"Directory {PROJECTS_DIR} not found.")
        return

    # 1. Load domain-specific specialized dataset if present
    specialized_file = OUTPUT_DIR / "rom_modding_and_game_dev.jsonl"
    if specialized_file.exists():
        with open(specialized_file, "r", encoding="utf-8") as sf:
            for line in sf:
                if line.strip():
                    dataset_records.append(json.loads(line))
        print(f"Loaded {len(dataset_records)} specialized ROM modding & game dev records.")

    # 2. Scan all project directories
    for item in PROJECTS_DIR.iterdir():
        if not item.is_dir() or item.name.startswith("."):
            continue

        proj_name = item.name
        files = []
        readme_content = ""
        file_types = {}

        for root, dirs, filenames in os.walk(item):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", "venv")]
            for f in filenames:
                ext = Path(f).suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
                rel_path = os.path.relpath(os.path.join(root, f), item)
                files.append(rel_path)
                if f.lower() in ("readme.md", "notes.txt", "description.txt", "ai_game_engineering_guide.md") and not readme_content:
                    try:
                        with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as rf:
                            readme_content = rf.read(2000)
                    except Exception:
                        pass

        # Determine category
        assigned_cat = "other"
        for cat, names in CATEGORIES.items():
            if any(n.lower() in proj_name.lower() for n in names):
                assigned_cat = cat
                break

        summary_catalog[proj_name] = {
            "category": assigned_cat,
            "total_files": len(files),
            "file_types": file_types,
            "sample_files": files[:10],
            "description": readme_content[:300] if readme_content else "Custom active development workspace"
        }

        # Formulate instruction-tuning pairs
        record = {
            "instruction": f"Explain the purpose, technical stack, and expansion roadmap for project '{proj_name}'.",
            "input": f"Category: {assigned_cat}. Total files: {len(files)}. Top file types: {list(file_types.keys())[:5]}.",
            "output": f"Project '{proj_name}' belongs to the {assigned_cat} domain. Its primary mission is to expand capabilities in {assigned_cat.replace('_', ' ')}. Key integration targets include cross-linking with automated workflows, generating revenue/viewership channels, and scaling via AI agent automation."
        }
        dataset_records.append(record)

        # Extra specialized records for game studio & game mods
        if proj_name.lower() == "game studio":
            dataset_records.append({
                "instruction": "What is the technical architecture of the PaperMario_Expedition33_Unity project in game studio?",
                "input": "Tools: Unity LTS, Visual Studio, C# scripting, Paper Mario turn-based timing mechanics, Expedition 33 reactive defense.",
                "output": "PaperMario_Expedition33_Unity is a hybrid RPG prototype blending Paper Mario's action commands (timing-based button presses for extra damage) with Clair Obscur: Expedition 33's real-time dodge/parry mechanics. Built in Unity using C# in Visual Studio, it utilizes ScriptableObjects for enemy stats, Animator states for synchronized timing windows, and an action-dispatching turn queue."
            })
        elif proj_name.lower() == "game mods":
            dataset_records.append({
                "instruction": "How are game mods, ROM launchers, and asset injections structured in the 'game mods' workspace?",
                "input": "Subsystems: Mario Kart Double Dash Sonic stages (mkdd_sonic_stages), Retro ROM launchers (NES, Pokemon, Genesis).",
                "output": "The 'game mods' workspace contains multi-platform modding pipelines: 1) GameCube asset swaps (mkdd_sonic_stages) converting Sonic Adventure 2 stages and AST audio into MKDD .arc and .rel modules. 2) Emulation launchers for NES, Genesis, and Pokemon GBA/NDS/GameCube titles. 3) Binary patching and ROM combination pipelines for cross-system hacks."
            })

    # Save JSONL dataset
    jsonl_path = OUTPUT_DIR / "project_dataset.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for rec in dataset_records:
            f.write(json.dumps(rec) + "\n")
    print(f"Generated {len(dataset_records)} training records at {jsonl_path}")

    # Save Catalog JSON
    catalog_path = OUTPUT_DIR / "project_catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(summary_catalog, f, indent=2)
    print(f"Saved project catalog at {catalog_path}")

if __name__ == "__main__":
    scan_projects()
