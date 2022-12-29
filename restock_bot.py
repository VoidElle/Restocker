import json
import re
import time
import webbrowser

import pyautogui
import pyperclip

from selenium import webdriver
from bs4 import BeautifulSoup

CURRENT_PAGE = 1
MAX_SHOES_PER_PAGE = 8

INITIAL_SHOE_COORDINATE_X, INITIAL_SHOE_COORDINATE_Y = 430, 350


def save_cookies(browser) -> None:
    with open("data/cookies.json", "w") as outfile:
        outfile.write(json.dumps(browser.get_cookies(), indent=4))
        # print("INFO: The cookies have been saved")


def load_cookies(browser: webdriver) -> None:
    cookies = json.load(open("data/cookies.json"))
    for cookie in cookies:
        browser.add_cookie(cookie)
    browser.refresh()
    # print("INFO: The cookies have been loaded")


def delete_all_cookies() -> None:
    with open("data/cookies.json", "w") as outfile:
        outfile.write(json.dumps([], indent=4))
        # print("INFO: The cookies have been deleted")


def remove_all_cookies(browser: webdriver) -> None:
    browser.delete_all_cookies()
    # print("INFO: The cookies have been removed from the current session")


def clear_cache(browser: webdriver) -> None:
    browser.execute_cdp_cmd('Storage.clearDataForOrigin', {
        "origin": "*",
        "storageTypes": "all",
    })
    # print("INFO: The cache have been deleted")


def go_to_my_account_section(browser: webdriver) -> bool:
    browser.get("https://restocks.net/it/account/")
    # print("INFO: Redirecting to the account section...")

    page_expire_point = pyautogui.locateCenterOnScreen("assets/utils/page_expired.png", confidence=0.6)
    # print(f"INFO: Page_Expire_Point Coordinates: {page_expire_point}")

    login_button_point = pyautogui.locateCenterOnScreen("assets/login_form/login_button.png", confidence=0.7)
    # print(f"INFO: Login_Button_Point Coordinates: {login_button_point}")

    initial_dialog_point = pyautogui.locateCenterOnScreen("assets/initial_dialog/save_button.png", confidence=0.92)
    # print(f"INFO: Initial_Dialog_Point Coordinates: {initial_dialog_point}")

    return page_expire_point is None and login_button_point is None and initial_dialog_point is None


def go_to_my_listing_section(browser: webdriver) -> None:
    browser.get("https://restocks.net/it/account/listings")
    # print("INFO: Redirecting to my listing section...")


def go_to_resale_section() -> bool:
    # print("INFO: Going to the resale section...")
    try:

        resale_button_x, resale_button_y = pyautogui.locateCenterOnScreen("assets/sections/resale_button.png",
                                                                          confidence=0.7)
        # print(f"INFO: Resale_Button Coordinates: {resale_button_x} | {resale_button_y}")
        pyautogui.moveTo(resale_button_x, resale_button_y)

        time.sleep(0.2)
        pyautogui.leftClick()
        return True
    except TypeError:
        return False


def make_login() -> bool:
    # print("INFO: Making the login...")

    try:
        email_form_x, email_form_y = pyautogui.locateCenterOnScreen("assets/login_form/email_login_form.png",
                                                                    confidence=0.6)
        # print(f"INFO: Email_Form Coordinates: {email_form_x} | {email_form_y}")

        password_form_x, password_form_y = pyautogui.locateCenterOnScreen("assets/login_form/password_login_form.png",
                                                                          confidence=0.6)
        # print(f"INFO: Password_Form Coordinates: {password_form_x} | {password_form_y}")

        login_button_x, login_button_y = pyautogui.locateCenterOnScreen("assets/login_form/login_button.png",
                                                                        confidence=0.7)
        # print(f"INFO: Login_Button Coordinates: {login_button_x} | {login_button_y}")
    except TypeError:
        return False

    login_email, login_password = get_login_data()

    pyautogui.moveTo(email_form_x, email_form_y)
    time.sleep(0.2)
    pyautogui.leftClick()
    for char in login_email:
        if char == "@":
            pyperclip.copy("@")
            pyautogui.hotkey("ctrl", "v")
        else:
            pyautogui.typewrite(char)

    pyautogui.moveTo(password_form_x, password_form_y)
    time.sleep(0.2)
    pyautogui.leftClick()
    pyautogui.typewrite(login_password, interval=0.1)

    pyautogui.moveTo(login_button_x, login_button_y)
    time.sleep(0.2)
    pyautogui.leftClick()

    return True


