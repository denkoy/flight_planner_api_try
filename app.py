from flask import Flask,request, jsonify
from routes import register_routes
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
ADMIN_TOKEN = "123123123"

def admin_required(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token != f"Bearer {ADMIN_TOKEN}":
            return jsonify({"error": "Unauthorized"}), 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def create_app():
    app = Flask(__name__)
    register_routes(app)
    return app

def main():
    app = create_app()
    app.run(debug=True)

if __name__ == '__main__':
    main()