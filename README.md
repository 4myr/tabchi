# Tabchi -AMYR -Python
My Telegram: [@SudoYUM](https://t.me/SudoYUM)

An adverstiment telegram bot that developed by [Telethon](https://github.com/LonamiWebs/Telethon) python library.
### Features:
  - Gathering supergroups invite links
  - Joining supergroups
  - Send random adverstiment to groups
  - Send random banner to private chats\
  - Enable/disable Joining groups, Sending Adverstiment, Sending Banners
  - Set maximum groups
  - Set delay for joining groups & sending adverstiment to groups
  - Send adverstiment only once per user
  - Detecting & Block adverstiment and not usable supergroups
  
---
### Commands:
  - !ping (بررسی آنلاین بودن ربات)
  - !stats (دریافت آمار و وضعیت کامل ربات)
  - !set [cron|groups|join|bot] [value] (تنظیم فاصله بین دو تبلیغ | حداکثر گروه ها | فاصله بین دو جوین | ربات)
  - !clear [adv|banner|users] (پاک کردن تمام متن های تبلیغ | متن های بنر در خصوصی | کش کاربران دریافت کننده تبلیغ)
  - !adv (لیست تمام متن های تبلیغات در گروه ها)
  - !adv [text] (ایجاد یک متن تبلیغ جدید)
  -	!adv [on|off] (روشن و خاموش کردن تبلیغ در گروه ها)
  - !banner (لیست تمام متن های تبلیغات در خصوصی)
  - !banner [text] (ایجاد یک متن تبلیغ خصوصی جدید)
  -	!banner [on|off] (روشن و خاموش کردن تبلیغ در خصوصی)
  - !join [on|off] (روشن و خاموش کردن جوین لینک ها)
  - And other commands...

### Installation (Ubuntu 18.04)

First, clone repository in your specific path:
```sh
$ cd ~
$ git clone https://github.com/4myr/tabchi
$ cd tabchi
```

Then, install redis, python3 and telethon library by pip3
```sh
$ sudo apt update
$ sudo apt install -y redis redis-tools python3 python3-pip screen
$ pip3 install --upgrade pip
$ pip3 install telethon psutil redis
```

Now, edit `config.py` file by:
```sh
$ nano config.py
``` 
Enter your Telegram Chat ID, API KEY & API HASH between quotes

Then, launch bot using:
```sh
$ screen python3 main.py
```

For first time you must login your account and for next times you don't need login.
You can use `CTRL + A + D` for deatach screen.
