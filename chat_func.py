import pymysql
import sys
import asyncio
import json
import time
from db import DataBase


class Chat_init(DataBase):
    def __init__(self):
        super().__init__()
        self.alphabet = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е':'e','ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
            'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
            'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ы': 'i', 'э': 'e', 
            'ю': 'yu','я': 'ya','ь':'','ъ':'',')':'','(':'','[':'',']':'','{':'','}':'',':':'','+':'','ә':'a',
            'ғ':'g','қ':'k','ң':'n','ө':'o','ұ':'y','ү':'y','һ':'h','і':'i','?':''}


    async def slugify(self, s):
        new = ''
        for i in s.lower() :
            if i == ' ':
                new+='_'
            else : 
                new+=self.alphabet.get(i,i)
        return new

    async def registration(self,user_id):
        data = self.get_final_act_inf(user_id)
        data = {
            'user_id':user_id,
            'first_name':data[0]['act_msg'],
            'login':await self.slugify(data[1]['act_msg'])
        }
        self.set_final_inf(data)

        return "Регистрация успешно завершена!\n" + await self.get_gen_info(data)
    
    async def get_gen_info(self,data):
        send_msg = f"""
        Ваше имя <b>{data['first_name']}</b>,
        Ваш логин <b>{data['login']}</b>,
        Ваш id <b>{data['user_id']}</b>
        """
        return send_msg
    
    async def add_to_req(self):
        free_users = self.select_all_from_queue()
        id_free_users = []
        
        if len(free_users) == 2:
            for i in free_users:
                id_free_users.append(i['user_id'])
            self.insert_into_requests(id_free_users)
            return (True,id_free_users)
        else:
            return (False,)
    
    async def friend_name(self, user_id):
        friends_list = self.check_requests_where_false(user_id)
        friends_list = [friends_list['req_from'],friends_list['req_to']]
        to_return = []
        for i in friends_list:
            user_data = self.select_all_from_users(i)
            to_append = {'id':user_data['user_id'],
                        'first_name':user_data['first_name']}
            to_return.append(to_append)
        return to_return

    async def add_messages(self, data):
        friends_list = self.check_requests_where_false(data['user_id'])
        message_from = data['user_id']
        if message_from != friends_list['req_from']:
            message_to = friends_list['req_from']
        else:
            message_to = friends_list['req_to']
        insert_data = {
            'from':message_from,
            'to':message_to,
            'text':data['text']
        }
        self.insert_into_messages(insert_data)
        return insert_data

