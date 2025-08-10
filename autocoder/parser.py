from autocoder.auth import delete_api_key

import os
from pathlib import Path
import pathspec

class CommandParser:
    def __init__(self):
        self.commands = {}

        # Auto-register all methods starting with 'cmd_'
        for attr_name in dir(self):
            if attr_name.startswith("cmd_"):
                cmd_name = attr_name[4:]  # strip 'cmd_'
                method = getattr(self, attr_name)
                self.commands[cmd_name] = method

    def parse(self, tokens):
        if not tokens:
            return

        cmd = tokens[0]
        args = tokens[1:]

        action = self.commands.get(cmd)
        if action:
            action(args)
        else:
            print(f"Unknown command: {cmd}")

    # Command handlers
    def cmd_print_tree(self, args):
         pass

    def cmd_logout(self, args):
        delete_api_key()

    def cmd_help(self, args):
        print(f"Available commands: {', '.join(self.commands.keys())}")

    def cmd_exit(self, args):
        print("Exiting...")
        exit(0)

    # Utils
    def load_gitignore_patterns(self):
        gitignore_path = Path(".gitignore")
        if gitignore_path.exists():
            with gitignore_path.open() as f:
                patterns = f.read().splitlines()
            return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
        return None
