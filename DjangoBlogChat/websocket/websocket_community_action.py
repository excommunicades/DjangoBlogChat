import hashlib
import json

from websocket.websocket_database_helpers import (
    get_user_by_id,
    add_user_to_chat,
    save_message_to_chat,
    set_message_status_read,
    get_user_chats,
    get_chat_messages,
    delete_message,
    update_message,
    save_forward_message,
    delete_chat,
)


class CommunityAction:

    @staticmethod
    async def chat_message(data, user_id, connected_users):

        participants = data.get('participants').split(',')
        print('participants:', participants)
        sender_id = int(data.get('sender'))
        sender_name = str(data.get('sender_name'))
        message = data.get('message')
        chat_id = data.get('chat_id')

        participants_ids = list(map(int, participants))
        participants_ids.sort()
        print(participants_ids)
        chat_name = f"chat_{'_'.join(map(str, participants_ids))}"
        chat_hash = hashlib.sha256(chat_name.encode('utf-8')).hexdigest()

        for participant_id in participants_ids:

            participant_channel = connected_users.get(participant_id)
            
            user = await get_user_by_id(int(participant_id))

            await add_user_to_chat(chat_name=chat_hash, user=user)

            if participant_channel:

                await participant_channel.send(text_data=json.dumps({
                    'type': 'chat_message',
                    'sender_id': sender_id,
                    'username': sender_name,
                    'message': message,
                    'chat_id': chat_id,
                }))

        user = await get_user_by_id(int(user_id))
        await save_message_to_chat(chat_hash, user, message)

    @staticmethod
    async def set_status_read(message_id):

        participants_id_list = await set_message_status_read(message_id)

        return participants_id_list


    @staticmethod
    async def get_chat_list(user_id):

        user_chats = await get_user_chats(user_id)

        return {
            'type': 'chat_list',
            'chats': user_chats
        }

    @staticmethod
    async def get_chat_messages(chat_id):

        messages = await get_chat_messages(chat_id)

        return {
            'type': 'chat_messages',
            'messages': messages
        }

    @staticmethod
    async def delete_chat(chat_id, user):

        participants_id_list = await delete_chat(chat_id, user)

        return participants_id_list

    @staticmethod
    async def delete_chat_message(message_id, user):

        participants_id_list = await delete_message(message_id, user)

        return participants_id_list

    @staticmethod
    async def update_chat_message(message_id, user, new_message_content):

        participants_id_list = await update_message(message_id, user, new_message_content)

        return participants_id_list

    @staticmethod
    async def forward_chat_message(message_content, from_user_id, to_chat_id):

        participants_id_list = await save_forward_message(message_content, from_user_id, to_chat_id)

        return participants_id_list
