# SITEMAPS
# ------------------------------------------------------------------------------------

"""
Sitemap is an XML file that tells search engines about the pages of a website, their relevancy and how frequently
they change. Django comes with a sitemap framework.
"""

from django.contrib.sitemaps import Sitemap
from .models import Post

class PostSiteMap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.updated

