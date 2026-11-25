# Django Daisy v2.0 🌼

![Test Status](https://github.com/hypy13/django-daisy/actions/workflows/tox_test.yml/badge.svg)
[![Published on Django Packages](https://img.shields.io/badge/Published%20on-Django%20Packages-0c3c26)](https://djangopackages.org/packages/p/django-daisy/)
![PyPI Downloads](https://badgen.net/pypi/dm/django-daisy)

**🎉 NEW: Version 2.0 is here!** Built with DaisyUI v5 and Tailwind CSS v4 for blazing-fast performance, enhanced responsiveness, and stunning new designs.

---

## 🚀 Live Demo

[**Try it now: https://hypy13-django-daisy.hf.space/en/admin/**](https://hypy13-django-daisy.hf.space/en/admin/)  
**Username:** demo | **Password:** demo

**RTL Demo:** https://hypy13-django-daisy.hf.space/fa/admin/

![ScreenShot](https://raw.githubusercontent.com/hypy13/django-daisy/refs/heads/main/screenshots/change_form.png)

---

## 📖 Documentation

**Full documentation:** https://hypy13.github.io/django-daisy-docs/

---

## ✨ What's New in v2.0

Version 2.0 brings major improvements in performance, design, and user experience:

- ⚡ **DaisyUI v5 & Tailwind CSS v4** - Lighter, faster, and more efficient
- 🎨 **New Themes & Icons** - Expanded theme collection with modern iconography
- 📱 **Enhanced Responsiveness** - Improved mobile experience with compact table views
- 🎯 **Redesigned Change Form** - Submit buttons relocated to right sidebar on large screens
- 📜 **Recent History Component** - Quick access to recent object changes in the sidebar
- 🗑️ **Improved Delete Confirmation** - Cleaner, more intuitive deletion interface
- ✅ **Updated Form Controls** - Modern DaisyUI v5 checkbox and input styling
- 🔧 **Performance Optimizations** - Faster load times and smoother interactions

<details>
<summary><strong>📋 Complete Changelog</strong></summary>

1. Upgraded to DaisyUI v5 and Tailwind CSS v4
2. Relocated submit button row to right sidebar on large screens (change form)
3. Added recent object history component in right sidebar (change form)
4. Improved change list table responsiveness with compact mobile view
5. Enhanced delete confirmation page design
6. Updated checkbox inputs to DaisyUI v5 styling
7. Added new themes to theme selector with updated icons
8. Various responsive improvements and UI enhancements

</details>

---

## ✨ Core Features

- 🌍 **Fully Responsive** - Seamless experience across mobile, tablet, and desktop
- 🔄 **RTL Support** - Complete right-to-left language support
- 🎨 **Multi-Theme System** - Switch themes effortlessly to match your brand
- 📑 **Tabbed Inline Admin** - Organize related data with tabbed sections
- 🔍 **Advanced Filtering** - Multi-value filters for precise navigation
- 🚀 **Optimized Performance** - Lightning-fast load times with minimal overhead

---

## ⚙️ Compatibility

- **Django:** 3.2 - 6.1 fully supported
- **Python:** 3.8+

---

## 📦 Installation

### Quick Install (PyPI)

```bash
pip install django-daisy
```

### Development Install (GitHub)

```bash
pip install -e git+https://github.com/hypy13/django-daisy.git#egg=django-daisy
```

### Configuration

Add to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    'django_daisy',
    'django.contrib.admin',
    'django.contrib.humanize',  # Required
    # ... your other apps
]
```

That's it! Your admin now has a modern, beautiful interface.

---

## 🎨 Customization

<details>
<summary><strong>App Configuration (apps.py)</strong></summary>

Customize individual app appearance in the sidebar:

```python
class PollsConfig(AppConfig):
    name = 'polls'
    icon = 'fa fa-square-poll-vertical'  # FontAwesome icon
    divider_title = "Apps"  # Section divider title
    priority = 0  # Sidebar ordering (higher = top)
    hide = False  # Hide from sidebar
```

</details>

<details>
<summary><strong>Global Settings (settings.py)</strong></summary>

Configure site-wide appearance and behavior:

```python
DAISY_SETTINGS = {
    # Branding
    'SITE_TITLE': 'Django Admin',
    'SITE_HEADER': 'Administration',
    'INDEX_TITLE': 'Hi, welcome to your dashboard',
    'SITE_LOGO': '/static/admin/img/django-daisy-logo.svg',
    'SITE_LOGO_DARK': None,  # Uses the bundled dark logo or reuses your custom SITE_LOGO
    
    # Customization
    'EXTRA_STYLES': [],  # Additional CSS files
    'EXTRA_SCRIPTS': [],  # Additional JS files
    'LOAD_FULL_STYLES': False,  # Load complete DaisyUI library
    'SHOW_CHANGELIST_FILTER': False,  # Auto-open filter sidebar
    'DONT_SUPPORT_ME': False,  # Hide GitHub link
    'SIDEBAR_FOOTNOTE': '',  # Custom sidebar footer text
    
    # Theme Configuration
    'DEFAULT_THEME': None,  # e.g., 'corporate', 'dark'
    'DEFAULT_THEME_DARK': None,  # Dark mode default
    'SHOW_THEME_SELECTOR': True,  # Show/hide theme dropdown
    'THEME_LIST': [
        {'name': 'Light', 'value': 'light'},
        {'name': 'Dark', 'value': 'dark'},
        # Add custom themes...
    ],
    
    # Third-Party App Customization
    'APPS_REORDER': {
        'auth': {
            'icon': 'fa-solid fa-person-military-pointing',
            'name': 'Authentication',
            'hide': False,
            'divider_title': "Auth",
        },
    },
}
```

</details>

<details>
<summary><strong>Theme Configuration Examples</strong></summary>

**Single Default Theme:**
```python
DAISY_SETTINGS = {
    'DEFAULT_THEME': 'corporate',  # Always use this theme
}
```

**Separate Light/Dark Themes:**
```python
DAISY_SETTINGS = {
    'DEFAULT_THEME': 'light',      # Light mode default
    'DEFAULT_THEME_DARK': 'dim',   # Dark mode default
}
```

**Enforce Theme (No User Choice):**
```python
DAISY_SETTINGS = {
    'DEFAULT_THEME': 'corporate',
    'SHOW_THEME_SELECTOR': False,  # Hide selector
}
```

**Custom Theme List:**
```python
DAISY_SETTINGS = {
    'THEME_LIST': [
        {'name': 'Light', 'value': 'light'},
        {'name': 'Corporate', 'value': 'corporate'},
        {'name': 'Luxury', 'value': 'luxury'},
    ],
}
```

> **Note:** For custom DaisyUI themes, enable `LOAD_FULL_STYLES: True` to load all theme styles.

</details>

---

## 🔧 Advanced Features

<details>
<summary><strong>Tabbed Inline Admin</strong></summary>

Create tabbed inline interfaces for related objects:

```python
from django_daisy.mixins import NavTabMixin

class ChoiceInline(admin.TabularInline, NavTabMixin):
    model = Choice
    extra = 1

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
```

</details>

<details>
<summary><strong>Tabbed Fieldsets</strong></summary>

Convert fieldsets into navigation tabs:

```python
@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email'),
            'classes': ('navtab',),  # Creates a tab
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )
```

</details>

<details>
<summary><strong>Language Switching</strong></summary>

Enable language selection in the admin panel:

**1. Add URL pattern (`urls.py`):**
```python
urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    # ... other patterns
]
```

**2. Enable middleware (`settings.py`):**
```python
MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',
    # ... other middleware
]
```

**3. Define languages (`settings.py`):**
```python
LANGUAGES = [
    ('en', 'English'),
    ('fa', 'Farsi'),
    # Add more languages...
]
```

</details>

---

## Custom Fields

### Rich Text Editor

Use `django-tinymce-editor` to add rich text editing to Django Daisy. [PyPI](https://pypi.org/project/django-tinymce-editor/) · [GitHub](https://github.com/django-daisy/tinymce-editor)

---

## 📸 Screenshots

<details>
<summary><strong>View Gallery</strong></summary>

**Listing View:**
![Listing View](https://raw.githubusercontent.com/hypy13/django-daisy/refs/heads/main/screenshots/listing.png)

**Change Form:**
![Change Form](https://raw.githubusercontent.com/hypy13/django-daisy/refs/heads/main/screenshots/change_form.png)

**Mobile Responsive:**
![Mobile View](https://raw.githubusercontent.com/hypy13/django-daisy/refs/heads/main/screenshots/mobile.png)

**Dark Theme:**
![Dark Theme](https://raw.githubusercontent.com/hypy13/django-daisy/refs/heads/main/screenshots/dark_theme.png)

</details>

---

## 🤝 Contributing

Contributions are welcome! Submit issues, suggestions, or pull requests on [GitHub](https://github.com/hypy13/django-daisy).

---

## 🙏 Acknowledgments

Special thanks to [Cloud With Django](https://www.youtube.com/@CloudWithDjango) for featuring Django Daisy!  
**Watch the demo:** https://www.youtube.com/watch?v=WEKTXu1la9M

---

## 📄 License

MIT License - see LICENSE file for details

---

**Made with ❤️ by the Django Daisy team**

### Dashboard

The index shows an overview of admin log activity, quick access links, daily activity,
and recent changes. Counts and the chart cover the last seven calendar days in the
active time zone. Superusers see all admin log entries; other staff see their own.
Quick access defaults to the first six model add pages available to the user.
When the registered user admin grants view permission, the overview also shows total,
active, and staff user counts, and a daily registrations chart. These use the user
admin’s `get_queryset(request)` so it must enforce any row-level restrictions. Active
and staff counts require corresponding boolean fields. The chart is omitted if the
configured date field is absent; its date range follows `activity_days`. Disable either
user component or select a custom date field through the dashboard settings below.

Configure the dashboard with `DAISY_SETTINGS`:

```python
from django.utils.translation import gettext_lazy as _

DAISY_SETTINGS = {
    'DASHBOARD': {
        'show_stats': True,
        'show_actions': True,
        'show_activity': True,
        'show_history': True,
        'show_user_stats': True,  # Requires permission to view the registered user admin
        'show_user_chart': True,
        'user_date_field': 'date_joined',  # DateField or DateTimeField on AUTH_USER_MODEL
        'activity_days': 7,  # 1–31, inclusive of today
        'history_limit': 10,
        # Omit this key for permission-aware model add links; [] disables links.
        'quick_actions': [
            {'label': _('View reports'), 'url': '/admin/reports/',
             'icon': 'fa-solid fa-chart-line'},
        ],
    },
}
```

Configured links are trusted project configuration: only include links appropriate
for all dashboard users, or filter them per request in a custom admin site. URLs
must point to views that enforce their own permissions. Labels can use Django's
`gettext_lazy` for translation.

For project-specific metrics and permission-aware actions, subclass `DaisyAdminSite`
and override `get_dashboard_config(request)`, `get_dashboard_stats(request, defaults)`,
or `get_dashboard_actions(request, defaults)`. The last two return lists of dictionaries;
statistics accept `label`, `value`, and optional `description` and Font Awesome `icon`;
actions accept `label`, `url`, and optional `icon`. Configure the subclass with
`DEFAULT_ADMIN_SITE_CLASS = "your_project.admin.YourAdminSite"` in Django settings. The chart and
default statistics use the queryset returned by `get_log_entries(request)`.

### Global admin search

The search field in the admin navigation (or `Ctrl+K` / `⌘K`) finds accessible
registered model pages and add actions. Results appear after two characters. It
uses the active admin site's app list, so hidden apps and models unavailable to
the current user do not appear. Record search is **off by default**; explicitly
select models after reviewing their search fields and access rules:

```python
DAISY_SETTINGS = {
    'GLOBAL_SEARCH': {
        'enabled': True,  # Set to False to remove the feature.
        'models': ['auth.user', 'shop.order'],  # app_label.model_name
        'limit_per_model': 5,  # 1–20 results per model
    },
}
```

Only registered, visible models with `ModelAdmin.get_search_fields(request)`
configured are searched. Search calls each model admin's `get_queryset()` and
`get_search_results()`, and checks view/change permission for each result. The
queryset must itself enforce any tenant or row-level restrictions, including
restrictions on fields searched or on related data. Results link to the model's
admin change page, which enforces its own access rules. To bound work, search
examines at most ten times the result limit for each model; some permitted
matches may be omitted when many preceding objects are denied. Search terms
must contain at least two characters and are limited to 200 characters.

Override `DaisyAdminSite.get_global_search_config(request)` to choose enabled
models per request. The feature does not add models or require migrations. The
admin site's own `admin_view` protects the search endpoint; projects using a
custom site must subclass `DaisyAdminSite` to use it.
