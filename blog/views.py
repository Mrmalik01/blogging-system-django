from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.conf import settings
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector

# Class based views here
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = "3"
    template_name = "blog/post/list.html"

# Function based views here.
def post_list(request, tag_slug=None):
    posts_objects = Post.published.all()

    # Filtering with the tags
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts_objects = posts_objects.filter(tags__in=[tag])

    paginator = Paginator(posts_objects, 3)
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer
        posts = paginator.page(1)
    except EmptyPage:
        # if the page is out of range, then show the last page
        posts = paginator.page(paginator.num_pages)
    return render(request, "blog/post/list.html", {"page" : page, "posts" : posts, "tag": tag})


# Share post through email
def share_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, status="published")
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = "{} recommends you read {}".format(cd['name'], post.title)
            message = "Read {} at  {}\n\n{}'s comments : {}".format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, settings.EMAIL_HOST_USER, [cd['to']], fail_silently=False)
            sent = True
    else:
        form = EmailPostForm()
    return render(request, "blog/post/share.html", {
                            "post" : post,
                            "form" : form,
                            "sent" : sent})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == "POST":
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    # Suggesting similar posts
    post_tags_ids = list(post.tags.values_list("id", flat=True)) # getting objects in a list
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
                                  .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by("-same_tags", "-publish")[:4]
    return render(request, "blog/post/detail.html", {"post": post,
                                                     "comments" : comments,
                                                     "new_comment": new_comment,
                                                     "comment_form" : comment_form,
                                                     "similar_posts" : similar_posts})


def search_posts(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vectors = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            rank = SearchRank(search_vectors, search_query)
            results = Post.published.annotate(search=search_vectors, rank=rank)\
                .filter(search=search_query)\
                .order_by('-rank')
    return render(request, 'blog/post/search.html', {
                                                        "form" : form,
                                                        "query" : query,
                                                        "results" : results
                                                    })