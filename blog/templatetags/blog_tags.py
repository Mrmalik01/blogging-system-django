from django import template
from ..models import Post
from django.db.models import Count
import markdown


# CUSTOM TEMPLATE TAGS
# ----------------------------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.0/ref/templates/builtins/.

register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()

@register.inclusion_tag("blog/post/latest_posts.html")
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by("-publish")[:count]
    return {"latest_posts" : latest_posts}

@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count("comments")).order_by("-total_comments")[:count]


# CUSTOM TEMPLATE FILTERS
# ----------------------------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.0/ref/templates/builtins/

from django.utils.safestring import mark_safe

@register.filter(name='markdown')
def markdown_filter(text):
    return mark_safe(markdown.markdown(text))
