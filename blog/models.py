from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager

# Create your models managers

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status="published")

# Create your models here.
class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )
    title = models.CharField(max_length=250)
    # Slug is used for strings that only contains - numbers, alphabets, underscore and hyphens
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blog_posts")
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    # Updated to the current time when we create a new record
    created = models.DateTimeField(auto_now_add=True)
    # Update the time to current time when we make changes in the object
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default="draft")

    # Managing the tags
    tags = TaggableManager()

    # Model managers
    # Default manager for the Post model
    objects = models.Manager()
    # Another manager for the Post model
    published = PublishedManager()

    # This methods gets the url for accessing the object detail
    # We might use the same post on several web pages
    # This creates a unique url for this post
    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])

    class Meta:
        # - means descending order
        ordering = ("-publish" ,)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("created", )

    def __str__(self):
        return f"Comment by : {self.name} on {self.post}"