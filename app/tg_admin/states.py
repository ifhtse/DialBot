from aiogram.fsm.state import StatesGroup, State

class AdminState(StatesGroup):

    ADD_CHAT = State()
    DEL_CHAT = State()
    ADD_CHATS_BULK = State()

    ADD_ADMIN = State()
    DEL_ADMIN = State()
    SET_DELAYS = State()

    ADD_SCENARIO = State()
    ADD_PHOTO = State()

    ACCOUNT_PHONE = State()
    ACCOUNT_CODE = State()
    ACCOUNT_PASSWORD = State()