def gather_shoes_info(page_source_code: str) -> None:
    # print("INFO: Gathering the shoes info from the page...")

    shoes_list = []

    source_code_soup = BeautifulSoup(page_source_code, "html.parser")
    all_shoes = source_code_soup.findAll('tr', {'class': 'clickable'})

    shoes_soup = BeautifulSoup(str(all_shoes), "html.parser")
    all_shoes_images = shoes_soup.find_all('img')

    all_shoes_clear = BeautifulSoup(str(all_shoes), "html.parser").get_text().split(',')
    i = 0
    for shoe in all_shoes_clear:

        clear_shoe = re.sub(r'[ \n]{2,}', '     ', shoe).strip().split('     ')

        if '[' in clear_shoe:
            clear_shoe.remove('[')
        if ']' in clear_shoe:
            clear_shoe.remove(']')

        shoe_dictionary = {
            'name': clear_shoe[0],
            'size': clear_shoe[1].replace('EU: ', ''),
            'id': clear_shoe[2].replace('ID: ', ''),
            'price_euro': int(clear_shoe[3].replace('€ ', '')),
            'expiration': clear_shoe[5],
            'most_economic': "storeprice red" not in str(shoes_soup).split(',')[i],
            'image': None
        }
        shoes_list.append(shoe_dictionary)
        i += 1

    i = 0
    for shoe_item in shoes_list:
        shoe_item['image'] = all_shoes_images[i].get('src')
        i += 1

    with open("data/shoes/loaded_shoes.json", "w") as outfile:
        outfile.write(json.dumps(shoes_list, indent=4))


def get_login_data() -> (str, str):
    login_data = json.load(open("data/login_data.json"))
    # print("INFO: Getting the login data...")
    return login_data["email"], login_data["password"]


def accept_initial_dialog() -> bool:
    # print("INFO: Accepting the initial dialog...")
    try:
        accept_button_x, accept_button_y = pyautogui.locateCenterOnScreen("assets/initial_dialog/save_button.png",
                                                                          confidence=0.6)
        # print(f"INFO: Accept Initial Dialog Button Coordinates {accept_button_x} | {accept_button_y}")
        pyautogui.moveTo(accept_button_x, accept_button_y)
        time.sleep(0.2)
        pyautogui.leftClick()
        return True
    except TypeError:
        return False


def get_shoes_prices_data():
    # print("INFO: Getting the shoes prices...")
    return json.load(open("data/shoes/stop_losses.json"))


def can_be_decremented(shoe_name: str, current_price: int) -> bool:
    print(f"INFO: Check if the shoe {shoe_name} with the price {current_price} can be decremented...")
    stop_loss = get_stop_loss(shoe_name)
    result = stop_loss != -1 and current_price > stop_loss
    print(f"INFO: The shoe {shoe_name} ca be decremented? {result}")
    return result


def get_stop_loss(shoe_name: str) -> int:
    # print(f"INFO: Getting the stop loss of the {shoe_name}...")
    shoes_prices = get_shoes_prices_data()
    for shoe_price in shoes_prices:
        if shoe_price["name"] == shoe_name:
            return shoe_price["stop_loss_euro"]
    return -1


def get_backup_price(shoe_name: str) -> int:
    shoes_prices = get_shoes_prices_data()
    for shoe_price in shoes_prices:
        if shoe_price["name"] == shoe_name:
            return shoe_price["backup_price_euro"]
    return -1


def decrement_price(initial_shoe_coordinate_x: int, initial_shoe_coordinate_y: int, current_price: int) -> None:
    # print("INFO: Decrementing a shoe price...")

    # Move on the price form
    price_form_x, price_form_y = initial_shoe_coordinate_x + 35, initial_shoe_coordinate_y + 105
    pyautogui.moveTo(price_form_x, price_form_y)

    pyautogui.leftClick()
    time.sleep(0.2)

    # Remove the old price
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('del')

    # Put the new price
    pyautogui.typewrite(str(current_price - 1), interval=0.1)
    time.sleep(0.2)


def save_price() -> None:
    # print("INFO: Saving a price...")

    save_button_x, save_button_y = pyautogui.locateCenterOnScreen("assets/shoes/save_shoe.png", confidence=0.6)
    # print(f"INFO: Save Button Coordinates {save_button_x} | {save_button_y}")
    pyautogui.moveTo(save_button_x, save_button_y)

    time.sleep(0.2)
    pyautogui.leftClick()


def get_loaded_shoes():
    return json.load(open("data/shoes/loaded_shoes.json"))


def accept_cookies():
    try:
        accept_cookies_button_x, accept_cookies_button_y = pyautogui.locateCenterOnScreen("assets/utils/accept_cookies.png", confidence=0.6)
        pyautogui.moveTo(accept_cookies_button_x, accept_cookies_button_y)
        time.sleep(0.2)
        pyautogui.leftClick()
    except TypeError:
        return


previous_scroll_y = None
j = 0


def scroll_to_next_shoe(browser: webbrowser):

    global previous_scroll_y
    global j

    distance_to_top = browser.execute_script("return window.pageYOffset;")
    if distance_to_top == previous_scroll_y:
        print("NOT SCROLLABLE ANYMORE")
        j = j + 1
    else:
        previous_scroll_y = distance_to_top

    refresh_height = 1354
    if distance_to_top == refresh_height or distance_to_top == refresh_height*2 or distance_to_top == refresh_height*3:
        print("INFO: Refreshing the shoes info...")
        refresh_elaborated_shoes(browser)

    print(f"CHECK: {distance_to_top} | {j}")

    pyautogui.scroll(-125)
    time.sleep(1)

    return


