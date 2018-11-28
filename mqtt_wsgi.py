from werkzeug.wsgi import DispatcherMiddleware
from mqtt import mqtt as application

def simple(env, resp):
    """
    Stupid dummy app required for DispatcherMiddleware. It's never actually
    used because it only responds to requests for / that nginx sends somehwere
    else. Only the /api app is actually used.
    See https://stackoverflow.com/a/18967744/867162
    """
    resp(b'200 OK', [(b'Content-Type', b'text/plain')])
    return [b'Hello WSGI World']

#application = DispatcherMiddleware(simple, {'/mqtt': app.wsgi_app})

