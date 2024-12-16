from django.db.models import Max
from channels.db import database_sync_to_async

@database_sync_to_async
def get_user_by_id(user_id):

    from blog_user.models import BlogUser

    try:
        return BlogUser.objects.get(id=user_id)
    except BlogUser.DoesNotExist:
        return None

@database_sync_to_async
def add_user_to_chat(chat_name, user):

    from publish.models import ChatRoom

    chat, created = ChatRoom.objects.get_or_create(name=chat_name)

    if user is not None and user not in chat.users.values_list('id', flat=True):
        chat.users.add(user)
    return chat

@database_sync_to_async
def save_message_to_chat(chat_name, user, message):

    from publish.models import ChatRoom, Message

    chat = ChatRoom.objects.get(name=chat_name)
    Message.objects.create(user=user, room=chat, content=message)

@database_sync_to_async
def set_message_status_read(message_id):

    from publish.models import Message
    from websocket.consumers import connected_users    


    message = Message.objects.filter(id=int(message_id)).first()

    if message:
        
        message.status = 'read'

        message.save()

        participants = message.room.users.all()

        return [connected_users.get(participant.id) for participant in participants if connected_users.get(participant.id)]

    return []

@database_sync_to_async
def get_user_chats(user_id):

    from publish.models import ChatRoom

    chats = ChatRoom.objects.filter(users__id=user_id)
    chats = chats.annotate(last_message_time=Max('messages__timestamp'))
    chats = chats.order_by('-last_message_time')
    return [{
        'chat_users': ', '.join([user.username for user in chat.users.exclude(id=user_id)]),
        'chat_id': chat.id,
        'chat_participant_list': ', '.join([str(user.id) for user in chat.users.all()]),
        'last_message_time': chat.last_message_time.isoformat() if chat.last_message_time else None
    } for chat in chats]

@database_sync_to_async
def get_chat_messages(chat_id):

    from publish.models import Message

    messages = Message.objects.filter(room_id=chat_id).select_related('user').order_by('-timestamp')
    return [{
        'message_id': message.id,
        'user_id': message.user.id,
        'username': message.user.username,
        'message': message.content,
        'timestamp': message.timestamp.isoformat()} for message in messages]

@database_sync_to_async
def delete_chat(chat_id, user):

    from publish.models import ChatRoom
    from websocket.consumers import connected_users    

    chat = ChatRoom.objects.filter(id=chat_id).first()

    participants = chat.users.all()


    if user not in chat.users.values_list('id', flat=True):

        chat.delete()
        chat.save()

        return [connected_users.get(participant.id) for participant in participants if connected_users.get(participant.id)]

    return []


@database_sync_to_async
def delete_message(message_id, user):

    from publish.models import Message
    from websocket.consumers import connected_users

    message = Message.objects.filter(id=message_id).first()
    if message and message.user.id == user:
        message.delete()
        participants = message.room.users.all()
        return [connected_users.get(participant.id) for participant in participants if connected_users.get(participant.id)]
    return []

@database_sync_to_async
def update_message(message_id, user, new_message_content):

    from publish.models import Message
    from websocket.consumers import connected_users

    message = Message.objects.filter(id=message_id).first()
    if message and message.user.id == user:
        message.content = new_message_content
        message.save()
        participants = message.room.users.all()
        return [connected_users.get(participant.id) for participant in participants if connected_users.get(participant.id)]
    return []

@database_sync_to_async
def save_forward_message(message_content, from_user_id, to_chat_id):

    from publish.models import Message
    from websocket.consumers import connected_users

    message = Message.objects.create(
                            content=message_content,
                            room_id=to_chat_id,
                            user_id=from_user_id
                            )

    participants = message.room.users.all()

    return [connected_users.get(participant.id) for participant in participants if connected_users.get(participant.id)]