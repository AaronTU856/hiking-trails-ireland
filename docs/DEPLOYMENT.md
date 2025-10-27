# Deployment Guide

This guide explains how to deploy the Django + GeoDjango (PostGIS) web mapping app in production using **Gunicorn** and **Nginx** on Ubuntu 20.04+.

---

## Prerequisites
- Ubuntu 20.04+ server (fresh installation recommended)
- Domain name pointing to your server (e.g., `your-domain.com`)
- SSH access to the server
- Python 3.10+ installed
- Git installed

---

## Installation Steps

### 1. Server Setup

sudo apt update
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib postgis
sudo systemctl enable nginx
sudo systemctl enable postgresql