shoes_to_elaborate = get_loaded_shoes()
shoe_removed = []


def refresh_elaborated_shoes(browser: webbrowser):

    global shoes_to_elaborate
    global shoe_removed

    gather_shoes_info(browser.page_source)
    time.sleep(3)

    shoes_to_elaborate = get_loaded_shoes()
    for shoe in shoe_removed:
        shoes_to_elaborate.remove(shoe)

    return


def decrement_shoe_to_elaborate(shoe) -> None:
    global shoes_to_elaborate

    for shoe_to_elaborate in shoes_to_elaborate:
        if shoe_to_elaborate == shoe:
            shoe_to_elaborate["price_euro"] = shoe_to_elaborate["price_euro"] - 1


def wait_decrement_price_gui_loading() -> None:
    time.sleep(0.2)
    euro_icon_point = pyautogui.locateCenterOnScreen("assets/utils/euro_icon.png", confidence=0.6)
    while euro_icon_point is None:
        time.sleep(3)
        euro_icon_point = pyautogui.locateCenterOnScreen("assets/utils/euro_icon.png", confidence=0.6)
    return


def decrement_shoes(browser: webbrowser) -> None:

    global shoe_removed
    global shoes_to_elaborate
    global j

    loaded_shoes_size = len(get_loaded_shoes())

    for shoe in shoes_to_elaborate:

        if len(shoe_removed) == loaded_shoes_size - 6:
            print("TRUE")
            pyautogui.moveTo(INITIAL_SHOE_COORDINATE_X, INITIAL_SHOE_COORDINATE_Y + 5)
            j = j + 1
        else:
            pyautogui.moveTo(INITIAL_SHOE_COORDINATE_X, INITIAL_SHOE_COORDINATE_Y + j*120 - 15*j)

        while not shoe["most_economic"] and can_be_decremented(shoe["name"], shoe["price_euro"]):
            # pyautogui.moveTo(INITIAL_SHOE_COORDINATE_X, INITIAL_SHOE_COORDINATE_Y + j * 120)
            time.sleep(0.2)
            pyautogui.leftClick()

            wait_decrement_price_gui_loading()

            decrement_price(INITIAL_SHOE_COORDINATE_X, INITIAL_SHOE_COORDINATE_Y, shoe["price_euro"])
            save_price()
            time.sleep(1)

            gather_shoes_info(browser.page_source)
            decrement_shoe_to_elaborate(shoe)

            time.sleep(0.2)

            return decrement_shoes(browser)

        shoes_to_elaborate.remove(shoe)
        shoe_removed.append(shoe)

        time.sleep(0.2)

        shoe_stop_loss = get_stop_loss(shoe["name"])
        if shoe["most_economic"] and shoe["price_euro"] == shoe_stop_loss:
            time.sleep(0.2)
            pyautogui.leftClick()
            shoe_backup_price = get_backup_price(shoe["name"])
            insert_backup_price(INITIAL_SHOE_COORDINATE_X, INITIAL_SHOE_COORDINATE_Y, shoe_backup_price)
            save_price()

        scroll_to_next_shoe(browser)
        return decrement_shoes(browser)

    return


def insert_backup_price(initial_shoe_coordinate_x: int, initial_shoe_coordinate_y: int, backup_price: int) -> None:
    # Move on the price form
    price_form_x, price_form_y = initial_shoe_coordinate_x + 35, initial_shoe_coordinate_y + 105
    pyautogui.moveTo(price_form_x, price_form_y)

    pyautogui.leftClick()
    time.sleep(0.2)

    # Remove the old price
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('del')

    # Put the new price
    pyautogui.typewrite(str(backup_price), interval=0.1)
    time.sleep(0.2)


def reset():
    global shoes_to_elaborate
    global previous_scroll_y
    global j

    shoes_to_elaborate = get_loaded_shoes()
    previous_scroll_y = None
    j = None


def main():
    # Open the chrome browser
    browser = webdriver.Chrome()
    browser.get("https://restocks.net/it")
    load_cookies(browser)
    time.sleep(1)

    is_logged = go_to_my_account_section(browser)
    if not is_logged:
        # print("INFO: User is not logged...starting the procedures to login...")

        # Clear the current session
        remove_all_cookies(browser)
        clear_cache(browser)
        browser.refresh()
        time.sleep(1)

        # Accept the initial dialog
        accept_initial_dialog()
        time.sleep(1)

        # Make the login
        make_login()
        time.sleep(1)

        # Store the new cookies
        save_cookies(browser)
        time.sleep(1)

    # Go to my listing section
    go_to_my_listing_section(browser)
    time.sleep(1)

    # Full screen
    pyautogui.press('f11')
    time.sleep(1)

    # Go to resale section
    go_to_resale_section()
    time.sleep(5)

    # Accept cookies if there
    accept_cookies()

    # Gather shoes info
    gather_shoes_info(browser.page_source)
    time.sleep(1)

    # Decrement the shoes
    decrement_shoes(browser)

    print("INFO: Restarting the bot...")
    browser.quit()
    time.sleep(5)
    reset()
    main()


if __name__ == "__main__":
    main()
