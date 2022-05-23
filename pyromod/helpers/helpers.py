from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ForceReply

def ikb(rows = []):
    lines = []
    for row in rows:
        line = []
        for button in row:
            button = btn(*button) # InlineKeyboardButton
            line.append(button)
        lines.append(line)
    return InlineKeyboardMarkup(inline_keyboard=lines)
    #return {'inline_keyboard': lines}

def btn(text, value, type = 'callback_data'):
    return InlineKeyboardButton(text, **{type: value})
    #return {'text': text, type: value}

# The inverse of above
def bki(keyboard):
    lines = []
    for row in keyboard.inline_keyboard:
        line = []
        for button in row:
            button = ntb(button) # btn() format
            line.append(button)
        lines.append(line)
    return lines
    #return ikb() format

def ntb(button):
    for btn_type in ['callback_data', 'url', 'switch_inline_query', 'switch_inline_query_current_chat', 'callback_game']:
        value = getattr(button, btn_type)
        if value:
            break
    button = [button.text, value]
    if btn_type != 'callback_data':
        button.append(btn_type)
    return button
    #return {'text': text, type: value}

def kb(rows = [], **kwargs):
    lines = []
    for row in rows:
        line = []
        for button in row:
            button_type = type(button)
            if button_type == str:
                button = KeyboardButton(button)
            elif button_type == dict:
                button = KeyboardButton(**button)
            
            line.append(button)
        lines.append(line)
    return ReplyKeyboardMarkup(keyboard=lines, **kwargs)

kbtn = KeyboardButton

def force_reply(selective=True):
    return ForceReply(selective=selective)

def array_chunk(input, size):
    return [input[i:i+size] for i in range(0, len(input), size)]

