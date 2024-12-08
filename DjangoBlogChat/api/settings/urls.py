from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from api.api_actions.views.posts_views import(
    PostListCreate,
    PostsCRUD,
    SetReactionToPOST
)

urlpatterns = [
    path('posts/', PostListCreate.as_view(), name="create_list_posts"),
    path('posts/<int:pk>', PostsCRUD.as_view(), name="retrieve_update_delete_post"),
    path('post-reaction', SetReactionToPOST.as_view(), name='set-reaction')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
