import os
import subprocess
import sys
from configparser import ConfigParser

def get_main_repo_root():
    try:
        return subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], 
                                      text=True).strip()
    except subprocess.CalledProcessError:
        sys.exit("Error: Not in a Git repository")

def find_submodules(main_root):
    main_dot_git = os.path.realpath(os.path.join(main_root, '.git'))
    submodules = []
    
    for root, dirs, _ in os.walk(main_root):
        if '.git' not in dirs:
            continue
            
        git_dir = os.path.realpath(os.path.join(root, '.git'))
        if git_dir == main_dot_git:
            dirs.remove('.git')  # Skip main repo's .git
            continue

        try:
            url = subprocess.check_output(
                ['git', '-C', root, 'config', '--get', 'remote.origin.url'],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
        except subprocess.CalledProcessError:
            continue  # Skip if no remote URL
        
        rel_path = os.path.relpath(root, main_root).replace('\\', '/')
        submodules.append((rel_path, url))
        dirs.remove('.git')  # Stop traversing into this .git directory
        
    return submodules

def update_gitmodules(main_root, submodules):
    gitmodules_path = os.path.join(main_root, '.gitmodules')
    config = ConfigParser()
    
    if os.path.exists(gitmodules_path):
        config.read(gitmodules_path)
    
    for path, url in submodules:
        section = f'submodule "{path}"'
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, 'path', path)
        config.set(section, 'url', url)
    
    with open(gitmodules_path, 'w') as f:
        config.write(f)

if __name__ == '__main__':
    main_root = get_main_repo_root()
    submodules = find_submodules(main_root)
    update_gitmodules(main_root, submodules)
    print(f"Updated .gitmodules with {len(submodules)} submodule(s)")