import json

from telegram import *
from telegram.ext import *

token = "5904482142:AAG-8soDFD0FcdR7Oy_ZTLLxLfyKYQmPoUk"


WAIT, ADD, MODIFY, DELETE, LIST, LOGIN, LOGIN_CHOOSE_MODIFY, LOGIN_MODIFY = range(8)

global status
status = WAIT


add_shoe_name = None
add_shoe_stop_loss = None
add_shoe_backup_price = None

delete_shoe_name = None

modify_shoe_name = None
modify_shoe_stop_loss = None
modify_shoe_action = None
modify_shoe_new_stop_loss = None
modify_shoe_new_backup_price = None

login_email = None
login_password = None

login_modify_email = None
login_modify_password = None


# Function to check if the user has permission to use the bot
def user_has_permission(id) -> bool:
    bot_access_list = json.load(open("data/telegram/bot_access.json"))
    for user in bot_access_list:
        if user["id"] == id:
            return True
    return False


# Function to handle the start command
def start(update: Update, context: CallbackContext) -> None:

    buttons = get_start_menu()

    user = update.message.from_user
    texts = json.load(open("data/telegram/texts.json", encoding="utf8"))

    if user_has_permission(user["id"]):
        context.bot.send_message(chat_id=update.effective_chat.id, text=texts["welcome"], reply_markup=ReplyKeyboardMarkup(buttons))
    else:
        update.message.reply_text(texts["no_permission"])


# Function to handle the messages
def messageHandler(update: Update, context: CallbackContext) -> None:

    global status

    message_text = update.message.text
    buttons_actions = get_buttons_actions()

    user = update.message.from_user
    texts = json.load(open("data/telegram/texts.json", encoding="utf8"))

    if user_has_permission(user["id"]):
        if message_text == "❌ Annulla":
            cancel_action()
            status = WAIT
            context.bot.send_message(chat_id=update.effective_chat.id, text="🟩 Azione annullata con successo", reply_markup=ReplyKeyboardMarkup(get_start_menu()))

        if buttons_actions[0] in message_text or status is ADD:
            handle_add_shoe_action(update, context)
        if buttons_actions[1] in message_text or status is MODIFY:
            handle_modify_shoe_action(update, context)
        if buttons_actions[2] in message_text or status is DELETE:
            handle_delete_shoe_action(update, context)
        if buttons_actions[3] in message_text or status is LIST:
            handle_shoes_list_action(update, context)
        if buttons_actions[4] in message_text or status is LOGIN or status is LOGIN_CHOOSE_MODIFY or status is LOGIN_MODIFY:
            handle_login_action(update, context)
    else:
        update.message.reply_text(texts["no_permission"])


# Function to handle the “Add Shoe” action
def handle_add_shoe_action(update: Update, context: CallbackContext) -> None:

    global status
    global add_shoe_name
    global add_shoe_stop_loss
    global add_shoe_backup_price

    if status == WAIT:
        status = ADD
        context.bot.send_message(chat_id=update.effective_chat.id, text="👞 Dimmi il nome della scarpa da aggiungere...", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text="❌ Annulla")]]))
        return

    if status == ADD:

        if add_shoe_name is None:
            add_shoe_name = update.message.text
            if is_shoe_present(add_shoe_name) is False:
                context.bot.send_message(chat_id=update.effective_chat.id, text="💶 Adesso dimmi il prezzo minimo che questa scarpa può raggiungere...", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text="❌ Annulla")]]))
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 E' già presente una scarpa con questo nome all'interno della lista, azione annullata!", reply_markup=ReplyKeyboardMarkup(get_start_menu()))
                status = WAIT
                cancel_action()
            return

        if add_shoe_stop_loss is None:
            try:
                add_shoe_stop_loss = int(update.message.text.replace('€', ''))
                context.bot.send_message(chat_id=update.effective_chat.id, text="📮 Adesso dimmi il prezzo di backup", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text="❌ Annulla")]]))
            except ValueError:
                context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Lo stop loss inserito non è un numero! Azione annullata!", reply_markup=ReplyKeyboardMarkup(get_start_menu()))
                status = WAIT
                cancel_action()
            return

        if add_shoe_backup_price is None:
            try:
                add_shoe_backup_price = int(update.message.text.replace('€', ''))
                save_shoe(add_shoe_name, add_shoe_stop_loss, add_shoe_backup_price)
                context.bot.send_message(chat_id=update.effective_chat.id, text="🟩 Scarpa aggiunta correttamente", reply_markup=ReplyKeyboardMarkup(get_start_menu()))
            except ValueError:
                context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Il prezzo di backup inserito non è un numero! Azione annullata!", reply_markup=ReplyKeyboardMarkup(get_start_menu()))
            status = WAIT
            cancel_action()
            return


