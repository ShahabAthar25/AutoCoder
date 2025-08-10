import shlex
from autocoder.parser import CommandParser
from autocoder.auth import get_api_key, store_api_key

class AutoCoderShell:
    def __init__(self):
        self.parser = CommandParser()
        self.prompt = "AutoCoder> "

    def login(self):
        store_api_key()

    def run(self):
        api_key = get_api_key()

        if api_key is None:
            return

        print("Welcome to AutoCoder shell. Type 'exit' to quit.")

        while True:
            try:
                raw_input_str = input(self.prompt)
                if raw_input_str.strip().lower() in ("exit", "quit"):
                    break
                tokens = shlex.split(raw_input_str)
                self.parser.parse(tokens)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting...")
                break

