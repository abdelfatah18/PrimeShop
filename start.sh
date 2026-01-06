#!/usr/bin/env bash
gunicorn project.wsgi:application
