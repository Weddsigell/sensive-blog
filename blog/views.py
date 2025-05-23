from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Count, Prefetch


def serialize_tag(tag):
    return {
        'title': tag.title, 
        'posts_with_tag': tag.tag_count,
        }


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def get_comments_count(posts):
    posts_ids = [post.id for post in posts]    
    ids_and_comments = dict(
        Post.objects \
        .filter(id__in=posts_ids) \
        .annotate(comments_count=Count('comments')) \
        .values_list('id', 'comments_count')
    )       
    for post in posts:
        post.comments_count = ids_and_comments[post.id]


def index(request):
    most_popular_posts = Post.objects \
        .prefetch_related(
            Prefetch('tags', queryset=Tag.objects.annotate(tag_count=Count('posts'))), 
            'author'
        ) \
        .popular()[:5]
    get_comments_count(most_popular_posts)

    most_fresh_posts = Post.objects \
        .prefetch_related(
            Prefetch('tags', queryset=Tag.objects.annotate(tag_count=Count('posts'))), 
            'author'
        ) \
        .order_by('-published_at')[:5]
    get_comments_count(most_fresh_posts)
        
    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [
            serialize_post(post) for post in most_fresh_posts
        ],
        'popular_tags': [
            serialize_tag(tag) for tag in most_popular_tags
        ],
    }
    
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects \
        .prefetch_related(
            'tags', 
            'author',
            'likes'
        ) \
        .popular() \
        .get(slug=slug)
    
    comments = Comment.objects \
        .prefetch_related('author') \
        .filter(post=post)
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [{'title': tag.title} for tag in post.tags.all()],
    }

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = Post.objects \
        .prefetch_related(
            Prefetch('tags', queryset=Tag.objects.annotate(tag_count=Count('posts'))), 
            'author'
        ) \
        .popular()[:5]
    get_comments_count(most_popular_posts)

    context = {
        'post': serialized_post,
        'popular_tags': [
            serialize_tag(tag) for tag in most_popular_tags
        ],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):    
    most_popular_tags = Tag.objects.popular()[:5]
    
    most_popular_posts = Post.objects \
        .prefetch_related(
            Prefetch('tags', queryset=Tag.objects.annotate(tag_count=Count('posts'))), 
            'author'
        ) \
        .popular()[:5]
    get_comments_count(most_popular_posts)

    tag = Tag.objects \
        .prefetch_related('posts') \
        .get(title=tag_title)
    related_posts = tag.posts \
        .prefetch_related(
            'author', 
            Prefetch('tags', queryset=Tag.objects.annotate(tag_count=Count('posts')))
        ) \
        .all()[:20]
    get_comments_count(related_posts)

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
