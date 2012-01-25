import urlparse

from django.conf import settings
from django import template

from purls import serverring


register = template.Library()

def _make_server_mapper(from_domain, to_domains):
    ring = serverring.ServerRing(nodes=to_domains)
    def url_rewriter(url, domain):
        new_domain = ring.get_node(url)
        if domain:
            url = url.replace(domain, new_domain)
        else:
            if from_domain != 'default':
                raise Exception("Only default setting in settings.PURL_SERVERS "
                        "is allowed to rewrite relative URLs")
            url = '//' + new_domain + url
        return url
    return from_domain, url_rewriter

def _get_mappers():
    try:
        if isinstance(settings.PURL_SERVERS, dict):
            return dict(map(lambda x: _make_server_mapper(x[0], x[1]),
                        settings.PURL_SERVERS.iteritems()))
        else:
            raise template.TemplateSyntaxError, \
                'purl tag requires settings.PURL_SERVERS to be a dict'
    except AttributeError:
        raise template.TemplateSyntaxError, \
            'purl tag requires settings.PURL_SERVERS to be defined'

@register.tag(name='purl')
def do_purl(parser, token):
    """
        Allows parallel download of static content by telling user agents to
        download the specified static content from one of the asset servers
        in settings.PURL_SERVERS.
          Usage:
            {% for image in images %}
                <img src="{% purl image.filename %}" />
            {% endfor %}
    """
    try:
        _, url = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            '%r tag requires a URL path' %  token.contents
    return PURLNode(url)

PURL_REWRITERS = _get_mappers()

class PURLNode(template.Node):
    def __init__(self, url):
        self.url = url

    def render(self, context):
        url = template.Variable(self.url)
        try:
            url = url.resolve(context)
        except template.VariableDoesNotExist:
            url = None
        if not url:
            return None
        default_rewriter = PURL_REWRITERS.get('default')
        if url.startswith('http://') or url.startswith('https://'):
            # absolute url, find rewriter for domain
            parts = urlparse.urlsplit(url)
            domain = parts[1]
            rewriter = PURL_REWRITERS.get(domain, default_rewriter)
        else:
            # relative url, use default rewriter
            rewriter = default_rewriter
            domain = None
        if rewriter is not None:
            url = rewriter(url, domain)
        return url

