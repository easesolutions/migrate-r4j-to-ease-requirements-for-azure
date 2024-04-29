import sys
from utilities import run_migration

if __name__ == '__main__':
    if len(sys.argv) == 3:
        project_name = sys.argv[1]
        dry_run: bool = sys.argv[2].lower() in ["true", "t", "1"] if sys.argv[2] is not None else False
        print(f"Project key: {project_name} Dry Run: {dry_run}")
        run_migration(project_name, dry_run)
    elif len(sys.argv) == 2:
        project_name = sys.argv[1]
        print(f"Project name: {project_name} Dry Run: {False}")
        run_migration(project_name, False)
    else:
        print("Project name is required. Usage: python migrate.py <project_name> <dry_run>")
