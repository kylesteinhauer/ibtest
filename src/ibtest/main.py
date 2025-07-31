"""
Main module for IBTest package.

This module contains the core functionality for the IBTest package.
"""


def hello_world() -> str:
    """
    Return a simple greeting message.

    Returns:
        str: A greeting message
    """
    return "Hello from IBTest!"


def main() -> None:
    """
    Main entry point for the application.
    """
    print(hello_world())


if __name__ == "__main__":
    main()
