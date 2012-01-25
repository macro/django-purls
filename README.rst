Django-Purls
------------

Django-Purls is the simplest way to enable parallelized download of static
content on your site.  Adding parallelize downloads to your pages may increase
response times by 30%.

See http://yuiblog.com/blog/2007/04/11/performance-research-part-4/ for a deeper
analysis.

Django-Purls maps static content URLs to one of the configured servers in the
PURL_SERVERS settings.  Django-Purls uses a consistent hashing algorithm
allowing you to add or remove servers without completely re-shuffling all
URL mappings and still utilize browser cache.

Using
`````
1. Wrap your static content (ex. images) in the purl template tag.
::

    {% load purl_tags %}

    {% for image in image_list %}
        <img src="{% purl image.thumbnail_url %}" />
    {% endfor %}

2. Install Djagno app and tell Django-Purls about your asset servers
::

    INSTALLED_APPS = (
        ...
        'purls',
    )

    PURL_SERVERS = {
        # rewrite all URLs using the purl template tag to one of the following
        # servers
        'default': ('assets0.example.com', 'assets1.example.com',
                'assets2.example.com'),
    }

3. Profit

Setup
`````
::

    $ easy_install django-purls


Supports Python 2.5 or later

