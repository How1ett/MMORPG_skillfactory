from django.urls import path
from .views import *

urlpatterns = [
    path('index', Index.as_view(), name='index'),
    path('advertisement/<int:pk>', AdvertisementItem.as_view(), name='adv_view'),
    path('create_ad', CreateAdvertisement.as_view(), name='create_ad'),
    path('advertisement/<int:pk>/edit', EditAdvertisement.as_view()),
    path('advertisement/<int:pk>/delete', DeleteAdvertisement.as_view()),
    path('comments', Comments.as_view(), name='comments'),
    path('comments/<int:pk>', Comments.as_view(), name='comments_view'),
    path('comment/<int:pk>', CreateComment.as_view(), name='comment'),
    path('comment/accept/<int:pk>', comment_accept),
    path('comment/delete/<int:pk>', comment_delete),
    path('', lambda request: redirect('index', permanent=False)),
    path('accounts/profile', AccountProfile.as_view(), name='account_profile'),
    path('edit', UpdateProfile.as_view(), name='account_edit'),
]