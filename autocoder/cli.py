import argparse

from autocoder.shell import AutoCoderShell


def main():
    parser = argparse.ArgumentParser(description="AutoCoder interactive shell.")
    parser.add_argument(
        "--login",
        action="store_true",
        help="Login and store credentials in the keyring",
    )
    args = parser.parse_args()

    shell = AutoCoderShell()

    if args.login:
        shell.login()

    shell.run()


if __name__ == "__main__":
    main()
