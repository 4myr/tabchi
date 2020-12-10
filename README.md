# tabchi

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
$ nano config.
``` 
Enter your API KEY & API HASH between quotes

Then, launch bot using:
```sh
$ screen python3 main.py
```

For first time you must login your account and for next times you don't need login.
You can use `CTRL + A + D` for deatach screen.
