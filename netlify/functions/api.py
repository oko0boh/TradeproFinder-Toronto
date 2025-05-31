from flask import Flask
import os
import sys
import json
from netlify_lambda_wsgi import make_handler

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the Flask app
from wsgi import app

# Create the handler
handler = make_handler(app)

# Lambda function
def lambda_handler(event, context):
    return handler(event, context)