# Function to check if a shoe is already inside the stop loss list
def is_shoe_present(name: str) -> bool:

    stop_losses_data = json.load(open("data/shoes/stop_losses.json"))
    for stop_loss in stop_losses_data:
        if stop_loss["name"] == name:
            return True

    return False


# Function to save a shoe in the stop loss json
def save_shoe(name: str, stop_loss: int, backup_price: int) -> None:

    stop_losses_file_path = "data/shoes/stop_losses.json"

    new_shoe_dictionary = {
        "name": name,
        "stop_loss_euro": stop_loss,
        "backup_price_euro": backup_price
    }

    stop_losses_data = json.load(open(stop_losses_file_path))
    stop_losses_data.append(new_shoe_dictionary)

    with open(stop_losses_file_path, "w") as outfile:
        outfile.write(json.dumps(stop_losses_data, indent=4))


# Function to handle the “Delete Shoe” action
def handle_delete_shoe_action(update: Update, context: CallbackContext) -> None:

    global status
    global delete_shoe_name

    if status == WAIT:

        shoes_buttons = [[KeyboardButton(text="❌ Annulla")]]

        status = DELETE
        for shoe in get_stop_losses_list():
            shoes_buttons.append([KeyboardButton(text=f"👞 {shoe['name']}")])

        shoes_buttons.append([KeyboardButton(text="❌ Annulla")])

        context.bot.send_message(chat_id=update.effective_chat.id, text="Seleziona la scarpa da eliminare:", reply_markup=ReplyKeyboardMarkup(shoes_buttons))
        return

    if status == DELETE:

        if delete_shoe_name is None:
            delete_shoe_name = update.message.text
            if delete_shoe(delete_shoe_name.replace("👞 ", "")):
                context.bot.send_message(chat_id=update.effective_chat.id, text="🟩 Scarpa eliminata con successo!", reply_markup=ReplyKeyboardMarkup(get_start_menu()))
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"🛑 Mi dispiace, non è stata trovata nessuna scarpa con il nome {delete_shoe_name}")
            status = WAIT
            cancel_action()
            return


# Function to delete a shoe inside the stop loss json
def delete_shoe(shoe_name: str) -> bool:

    stop_loss_data = get_stop_losses_list()
    found = False

    for shoe in stop_loss_data:
        if shoe["name"] == shoe_name:
            stop_loss_data.remove(shoe)
            found = True
            break

    if found:
        with open("data/shoes/stop_losses.json", "w") as outfile:
            outfile.write(json.dumps(stop_loss_data, indent=4))

    return found


# Function to handle the “Modify Shoe” action
def handle_modify_shoe_action(update: Update, context: CallbackContext) -> None:

    global status
    global modify_shoe_name
    global modify_shoe_stop_loss
    global modify_shoe_action
    global modify_shoe_new_stop_loss
    global modify_shoe_new_backup_price

    start_menu = get_start_menu()

    if status == WAIT:

        shoes_buttons = [[KeyboardButton(text="❌ Annulla")]]

        status = MODIFY
        for shoe in get_stop_losses_list():
            shoes_buttons.append([KeyboardButton(text=f"👞 {shoe['name']}")])

        shoes_buttons.append([KeyboardButton(text="❌ Annulla")])

        context.bot.send_message(chat_id=update.effective_chat.id, text="Seleziona la scarpa da modificare:", reply_markup=ReplyKeyboardMarkup(shoes_buttons))
        return

    if status == MODIFY:
        if modify_shoe_name is None:
            modify_shoe_menu = [
                [KeyboardButton(text="❌ Annulla")],
                [KeyboardButton(text="🛑 Stop loss")],
                [KeyboardButton(text="📮 Prezzo backup")],
                [KeyboardButton(text="❌ Annulla")]
            ]
            modify_shoe_name = update.message.text.replace("👞 ", "")
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Seleziona cosa vuoi modificare delle {modify_shoe_name}:", reply_markup=ReplyKeyboardMarkup(modify_shoe_menu))
            return

        if modify_shoe_action is None:
            modify_shoe_action = update.message.text[2:]
            if modify_shoe_action == "Stop loss":
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"🛑 Inserisci il nuovo stop loss:", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text="❌ Annulla")]]))
            if modify_shoe_action == "Prezzo backup":
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"📮 Inserisci il nuovo prezzo di backup:", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text="❌ Annulla")]]))
            return

        if modify_shoe_action == "Stop loss":
            try:
                modify_shoe_new_stop_loss = int(update.message.text.replace('€', ''))
                if modify_shoe(modify_shoe_name, modify_shoe_new_stop_loss, None):
                    context.bot.send_message(chat_id=update.effective_chat.id, text="🔃 Scarpa aggiornata con successo!", reply_markup=ReplyKeyboardMarkup(start_menu))
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"🛑 Mi dispiace, non è stata trovata nessuna scarpa con il nome {delete_shoe_name}", reply_markup=ReplyKeyboardMarkup(start_menu))
            except ValueError:
                context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Lo stop loss inserito non è un numero! Azione annullata!", reply_markup=ReplyKeyboardMarkup(start_menu))
            cancel_action()
            status = WAIT
            return

        if modify_shoe_action == "Prezzo backup":
            try:
                modify_shoe_new_backup_price = int(update.message.text.replace('€', ''))
                if modify_shoe(modify_shoe_name, None, modify_shoe_new_backup_price):
                    context.bot.send_message(chat_id=update.effective_chat.id, text="🔃 Scarpa aggiornata con successo!", reply_markup=ReplyKeyboardMarkup(start_menu))
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"🛑 Mi dispiace, non è stata trovata nessuna scarpa con il nome {delete_shoe_name}", reply_markup=ReplyKeyboardMarkup(start_menu))
            except ValueError:
                context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Il prezzo di backup inserito non è un numero! Azione annullata!", reply_markup=ReplyKeyboardMarkup(start_menu))
            cancel_action()
            status = WAIT
            return

        """
        if modify_shoe_stop_loss is None:
            modify_shoe_stop_loss = update.message.text
            try:
                if modify_shoe(modify_shoe_name, int(modify_shoe_stop_loss)):
                    context.bot.send_message(chat_id=update.effective_chat.id, text="🔃 Scarpa aggiornata con successo!", reply_markup=ReplyKeyboardMarkup(start_menu))
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"🛑 Mi dispiace, non è stata trovata nessuna scarpa con il nome {delete_shoe_name}", reply_markup=ReplyKeyboardMarkup(start_menu))
            except ValueError:
                context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 Lo stop loss inserito non è un numero! Azione annullata!", reply_markup=ReplyKeyboardMarkup(start_menu))
            status = WAIT
            cancel_action()
            return
        """


