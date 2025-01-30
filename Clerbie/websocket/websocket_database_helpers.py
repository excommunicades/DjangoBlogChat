from channels.db import database_sync_to_async

from django.utils import timezone
from django.db.models import Max

@database_sync_to_async
def get_user_by_id(user_id):

    from authify.models import Clerbie

    try:
        return Clerbie.objects.get(id=user_id)
    except Clerbie.DoesNotExist:
        return None

@database_sync_to_async
def is_user_blocked(blocked_user, user):

    from authify.models import BlackList

    try:
        return BlackList.objects.get(blocked_user=blocked_user, user__id=user)
    except Clerbie.DoesNotExist:
        return None

@database_sync_to_async
def add_user_to_chat(chat_name, user):

    from chat.models import ChatRoom

    chat, created = ChatRoom.objects.get_or_create(name=chat_name)

    if user is not None and user not in chat.users.values_list('id', flat=True):
        chat.users.add(user)

    if created:

        return {"chat": chat.id, "status": "created"}

    return {"chat": chat.id, "status": "existing"}

@database_sync_to_async
def save_message_to_chat(chat_name, user, message):

    from chat.models import ChatRoom, Message

    chat = ChatRoom.objects.get(name=chat_name)
    message = Message.objects.create(user=user, room=chat, content=message)

    return message

@database_sync_to_async
def set_message_status_read(message_id):

    from chat.models import Message
    from websocket.consumers import connected_users    


    message = Message.objects.filter(id=int(message_id)).first()

    if message:
        
        message.status = 'read'
        message.when_read = timezone.now()

        message.save()

        participants = message.room.users.all()

        return [connected_users.get(participant.id) for participant in participants if connected_users.get(participant.id)]

    return []

@database_sync_to_async
def get_user_chats(user_id):

    from chat.models import ChatRoom

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

    from chat.models import Message

    messages = Message.objects.filter(room_id=chat_id).select_related('user').order_by('-timestamp')
    return [{
        'message_id': message.id,
        'user_id': message.user.id,
        'username': message.user.username,
        'message': message.content,
        'status': message.status,
        'when_message_was_read': message.when_read if message.when_read else None,
        'is_pinned': message.is_pinned,
        'reply_from_user': {
            'username': str(message.reply_from.username),
            'nickname': str(message.reply_from.nickname),
            'id': int(message.reply_from.id)
        } if message.reply_from else False,
        # 'reply_from_user': int(message.reply_from.id) if message.reply_from else False,
        'is_it_reply': True if message.reply_from else False,
        'reply_to': message.reply_to.id if message.reply_to is not None else False,
        'timestamp': message.timestamp.isoformat()} for message in messages]

@database_sync_to_async
def delete_chat(chat_id, user):

    from chat.models import ChatRoom
    from websocket.consumers import connected_users    

    chat = ChatRoom.objects.filter(id=chat_id).first()

    if not chat:
        return []

    participants = list(chat.users.all())


    if user in chat.users.values_list('id', flat=True):

        chat.delete()

        return [
            connected_users.get(participant.id)
            for participant in participants
            if connected_users.get(participant.id)
            ]

    return []


@database_sync_to_async
def delete_message(message_id, user, chat_id):

    from chat.models import Message
    from websocket.consumers import connected_users

    messages = Message.objects.filter(room_id=chat_id)

    message = messages.filter(id=message_id).first()

    if message and message.user.id == user:

        if messages.count() > 1:

            message.delete()

        else:

            message.delete()

            room = message.room

            room.delete()

        participants = message.room.users.all()

        return [connected_users.get(participant.id) for participant in participants if connected_users.get(participant.id)]

    return []

@database_sync_to_async
def update_message(message_id, user, new_message_content):

    from chat.models import Message
    from websocket.consumers import connected_users

    message = Message.objects.filter(id=message_id).first()
    if message and message.user.id == user:
        message.content = new_message_content
        message.save()
        participants = message.room.users.all()
        return [connected_users.get(participant.id) for participant in participants if connected_users.get(participant.id)]
    return []

@database_sync_to_async
def pin_message(message_id, user):

    from chat.models import Message
    from websocket.consumers import connected_users

    message = Message.objects.filter(id=message_id).first()

    if message and message.user.id == user:

        message.is_pinned = True
        message.save()
        participants = message.room.users.all()
        return [connected_users.get(participant.id) for participant in participants if connected_users.get(participant.id)]
    return []

@database_sync_to_async
def reply_message(message_replied_id, reply_content, chat_id, user):

    from chat.models import Message
    from websocket.consumers import connected_users

    message = Message.objects.create(user=user, room=int(chat_id), content=reply_content, reply_to=message_replied_id)

    participants = message.room.users.all()

    return [connected_users.get(participant.id) for participant in participants if connected_users.get(participant.id)]


@database_sync_to_async
def save_forward_message(message_content, from_user_id, user_from,  to_chat_id):

    from chat.models import Message
    from websocket.consumers import connected_users

    message = Message.objects.create(
                            content=message_content,
                            room_id=to_chat_id,
                            user_id=from_user_id,
                            reply_from=user_from,
                            reply_to_id=to_chat_id,
                            )

    participants = message.room.users.all()

    return [connected_users.get(participant.id) for participant in participants if connected_users.get(participant.id)]