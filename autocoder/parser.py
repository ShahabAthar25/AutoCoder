from autocoder.auth import delete_api_key

class CommandParser:
    def __init__(self):
        self.commands = {
            "say": self.cmd_say,
            "logout": self.cmd_logout,
            "help": self.cmd_help,
            "exit": self.cmd_exit
        }

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
    def cmd_say(self, args):
        print(" ".join(args))

    def cmd_logout(self, args):
        delete_api_key()

    def cmd_help(self, args):
        print(f"Available commands: {', '.join(self.commands.keys())}")

    def cmd_exit(self, args):
        print("Exiting...")
        exit(0)
