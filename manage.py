#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


# import requests
#
# API_URL = "https://flowise.aludecor.co.in/api/v1/prediction/32a08670-da7b-463d-b91e-0af54589999f"
#
#
# def query(payload):
#     response = requests.post(API_URL, json=payload, verify=False)
#     return response.json()
#
#
# output = query({
#     "question": "Hey, how are you?",
# })


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SMS.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
      main()
