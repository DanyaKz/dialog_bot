from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import pymysql
import sys
import logging
import json
import time
from chat_func import Chat_init
import random


class Message_init(Chat_init):
    def __init__(self,API_TOKEN):
        super().__init__()
        logging.basicConfig(level=logging.INFO)
        self.bot = Bot(token=API_TOKEN)
        self.dp = Dispatcher(self.bot)
        self.owner = 000000000 #owner's telegram id
        with open('msgs.json', encoding='utf-8') as f:
            self.KB = json.load(f)

    def execute_bot(self):
        executor.start_polling(self.dp, skip_updates=True)

    def start_handler(self):
        @self.dp.message_handler(commands=['start'])
        async def process_start_command(message: types.Message):
            print(message)
            user_id = message['from']['id']
            isExists = self.is_user_exists(user_id)
            if isExists:
                data = self.select_all_from_users(user_id)
                data = {'user_id':user_id,'first_name':data['first_name'],'login':data['login']}
                await self.bot.send_message(user_id, 
                f"{self.KB['start_msg_user_exists']}\n{self.KB['random']}\n{await self.get_gen_info(data)}",
                parse_mode='HTML')
            else:
                await self.bot.send_message(user_id, self.KB['start_msg_user_not_exists'])
                self.user_first_act(user_id)
                await self.bot.send_message(user_id, 'Введите Ваше имя:')

    def kb_button_handler(self):
        @self.dp.message_handler(content_types='text') #content_types='text'
        async def kb_btn(message: types.Message):
            user_id = message['from']['id']
            isExists = self.is_user_exists(user_id)
            if isExists:
                is_busy = self.is_busy(user_id)['busy']
                check_user_req = self.check_requests_where_false(user_id)
                if not bool(is_busy) and not bool(check_user_req):
                    await self.user_is_free(user_id,message)
                else:
                    await self.chat_message_handler(int(user_id), message)
            else:
                await self.bot.send_message(user_id, self.KB['start_msg_user_not_exists'])
                self.user_first_act(user_id)
                await self.bot.send_message(user_id, 'Введите Ваше имя:')

    def random_handler(self):
        @self.dp.message_handler(commands=['random'])
        async def process_random_command(message: types.Message):
            print(message)
            user_id = message['from']['id']
            isExists = self.is_user_exists(user_id)
            if isExists:
                check_user_req = self.check_requests_where_false(user_id)
                check_user_q = self.select_all_from_queue_user_id(user_id)
                last_act = self.get_action(user_id)['act']

                if not bool(check_user_req) and not bool(check_user_q) and last_act not in [1,2]:
                    self.insert_into_queue(user_id)
                    add_to_req = await self.add_to_req()
                    await self.bot.send_message(user_id, f"{self.KB['random_response_1']}")
                    if add_to_req[0]:
                        for i in add_to_req[1]:
                            self.queue_set_true(i)
                            self.set_busy(i)
                        friend_name = await self.friend_name(i)

                        await self.bot.send_message(friend_name[0]['id'],
                            f"Cобеседник найден!\nВаш собеседник(ца) <b>{friend_name[1]['first_name']}</b>\n{self.KB['to_stop']}",
                            parse_mode='HTML')
                        await self.bot.send_message(friend_name[1]['id'],
                            f"Cобеседник найден!\nВаш собеседник(ца) <b>{friend_name[0]['first_name']}</b>\n{self.KB['to_stop']}",
                            parse_mode='HTML')
            else:
                await self.bot.send_message(user_id, self.KB['start_msg_user_not_exists'])
                self.user_first_act(user_id)
                await self.bot.send_message(user_id, 'Введите Ваше имя:')


    async def user_is_free(self, user_id, message):
        last_act = self.get_action(user_id)['act']
        if last_act == 1:
            data = {
                'user_id':user_id,
                'act':1,
                'act_msg':message.text
            }
            self.set_action_messages(data)
            self.set_last_act({'user_id':user_id,'act':2})
            await self.bot.send_message(user_id, 'Придумайте логин:')
        elif last_act == 2:
            data = {
                'user_id':user_id,
                'act':2,
                'act_msg':message.text
            }
            self.set_action_messages(data)
            send_msg = await self.registration(user_id)
            self.set_last_act({'user_id':user_id,'act':3})
            await self.bot.send_message(user_id, send_msg , parse_mode='HTML')
            await self.bot.send_message(user_id, "Для поиска собеседника введите, либо нажмите команду /random" , parse_mode='HTML')
        # set 3//4 for hobbies , ask to write messages of hobbies, then user set /confirm_hobbies
        elif last_act not in [1,2]:
            await self.bot.send_message(user_id, f"Вы готовы к общению!\n{self.KB['random']}")

    def stop_handler(self):
        @self.dp.message_handler(commands=['stop'])
        async def process_stop_command(message: types.Message):
            user_id = message['from']['id']
            isExists = self.is_user_exists(user_id)
            if isExists:
                last_act = self.get_action(user_id)['act']
                check_user = self.is_busy(user_id)['busy']
                check_user_req = self.check_requests_where_false(user_id)
                users_list = [check_user_req['req_from'],check_user_req['req_to']]
                if bool(check_user) and bool(check_user_req) and last_act not in [1,2]:
                    await self.bot.send_message(user_id, 
            """<i><u><b>Вы действительно хотите завершить диалог?</b></u> 
    Если <b>да</b>, то нажмите на подтверждающую команду, либо же ведите её /confirm.
    Если вы передумали, либо же нажали стоп-команду случайно, то просто проигнорируйте это сообщение.</i>""",
                parse_mode='HTML')

    async def chat_message_handler(self, user_id, msg):
        data = {
            'user_id':user_id,
            'text':msg.text
        }
        to_send = await self.add_messages(data)
        await self.bot.send_message(to_send['to'], to_send['text'], parse_mode='HTML')

    def confirm_handler(self):
        @self.dp.message_handler(commands=['confirm'])
        async def process_end_command(message: types.Message):
            print(message)
            user_id = message['from']['id']
            isExists = self.is_user_exists(user_id)
            if isExists :
                last_act = self.get_action(user_id)['act']
                check_user = self.is_busy(user_id)['busy']
                check_user_req = self.check_requests_where_false(user_id)
                users_list = [check_user_req['req_from'],check_user_req['req_to']]
                print(users_list)
                if bool(check_user) and bool(check_user_req) and last_act not in [1,2]:
                    self.end_conversation_requests(check_user_req['req_id'])
                    for i in users_list:
                        self.set_busy_false(i)
                        await self.bot.send_message(i,
                            f"""Диалог был завершен.Для поиска нового собеседника нажмите на данную команду /random , либо же напечатайте""",
                            parse_mode='HTML')
    
    def cancel_handler(self):
        @self.dp.message_handler(commands=['cancel'])
        async def process_end_command(message: types.Message):
            print(message)
            user_id = message['from']['id']
            isExists = self.is_user_exists(user_id)
            if isExists :
                last_act = self.get_action(user_id)['act']
                check_user = self.is_busy(user_id)['busy']
                check_user_req = self.check_requests_where_false(user_id)
                print(bool(check_user) , bool(check_user_req))
                if not bool(check_user) and not bool(check_user_req) and last_act not in [1,2]:
                    self.queue_set_true(user_id)
                    await self.bot.send_message(user_id,
                            f"""Вы отменили запрос на поиск нового собеседника, если вы это сделали случайно, либо все же захотите пообщаться, то нажмите на данную команду /random , либо же напечатайте""",
                            parse_mode='HTML')