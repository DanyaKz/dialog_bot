import pymysql
import sys
from datetime import datetime


class DataBase():
    def __init__(self):

        self.conn =  pymysql.connect(host='host',
                             user='user',
                             password='your_password',
                             database='your_database',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.conn.cursor()

    def is_user_exists(self,data):
        self.cur.execute(f'select * from users where user_id = {int(data)}')
        isExist = self.cur.fetchone()
        if isExist:
            return True
        else:
            return False 
    
    def user_first_act(self,user_id):
        self.cur.execute(f'insert into users (user_id, first_name, login,act,busy)'
                            f"values({int(user_id)},'x','x',1,false)")
        self.conn.commit()
    
    def select_all_from_users(self,user_id):
        self.cur.execute(f'select * from users where user_id = {int(user_id)}')
        user = self.cur.fetchone()
        return user

    def is_busy(self,user_id):
        self.cur.execute(f'select busy from users where user_id = {int(user_id)}')
        return self.cur.fetchone()
    
    def update_user_act(self,data):
        self.cur.execute(f"update users set act = {data['act']} where user_id = {int(data['user_id'])};")
        self.conn.commit()
    
    def get_action(self, user_id):
        self.cur.execute(f'select act from users where user_id = {int(user_id)}')
        return self.cur.fetchone()
    
    def set_last_act(self, data):
        self.cur.execute(f"update users set act = {data['act']} where user_id = {int(data['user_id'])};")
        self.conn.commit()
    
    def set_action_messages(self,data):
        self.cur.execute(f"insert into action_messages(user_id,act,act_msg) values ({data['user_id']},{data['act']},'{data['act_msg']}');")
        self.conn.commit()
    
    def get_final_act_inf(self, user_id):
        self.cur.execute(f'select * from action_messages where user_id = {int(user_id)}')
        return self.cur.fetchall()

    def set_final_inf(self,data):
        self.cur.execute(f"update users set first_name = '{data['first_name']}' , login = '{data['login']}' where user_id = {int(data['user_id'])};")
        self.conn.commit()

    def insert_into_queue(self,user_id):
        self.cur.execute(f"insert into queue(user_id,is_accepted)value({int(user_id)},false);")
        self.conn.commit()

    def select_all_from_queue_user_id(self, user_id):
        self.cur.execute(f'select * from queue where is_accepted = false and user_id = {int(user_id)}')
        return self.cur.fetchall()

    def select_all_from_queue(self):
        self.cur.execute(f'select * from queue where is_accepted = false')
        return self.cur.fetchall()
    
    def insert_into_requests(self,data):
        now = datetime.now()
        self.cur.execute(f"""insert into requests(req_time,start_time,end_time,req_from,req_to,is_it_aproved,is_it_end)
                            value('{now}','{now}','{now}',{data[0]},{data[1]},true,false)""")
        self.conn.commit()
    
    def queue_set_true(self,user_id):
        self.cur.execute(f"update queue set is_accepted = true where user_id = {user_id};")
        self.conn.commit()
    
    def set_busy(self,user_id):
        self.cur.execute(f'update users set busy = true where user_id = {int(user_id)};')
        self.conn.commit()
    
    def set_busy_false(self,user_id):
        self.cur.execute(f'update users set busy = false where user_id = {int(user_id)};')
        self.conn.commit()
    
    def insert_into_messages(self,data):
        self.cur.execute(f"""insert into messages(f_user,s_user,message,m_time)
                            value({data['from']},{data['to']},'{data['text']}','{datetime.now()}')""")
        self.conn.commit()

    def check_requests_where_false(self,user_id):
        self.cur.execute(f'select * from requests where (req_from = {int(user_id)} or req_to = {int(user_id)}) and is_it_end = false')
        return self.cur.fetchone()
    
    def end_conversation_requests(self, data):
        self.cur.execute(f"update requests set is_it_end = true, end_time = '{datetime.now()}' where req_id = {data};")
        self.conn.commit()
