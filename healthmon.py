#!/usr/bin/env python3

from pwn import *
import requests
from slackclient import SlackClient
context.log_level = "info"
slack_token = "XXXXX"

sc = SlackClient(slack_token)



challenges = {
	"circus": [59696,"<@XXX>"],
	"defaced": [59698,"<@XXX>"],
	"Can you login": [57000, "<@XXX>"],
	"badday": [55351, "<@XXXX>"],
	"potato": [58888, "<@XXXX> <@XXX>"],
	"whiskeytangofoxtrot": [51336,"<@XXX>"],
	"elias puzzle": [59542, "<@XXX>"],
	"smart pants": [59213, "<@XXX>"],
	"db_over_9000": [59317, "<!everyone>"],
	"bitflip_like_tony": [59211, "<@XXX>"],
	"pay2win": [59240, "<@XXXX>"],
	"the robber": [59005, "<@XXX>"],
	"magicnumber": [59230, "<@XXX>"],
	"hog_shelter": [59220, "<@XXX>"],
	"batter_up": [59201, "<@XXX>"],
	"dog_shelter": [59200, "<@XXX>"],
	"batterup3": [59203, "<@XXXX>"],
	"batterup2": [59202, "<@XXX>"],
	"everythingformula": [59209, "<@XXX> <@XXX>"],
	"primetime2": [59313, "<@XXX> <@XXX>"],
	"primetime": [59312, "<@XXX> <@XXX>"],
	"planetmusic": [59210, "<@XXX>"],
	"talkingcat": [55556, "<@XXX>"]
}


blocking_state = []

# Every challenge starts in "Offline" state
for c in challenges:
	blocking_state.append(c)

def health_check(port):
	retry_count = 3
	state = False
	while retry_count > 0:
		try:
			r = remote("challenge.ctf.pwn",port,timeout=5, level='critical')
			r.close()
			state = True
			break
		except Exception as e:
			log.critical(e)
			state = False
		retry_count -= 1
		time.sleep(7)
	return state 

# health check website
def health_website():
	try:
		r = requests.get("https://play.ctf.pwn/")
		if r.status_code != 200:
			log.critical("Website returned error code %d" % r.status_code)
			slack_notify("website", "Website returned error code %d. <!everyone>" % r.status_code)
		elif r.status_code == 200:	
			state_online("website")

	except Exception as e:
		slack_notify("website","Website down!!! <!everyone>")
		log.critical("Website down!!!")
	return True

def state_online(chall):
	if chall in blocking_state:
		slack_notify("Null", "Challenge %s now working!" % chall, True)
		blocking_state.remove(chall)

def health_challenges():
	# Healthcheck challenges
	for chall in challenges:
		port = challenges[chall][0]
		author = challenges[chall][1]
		hc = health_check(port)
		if hc:
			state_online(chall)
			log.info("Service %s UP" % chall)	
		else:
			log.critical("Service %s is down. %s" % (chall, author))
			slack_notify(chall, "Service %s is down. %s" % (chall, author))

def slack_notify(chall, message, force=False):
	if not force:
		if chall in blocking_state:
			return 
		blocking_state.append(chall)
	sc.api_call(
	  "chat.postMessage",
	  channel="healthcheck",
	  text=message,
	)


x = 0
while True:
	health_website()
	health_challenges()
	print (blocking_state)
	for i in range(30):
		print(".",end='')
		time.sleep(1)
	print ("")
	x+=1
	if x > 60:
		x = 0
		slack_notify("null", "Heartbeat <3", True)
