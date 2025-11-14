"""Google Drive File Reviewer - Unlimited Resources Mode"""
import os
import sys
from pathlib import Path

# Google Drive path (Windows mapped drive)
GDRIVE_PATH = r"H:\My Drive\ultron"

def scan_directory(path):
    """Recursively scan directory and return all files"""
    files = []
    try:
        for root, dirs, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                try:
                    size = os.path.getsize(filepath)
                    files.append({
                        'path': filepath,
                        'name': filename,
                        'size': size,
                        'ext': Path(filename).suffix.lower()
                    })
                except Exception as e:
                    print(f"Error accessing {filepath}: {e}")
    except Exception as e:
        print(f"Error scanning {path}: {e}")
    return files

def categorize_files(files):
    """Categorize files by type"""
    categories = {
        'code': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs'],
        'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'],
        'docs': ['.md', '.txt', '.rst', '.pdf', '.docx', '.doc'],
        'web': ['.html', '.css', '.scss', '.jsx', '.tsx', '.vue'],
        'data': ['.csv', '.xlsx', '.xls', '.db', '.sqlite', '.sql'],
        'images': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico'],
        'batch': ['.bat', '.cmd', '.ps1', '.sh'],
        'other': []
    }
    
    categorized = {k: [] for k in categories.keys()}
    
    for file in files:
        ext = file['ext']
        found = False
        for category, extensions in categories.items():
            if ext in extensions:
                categorized[category].append(file)
                found = True
                break
        if not found:
            categorized['other'].append(file)
    
    return categorized

def generate_report(files, categorized):
    """Generate comprehensive report"""
    report = []
    report.append("=" * 80)
    report.append("GOOGLE DRIVE FILE ANALYSIS - UNLIMITED RESOURCES MODE")
    report.append("=" * 80)
    report.append(f"\nSource: {GDRIVE_PATH}")
    report.append(f"Total Files: {len(files)}")
    report.append(f"Total Size: {sum(f['size'] for f in files) / 1024 / 1024:.2f} MB")
    report.append("\n" + "=" * 80)
    report.append("FILE CATEGORIES")
    report.append("=" * 80)
    
    for category, items in categorized.items():
        if items:
            report.append(f"\n{category.upper()} ({len(items)} files):")
            for item in items[:20]:  # Show first 20
                report.append(f"  - {item['name']} ({item['size']/1024:.1f} KB)")
            if len(items) > 20:
                report.append(f"  ... and {len(items)-20} more files")
    
    return "\n".join(report)

if __name__ == "__main__":
    print("Scanning Google Drive folder...")
    
    if not os.path.exists(GDRIVE_PATH):
        print(f"ERROR: Path not found: {GDRIVE_PATH}")
        print("Please ensure Google Drive is mounted at H:\\My Drive\\ultron")
        sys.exit(1)
    
    files = scan_directory(GDRIVE_PATH)
    categorized = categorize_files(files)
    report = generate_report(files, categorized)
    
    # Save report
    with open("gdrive_analysis.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(report)
    print(f"\nReport saved to: gdrive_analysis.txt")
    print(f"\nReady for Amazon Q review!")
