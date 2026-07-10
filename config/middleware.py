from django.conf import settings
from django.http import HttpResponseRedirect


class NormalizeHostMiddleware:
    """Redirect localhost/127.0.0.1 traffic to a single host in development.

    Django treats localhost and 127.0.0.1 as different hosts for session cookies,
    so a login on one host can be lost when the same app is opened on the other.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.DEBUG:
            return self.get_response(request)

        host = request.get_host().split(":")[0]
        # Only redirect safe methods (GET/HEAD). Redirecting POST/PUT/etc loses body
        # and will break form submissions (e.g. registration). See issue where
        # POST from 127.0.0.1 was being redirected to localhost and losing data.
        if host in {"127.0.0.1", "0.0.0.0"} and request.method in {"GET", "HEAD"}:
            scheme = "https" if request.is_secure() else "http"
            port = request.get_port()
            canonical_host = "localhost"
            netloc = canonical_host if port in {80, 443, None} else f"{canonical_host}:{port}"
            redirect_url = f"{scheme}://{netloc}{request.get_full_path()}"
            return HttpResponseRedirect(redirect_url)

        return self.get_response(request)