# Function to modify a shoe inside the stop loss json
def modify_shoe(shoe_name: str, shoe_stop_loss: int | None, shoe_backup_price: int | None) -> bool:

    stop_loss_data = get_stop_losses_list()
    found = False

    for shoe in stop_loss_data:
        if shoe["name"] == shoe_name:
            if shoe_stop_loss is not None:
                shoe["stop_loss_euro"] = shoe_stop_loss
            if shoe_backup_price is not None:
                shoe["backup_price_euro"] = shoe_backup_price
            found = True
            break

    if found:
        with open("data/shoes/stop_losses.json", "w") as outfile:
            outfile.write(json.dumps(stop_loss_data, indent=4))

    return found


# Function to handle the “Shoes List” action
def handle_shoes_list_action(update: Update, context: CallbackContext) -> None:
    shoes_list = get_shoes_list()
    stop_losses_list = get_stop_losses_list()

    message_output = ""
    for shoe in shoes_list:

        actual_stop_loss = None
        actual_backup_price = None

        for stop_loss in stop_losses_list:
            if shoe["name"] == stop_loss["name"]:
                actual_stop_loss = stop_loss["stop_loss_euro"]
                actual_backup_price = stop_loss["backup_price_euro"]
                break

        message_output = message_output + f"👞 Nome: {shoe['name']}\nℹ️ ID: {shoe['id']}\n🔢 Taglia: {shoe['size']}\n💸 Prezzo attuale: {shoe['price_euro']}€\n"
        if actual_stop_loss is not None:
            message_output = message_output + f"🛑 Stop loss: {str(actual_stop_loss)}€\n"
        else:
            message_output = message_output + "🛑 Stop loss: Non impostato\n"

        if actual_backup_price is not None:
            message_output = message_output + f"📮 Backup price: {str(actual_backup_price)}€\n"
        else:
            message_output = message_output + f"📮 Backup price: Non impostato\n"

        message_output = message_output + "\n"

    context.bot.send_message(chat_id=update.effective_chat.id, text=message_output)


