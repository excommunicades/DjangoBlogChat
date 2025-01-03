from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from api.api_actions.views.posts_views import(
    PostListCreate,
    PostsCRUD,
    SetReactionToPOST
)

from api.api_actions.views.chat_views import (
    UserChatRoomsView
)

urlpatterns = [
    path('posts/', PostListCreate.as_view(), name="create_list_posts"),
    path('posts/<int:pk>', PostsCRUD.as_view(), name="retrieve_update_delete_post"),
    path('post-reaction', SetReactionToPOST.as_view(), name='set-reaction'),

    #CHAT
    path('chats', UserChatRoomsView.as_view, name='user-chat-list')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
