#!/usr/bin/env python3
"""
Script to extract and manage translations for the Idle Clans Profit Optimizer.

Usage:
  python extract_translations.py extract  # Extract translatable strings
  python extract_translations.py update   # Update existing translations
  python extract_translations.py compile  # Compile translations
"""

import os
import sys
from babel.messages import frontend as babel

def extract_messages():
    """Extract translatable strings from source code"""
    print("Extracting translatable strings...")
    os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .')

def init_language(lang):
    """Initialize a new language"""
    print(f"Initializing {lang} translations...")
    os.system(f'pybabel init -i messages.pot -d translations -l {lang}')

def update_translations():
    """Update existing translations"""
    print("Updating translations...")
    os.system('pybabel update -i messages.pot -d translations')

def compile_translations():
    """Compile translations"""
    print("Compiling translations...")
    os.system('pybabel compile -d translations')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'extract':
        extract_messages()
        print("Next steps:")
        print("  python extract_translations.py init de  # Initialize German")
        print("  python extract_translations.py compile  # Compile")
    elif command == 'init' and len(sys.argv) == 3:
        lang = sys.argv[2]
        init_language(lang)
    elif command == 'update':
        extract_messages()
        update_translations()
    elif command == 'compile':
        compile_translations()
    else:
        print(__doc__)