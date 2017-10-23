DjAPI
=====

The library of simple helpers to build API with Django.
Not aimed at implementing REST.

Requirements: Python 2.7+ and Django 1.8+. Installation::

    $ pip install djapi


Setup
-----

Most of the library needs no configuration, but if you want to use token authentication:

.. code:: python

    INSTALLED_APPS += ['djapi.authtoken']
    DJAPI_AUTH = ['djapi.authtoken.use_token']

    # Or add default django auth for e.g. debugging purposes
    DJAPI_AUTH = ['djapi.authtoken.use_token', 'djapi.auth.use_contribauth']


Usage
-----

.. code:: python

    import djapi as api


    posts_qs = api.queryset(Post).filter(visible=True) \
        .values_but('visible', 'modified_on')          \
        .values_add(category='category__title')        \
        .map_types(Image, lambda img: img.url)


    @api.catch(Post.DoesNotExist, status=404)
    def post(request, pk):
        return api.json(posts_qs.get(pk=pk))


    def posts_list(request):
        return api.json(api.paginate(request, posts_qs, per_page=20))

    @api.auth_required
    @api.user_passes_test(lambda user: user.is_staff)
    @api.validate(PostForm)
    def posts_create(request, post):
        post.created_by = request.user
        post.save()
        return api.json(201, created=post.pk)

    posts = api.route(get=posts_list, post=posts_create)
