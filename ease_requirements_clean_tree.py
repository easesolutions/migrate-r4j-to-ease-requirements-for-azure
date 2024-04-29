import sys
from utilities import run_clean

if __name__ == '__main__':
    if len(sys.argv) == 2:
        project_key = sys.argv[1]
        # should be change
        run_clean(project_key)
    else:
        print("{project_key} is required. Usage: python ease_requirements_clean_tree.py {project_key}")
