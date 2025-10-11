# 🌐 Internationalization (i18n) Guide

This application uses Flask-Babel for internationalization support.

## 📁 Structure

```
translations/
├── de/
│   └── LC_MESSAGES/
│       ├── messages.po  # German translations (editable)
│       └── messages.mo  # Compiled translations (binary)
├── en/
│   └── LC_MESSAGES/
│       ├── messages.po  # English translations
│       └── messages.mo  # Compiled translations
babel.cfg               # Babel configuration
extract_translations.py # Translation management script
messages.pot           # Translation template
```

## 🚀 Quick Start

### 1. Extract translatable strings
```bash
python extract_translations.py extract
```

### 2. Initialize German translations
```bash
python extract_translations.py init de
```

### 3. Edit translations
Edit `translations/de/LC_MESSAGES/messages.po`:
```po
msgid "Idle Clans Profit Optimizer"
msgstr "Idle Clans Gewinn-Optimierer"

msgid "Categories"
msgstr "Kategorien"
```

### 4. Compile translations
```bash
python extract_translations.py compile
```

### 5. Restart application
```bash
docker-compose restart
```

## 🔄 Development Workflow

### Adding new translatable strings
1. Wrap strings in `_()` function:
   ```python
   # Python
   message = _("Hello World")

   # Templates
   {{ _("Hello World") }}
   ```

2. Extract and update:
   ```bash
   python extract_translations.py update
   ```

3. Translate in `.po` files
4. Compile: `python extract_translations.py compile`
5. Restart app

## 📝 Translation Guidelines

### Python Code
```python
# Simple strings
title = _("Profit Calculator")

# Variables in strings
message = _("Found %(count)d tasks", count=len(tasks))

# Lazy translations (for forms, etc.)
from flask_babel import lazy_gettext as _l
field_label = _l("Task Name")
```

### Jinja Templates
```html
<!-- Simple translation -->
<h1>{{ _("Title") }}</h1>

<!-- With variables -->
<p>{{ _("Hello %(name)s", name=user.name) }}</p>

<!-- Pluralization -->
<p>{{ ngettext("%(num)d task", "%(num)d tasks", count, num=count) }}</p>
```

## 🎯 Item Name Translations

For game items and categories, we have special functions:

```python
# In Python
item_name = translate_item_name("item_key_from_api")
category_name = translate_category_name("category_key")

# In templates
{{ translate_item_name(task.name) }}
```

### Adding item translations
Edit the translation functions in `main.py`:

```python
def translate_item_name(item_key):
    translations = {
        'en': {
            'spruce_log': 'Spruce Log',
            'iron_ore': 'Iron Ore',
        },
        'de': {
            'spruce_log': 'Fichtenholz',
            'iron_ore': 'Eisenerz',
        }
    }
    locale = get_locale()
    return translations.get(locale, {}).get(item_key, item_key)
```

## 🌍 Supported Languages

- **English (en)** - Default
- **German (de)** - Work in progress

## 🔧 Technical Details

### Language Detection
1. User preference (future feature)
2. Browser `Accept-Language` header
3. Fallback to English

### Browser Testing
Test different languages:
```bash
# English
curl -H "Accept-Language: en" http://localhost:8001/

# German
curl -H "Accept-Language: de" http://localhost:8001/
```

## 📚 Resources

- [Flask-Babel Documentation](https://python-babel.github.io/flask-babel/)
- [Babel Documentation](http://babel.pocoo.org/)
- [GNU gettext](https://www.gnu.org/software/gettext/)