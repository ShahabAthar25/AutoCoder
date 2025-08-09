from getpass import getpass

import keyring

SERVICE_NAME = "AutoCoderCLI"
USERNAME = "default"


def store_api_key():
    """Prompts user for API key and stores it securely."""
    api_key = getpass("Enter Gemini API Key: ")
    keyring.set_password(SERVICE_NAME, USERNAME, api_key)
    print("API key stored securely in your system keychain.")


def get_api_key():
    """Retrieves the stored API key, or prompts user to login."""
    api_key = keyring.get_password(SERVICE_NAME, USERNAME)
    if api_key is None:
        print("No API key found. Please run with --login first.")
        print("Please Login.")
    return api_key



def delete_api_key():
    """Deletes the stored API key from keychain."""
    keyring.delete_password(SERVICE_NAME, USERNAME)
    print("API key deleted from keychain.")
