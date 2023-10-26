import telebot
import random
import sqlite3

bot = telebot.TeleBot('5681456371:AAEiQelZJqNzEwUhr89cXjujhVFdci1MhmY')

dreams = {}

conn = sqlite3.connect('data.db', check_same_thread=False)
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, dreams TEXT)')

# считывает команду start
@bot.message_handler(commands=['start'])
def start(message):
    who_gets = []
    who_gives = []
    entities = (message.chat.id, message.from_user.username)
    #cur.execute(f'INSERT OR IGNORE INTO users (user_id) VALUES ({message.chat.id})')
    tabele = cur.execute('''INSERT OR IGNORE INTO users (user_id, username) VALUES(?, ?)''', entities)
    mess = f"Hello, <b>{message.from_user.first_name} {message.from_user.last_name}, you are now in the game. Wait for a message that will indicate to whom you are giving a gift. Also, write your interests (in one message) or what you would like to receive for the New Year to make your Santa's life easier.</b>"
    if message.from_user.username not in who_gives:
        who_gives.append(message.from_user.username)
        who_gets.append(message.from_user.username)
        print("List of participants: ", who_gives)

        bot.send_message(message.chat.id, mess, parse_mode='html')
    else:
        bot.send_message(message.chat.id, "You're already on the list.")

    conn.commit()

@bot.message_handler(commands=['go'])
def go(message):
    if message.id == "admin_id":
        bot.send_message(message.chat.id, 'have begun')
        username = cur.execute(f'SELECT username FROM users')
        who_gives = username.fetchall()
        who_gets = list.copy(who_gives)


        while len(who_gives) != 0:
            partner_gives = random.choice(who_gives)  # Выбираем рандомно из списка дарящих
            partner_gets = random.choice(who_gets)  # Выбираем рандомно из списка получающих

            if partner_gets != partner_gives:
                #print(partner_gives, " дарит подарок ", partner_gets)
                ptgets = cur.execute(f'SELECT username, dreams FROM users WHERE (username) = ("{partner_gets[0]}")')#запрос для получения имени, кому дарят и мечты
                result = ptgets.fetchall()
                ptgives = cur.execute(f'SELECT user_id FROM users WHERE (username) = ("{partner_gives[0]}")')#Запрос для получения айди, кто дарит
                result_id = ptgives.fetchall()
                bot.send_message(result_id[0][0], f'{partner_gives[0]}, gives a gift , {result[0][0]}. Desire: {result[0][1]}') #отправка конечного сообщения


                if message.from_user.username == partner_gives:
                    bot.send_message(message.chat.id, "You're giving a gift", partner_gets)
                    print('The condition was fulfilled')

                who_gives.remove(partner_gives)
                who_gets.remove(partner_gets)


        conn.commit()
    else:
        bot.send_message(message.chat.id , "You don't have access")

#отвечает на присланный текст
@bot.message_handler(content_types=['text'])
def get_user_text(message):
    cur.execute(f'UPDATE users SET dreams = ("{message.text}") WHERE user_id = ("{message.chat.id}")')
    if message.from_user.username not in dreams:
        people = message.from_user.username
        dreams[people] = message.text
        bot.send_message(message.chat.id, 'Great, I wrote it down.')
    elif message.from_user.username in dreams:
        people = message.from_user.username
        dreams[people] = message.text
        bot.send_message(message.chat.id, 'You have changed your desire.')
    print(dreams)
    conn.commit()


bot.polling(none_stop=True)