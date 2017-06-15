import csv
import urllib.request

from flask import redirect, render_template, request, session, url_for
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_session") is None:
            return redirect(url_for("index", next=request.url))
        return f(*args, **kwargs)
    return decorated_function
    
def test_check():
    pass