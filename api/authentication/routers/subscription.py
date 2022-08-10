from rest_framework.routers import Route, SimpleRouter


class SubscriptionRouter(SimpleRouter):
    basename = 'subscriptions'
    routes = [
        Route(
            url=r'^subscribe$',
            mapping={'post': 'create'},
            name='{basename}-subscribe',
            detail=True,
            initkwargs={'suffix': 'Subscribe'}),
        Route(
            url=r'^unsubscribe/(?P<pk>[1-9]\d*)$',
            mapping={'delete': 'destroy'},
            name='{basename}-unsubscribe',
            detail=False,
            initkwargs={'suffix': 'Unsubscribe'}),
        Route(
            url=r'^subscriptions/lookup$',
            mapping={'get': 'lookup'},
            name='{basename}-lookup',
            detail=True,
            initkwargs={
                'suffix': 'Lookup',
            }),
        Route(
            url=r'^subscriptions/(?P<pk>[1-9]\d*)$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
            },
            name='{basename}-instance',
            detail=True,
            initkwargs={
                'suffix': 'Instance',
            }),
        Route(
            url=r'^subscriptions(\.(?P<ext>json|txt|csv))?$',
            mapping={'get': 'list'},
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}),
    ]
