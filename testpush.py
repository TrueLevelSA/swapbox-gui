
import crossbarconnect

from random import randint

from time import sleep

client = crossbarconnect.Client("http://127.0.0.1:8080/notify")


while True:
    sleep(1)
    client.publish("CHFSELL", str(randint(200,300)))
