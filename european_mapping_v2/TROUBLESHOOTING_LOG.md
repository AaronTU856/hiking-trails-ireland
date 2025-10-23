# Troubleshooting & Testing Notes

### Project: European Mapping Dashboard  
**Date:** October 23, 2025  
**Author:** Aaron Baggot  

---

## Overview
While setting up and testing the Django project, I ran into a few issues with environment setup, templates, and URL routing.  
This log briefly outlines what I did to fix them and get everything working.

---

## Key Steps & Fixes

### 1. Environment & Setup
- Created and activated a new virtual environment:
  
  python3 -m venv .venv
  source .venv/bin/activate


### 2. Database & Admin

- Ran migrations after activating the correct Python environment:

 python3 manage.py makemigrations
 python3 manage.py migrate


Recreated the superuser after a login issue and confirmed access at /admin/.

### 3. Templates & Routing

- Fixed missing templates by confirming they were stored in:

templates/dashboard/base.html
templates/analytics.html
templates/index.html


- Added template path to settings.py:

'DIRS': [BASE_DIR / "templates"],


Resolved TemplateDoesNotExist and NoReverseMatch errors by adding missing URL routes in urls.py:

path('dashboard/', views.dashboard_index, name='dashboard_index'),
path('dashboard/analytics/', views.analytics_view, name='dashboard_analytics'),

### 4. Testing Views

Verified the following pages load correctly:

/ → Map view

/dashboard/ → Dashboard

/dashboard/analytics/ → Analytics

/admin/ → Admin panel

- All pages rendered successfully after updating URLs and templates.

## Summary

- Most of the issues were due to template paths and missing routes.
- Once fixed, the Django server ran smoothly and all views loaded as expected.
