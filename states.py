from aiogram.fsm.state import StatesGroup, State

'''
TODO: Вспомогательные классы для FSM (машины состояний), 
а также фабрики Callback Data для кнопок Inline клавиатур

'''

class reg(StatesGroup):

    text_search = State()

    text_prompt = State()
    img_prompt = State()

