from django.urls import path
from .views import GoogleSignIn, search_query,  trending, main_page_links, load_cookies

urlpatterns = [
    path('search/', search_query.as_view(), name='Search'),
    path('trending/', trending.as_view(), name='Trending'),
    path('signin/', GoogleSignIn.as_view(), name = 'GoogleSignIn'),
    path('mainpage/', main_page_links.as_view(), name = 'MainPageLinks'),
    path('loadcookies/', load_cookies.as_view(), name = 'loadcookies')
]