import calendar
import datetime
import holidays
# import pywhatkit
import os
from twilio.rest import Client
from dotenv import load_dotenv
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

load_dotenv()


def getBalance():
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--headless")
    browser = webdriver.Chrome(executable_path=r'/usr/local/bin/chromedriver', options=options)
    browser.get('https://www.mysodexo.co.il/')
    assert 'Cibus' in browser.title
    browser.find_element(By.ID, 'txtUsr').send_keys(os.getenv('USR'))
    browser.find_element(By.ID, 'txtPas').send_keys(os.getenv('PSW'))
    browser.find_element(By.ID, 'txtCmp').send_keys(os.getenv('COMPANY'))
    browser.find_element(By.ID, 'btnLogin').click()
    balance = (
        WebDriverWait(browser, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@class='bdg space']")))).text
    print(balance)
    browser.close()
    browser.quit()
    return re.findall('\d+\.\d+', balance)[0]


def twilio_SMS(message, phoneNumber):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    # To send SMS:
    message = client.messages.create(
        from_='+15618163469',
        body=message,
        to=phoneNumber
    )
    # To send Whatsapp:
    # message = client.messages.create(
    #     from_='whatsapp:+14155238886',
    #     body=message,
    #     to='whatsapp:' + os.getenv('PHONE_NO')
    # )
    print(message.sid)


def check_if_BD(date):
    Israel_holidays = holidays.IL()  # this is a dict
    if date in Israel_holidays:
        if 'eve' not in Israel_holidays.get(date):
            print(f'{date} is a holiday')
            date -= datetime.timedelta(days=1)
            return check_if_BD(date)
    elif date.strftime('%A') in ['Friday', 'Saturday']:
        print(f'{date} is a weekend')
        date -= datetime.timedelta(days=1)
        print('date after weekend-', date)
        return check_if_BD(date)
    return date


def last_valid_day_of_month(year, month):
    lastDayOfMonth = datetime.date(year, month, calendar.monthrange(year, month)[1])
    return check_if_BD(lastDayOfMonth)


def main():
    currentDate = datetime.date.today()
    print(currentDate)
    lastBDinMonth = last_valid_day_of_month(currentDate.year, currentDate.month)
    print(f"last day in current month {currentDate.month}", lastBDinMonth)
    if lastBDinMonth == currentDate:
        twilio_SMS(f'Last day to use cibus! \nYour current balance is ₪{getBalance()}', os.getenv('PHONE_NO'))
        twilio_SMS(f'Last day to use cibus!', os.getenv('MICHAEL_PHONE_NO'))


if __name__ == '__main__':
    main()


