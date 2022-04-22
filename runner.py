from message_handler import Message_init


class Runner(Message_init):
    def __init__(self):
        self.token = open('token.txt','r')
        super().__init__(*self.token)
    
    def run_funcs(self):
        self.start_handler()
        self.random_handler()
        self.stop_handler()
        self.confirm_handler()
        self.cancel_handler()
        # Hothing to input after this comment
        self.kb_button_handler()
        self.execute_bot()

bot = Runner()
bot.run_funcs()

