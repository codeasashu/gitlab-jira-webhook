from flask import request, abort
import functools

def filter_webhook(object_kind): 
    def filter_gl_webhook(f): 
        @functools.wraps(f)
        def inner(*args, **kwargs):
            request_data = request.get_json(silent=True)
            if 'object_kind' not in request_data or \
             (object_kind != request_data['object_kind']):
                return abort(400)
            return f(request_data, *args, **kwargs)
        return inner
    return filter_gl_webhook