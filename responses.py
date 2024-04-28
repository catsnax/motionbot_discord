import random


def get_response(user_input):
    lowered = user_input.lower()

    if lowered == '':
        return 'empty'
    elif 'hello' in lowered:
        return 'hello world'