# Function to handle the "Login" action
def handle_login_action(update: Update, context: CallbackContext) -> None:

    global status
    global login_email
    global login_password
    global login_modify_email
    global login_modify_password

    start_menu = get_start_menu()
    current_login_data = get_login_data()

    if status == WAIT:
        if current_login_data["email"] is None or current_login_data["email"] == "" or current_login_data["password"] is None or current_login_data["password"] == "":
            status = LOGIN
            context.bot.send_message(chat_id=update.effective_chat.id, text="Non sono presenti dati di login nel bot\n📧 Scrivimi l'email per inserirla", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text="❌ Annulla")]]))
            return
        else:
            buttons = [
                [KeyboardButton(text="✏️ Modifica dati")],
                [KeyboardButton(text="🗑️ Elimina dati")],
                [KeyboardButton(text="❌ Annulla")]
            ]

            login_email = current_login_data["email"]
            login_password = current_login_data["password"]

            status = LOGIN_CHOOSE_MODIFY

            context.bot.send_message(chat_id=update.effective_chat.id, text="🎲 Sono già presenti dei dati di accesso, seleziona l'azione dai pulsanti qua sotto", reply_markup=ReplyKeyboardMarkup(buttons))

    if status == LOGIN:
        if login_email is None:
            login_email = update.message.text
            context.bot.send_message(chat_id=update.effective_chat.id, text="🔑 Scrivimi la password", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text="❌ Annulla")]]))
            return
        if login_password is None:

            login_password = update.message.text
            context.bot.send_message(chat_id=update.effective_chat.id, text="🟩 Sono stati inseriti i nuovi dati di accesso", reply_markup=ReplyKeyboardMarkup(start_menu))
            status = WAIT

            login_data = {
                "email": login_email,
                "password": login_password
            }

            with open("data/login_data.json", "w") as outfile:
                outfile.write(json.dumps(login_data, indent=4))
            cancel_action()
            return

    if status == LOGIN_CHOOSE_MODIFY:

        if "✏️ Modifica dati" in update.message.text:

            login_modify_email = None
            login_modify_password = None

            status = LOGIN_MODIFY

            context.bot.send_message(chat_id=update.effective_chat.id, text="📧 Inserisci l'email", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text="❌ Annulla")]]))
            return

        if "🗑️ Elimina dati" in update.message.text:

            login_email = None
            login_password = None
            delete_login_data()

            status = WAIT
            context.bot.send_message(chat_id=update.effective_chat.id, text="🟩 Dati di accesso eliminati correttamente", reply_markup=ReplyKeyboardMarkup(start_menu))
            return

    if status == LOGIN_MODIFY:
        if login_modify_email is None:
            login_modify_email = update.message.text
            context.bot.send_message(chat_id=update.effective_chat.id, text="🔐 Inserisci la password", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text="❌ Annulla")]]))
            return

        if login_modify_password is None:
            login_modify_password = update.message.text
            if modify_login_data(login_modify_email, login_modify_password):
                context.bot.send_message(chat_id=update.effective_chat.id, text="🟩 Dati di accesso aggiornati correttamente", reply_markup=ReplyKeyboardMarkup(start_menu))
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="🛑 E' stato riscontrato un errore nell'aggiornamento dei dati di accesso", reply_markup=ReplyKeyboardMarkup(start_menu))
            status = WAIT
            cancel_action()
            return


def modify_login_data(email: str, password: str) -> bool:
    try:
        new_login_data = {
            "email": email,
            "password": password
        }
        with open("data/login_data.json", "w") as outfile:
            outfile.write(json.dumps(new_login_data, indent=4))
        cancel_action()
        return True
    except:
        return False


# Get the data from the loaded shoes json file
def get_shoes_list():
    return json.load(open("data/shoes/loaded_shoes.json"))


# Get the data from the stop losses json file
def get_stop_losses_list():
    return json.load(open("data/shoes/stop_losses.json"))


# Get the data from the buttons json file
def get_buttons_actions():
    return json.load(open("data/telegram/texts.json", encoding="utf8"))["buttons_action"]


# Get the login data
def get_login_data():
    return json.load(open("data/login_data.json"))


# Cancel the actual action
def cancel_action():

    global status
    global add_shoe_name
    global add_shoe_stop_loss
    global add_shoe_backup_price
    global delete_shoe_name
    global modify_shoe_name
    global modify_shoe_stop_loss
    global modify_shoe_new_stop_loss
    global modify_shoe_new_backup_price
    global modify_shoe_action
    global login_email
    global login_password
    global login_modify_email
    global login_modify_password

    status = WAIT
    add_shoe_name = None
    add_shoe_stop_loss = None
    add_shoe_backup_price = None
    delete_shoe_name = None
    modify_shoe_name = None
    modify_shoe_stop_loss = None
    modify_shoe_new_stop_loss = None
    modify_shoe_new_backup_price = None
    modify_shoe_action = None
    login_email = None
    login_password = None
    login_modify_email = None
    login_modify_password = None


# Delete login data
def delete_login_data():
    new_dictionary = {
        "email": "",
        "password": ""
    }
    with open("data/login_data.json", "w") as outfile:
        outfile.write(json.dumps(new_dictionary, indent=4))


def get_start_menu() -> list:
    buttons_data = get_buttons_actions()
    buttons = []
    for button in buttons_data:
        button_list = [KeyboardButton(text=button)]
        buttons.append(button_list)
    return buttons


updater = Updater(token=token)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text, messageHandler))

updater.start_polling()
