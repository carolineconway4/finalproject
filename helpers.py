import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
