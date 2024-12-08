import locale
import locales.eng.eng as eng
import locales.rus.rus as rus

def answer(msg):
    lang = locale.getlocale()
    if lang[0] == "ru_RU":
        print(eng.message[msg])
        return rus.message[msg]
    elif lang[0] == "en_US":
        print(eng.message[msg])
        return eng.message[msg]
    
answer("move_to_text_pos")