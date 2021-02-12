#!/usr/bin/env python3

import datetime
import smtplib
import sqlite3
import time
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread

import matplotlib.pyplot as plt
import numpy as np
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

# config
url = "https://www.huobi.be/zh-cn/exchange/ada_usdt/"
times_of_one_day = 3
email_smtp_host = "smtp.qq.com"
email_smtp_port = 465
email_user = "example@example.com"
email_pass = "pass"
sender = email_user
receivers = ["example@example.com"]
subject = "Monitor Ada"


def get_price():
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    browser = webdriver.Chrome(options=options)
    WebDriverWait(browser, 10)
    browser.get(url)
    price_container = browser.find_element_by_class_name("price-container")
    price = price_container.find_element_by_class_name("price").text
    browser.close()
    return price


def connect_database():
    conn = sqlite3.connect("price.db")
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS price(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    price FLOAT
    )
    ''')
    return conn


def insert_values(timestamp, price):
    conn = connect_database()
    c = conn.cursor()
    c.execute('''INSERT INTO price(time, price) VALUES(:timestamp , :price)''',
              {"timestamp": timestamp, "price": price})
    conn.commit()
    conn.close()


def query_days_of_draw():
    conn = connect_database()
    c = conn.cursor()
    query = c.execute('''
    SELECT * FROM price where time BETWEEN datetime('now','localtime', '-7 days') AND datetime('now', 'localtime') ORDER BY id;
    ''')
    result = query.fetchall()
    conn.close()
    return result


def draw():
    result = query_days_of_draw()
    ss = np.array(result)
    x = ss[:, 1]
    y = ss[:, 2]
    x = [datetime.datetime.fromisoformat(_).strftime(("%m-%d-%H:%M")) for _ in x]
    y = [float(_) for _ in y]
    plt.figure(dpi=300, figsize=(20, 10))
    plt.plot(x, y)
    for a, b in zip(x, y):
        plt.text(a, b, str(b))
    plt.savefig("current.png", dpi=300)


def send_email():
    draw()
    msg_root = MIMEMultipart("related")
    msg_root["From"] = Header("huobi.be", "utf-8")
    msg_root["To"] = Header(receivers[0], "utf-8")
    msg_root["Subject"] = Header(subject, "utf-8")
    msg_alternative = MIMEMultipart('alternative')
    msg_root.attach(msg_alternative)
    msg = MIMEText('''
    <p><img src="cid:image1"></p>
    ''', "html", "utf-8")
    msg_alternative.attach(msg)
    with open("current.png", "rb") as f:
        msg_image = MIMEImage(f.read())
        msg_image.add_header("Content-ID", "image1")
        msg_root.attach(msg_image)
    try:
        with smtplib.SMTP_SSL(email_smtp_host, email_smtp_port) as server:
            server.login(email_user, email_pass)
            server.sendmail(sender, receivers, msg_root.as_string())
    except smtplib.SMTPException as e:
        print(e)
        print(msg_root)


def start_monitor():
    delta_seconds = (24 * 60 * 60) // times_of_one_day
    while True:
        price = get_price()
        insert_values(datetime.datetime.now(), price)
        time.sleep(delta_seconds)


def start_send_mail():
    delta_seconds = 24 * 60 * 60
    while True:
        send_email()
        time.sleep(delta_seconds)


def start():
    t1 = Thread(target=start_monitor)
    t2 = Thread(target=start_send_mail)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


start()
