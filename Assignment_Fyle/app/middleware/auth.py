from functools import wraps
from flask import request, jsonify
import json

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('X-Principal')
        if not auth:
            return jsonify({'error': 'Missing authentication'}), 401
            
        try:
            auth_data = json.loads(auth)
            request.auth = auth_data
            return f(*args, **kwargs)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid authentication format'}), 400
            
    return decorated
