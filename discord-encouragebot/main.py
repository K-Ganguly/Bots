import discord
import os
import requests
import json
import random
from replit import db
from keep_alive import keep_alive

token = os.environ['TOKEN']

client = discord.Client()

# creating a list to inspire the user when he posts a depressing message
sad_words = [
    "sad", "depressed", "unhappy", "miserable", "can't take it anymore",
    "suffering"
]

# starter encouraging phrases to encourage the user
starter_encouragements = [
    "c'mon, cheer up buddy", "chill out", "life is too short to have regrets",
    "make the most out of life", "what's there to be sad about"
]

# check if responding is in the database
if not "responding" in db.keys():
    db["responding"] = True


# helper function to return a quote from the api
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]["q"] + " - " + json_data[0]["a"]
    return quote


# function to update encouraging messages by the users
def update_encouragements(encouraging_message):
    if "encouragements" in db.keys():
        encouragements = db["encouragements"]
        encouragements.append(encouraging_message)
        db["encouragements"] = encouragements
    else:
        db["encouragements"] = [encouraging_message]


# function for deleting an encouraging message
def delete_encouragement(index):
    encouragements = db["encouragements"]
    if len(encouragements) > index:
        del encouragements[index]
        db["encouragements"] = encouragements


@client.event
async def on_ready():
    print("We have logged in as {0.user} ".format(client))


# when the bot receives a message
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg.startswith("$inspire"):
        quote = get_quote()
        await message.channel.send(quote)

    if db["responding"]:
        options = starter_encouragements
        if "encouragements" in db.keys():
            options = options + list(db["encouragements"])

        if any(word in msg for word in sad_words):
            await message.channel.send(random.choice(options))

    if msg.startswith("$new"):
        encouraging_message = msg.split("$new ", 1)[1]
        update_encouragements(encouraging_message)
        await message.channel.send("New encouraging message added")

    if msg.startswith("$del"):
        encouragements = []
        if "encouragements" in db.keys():
            index = int(msg.split("$del", 1)[1])
            delete_encouragement(index)
            encouragements = db["encouragements"]
        await message.channel.send(encouragements)

    if msg.startswith("$list"):
        encouragements = []
        if "encouragements" in db.keys():
            encouragements = db["encouragements"]
        await message.channel.send(encouragements)

    if msg.startswith("$responding"):
        value = msg.split("$responding ", 1)[1]
        if value.lower() == "true":
            db["responding"] = True
            await message.channel.send("Responding is on")
        else:
            db["responding"] = False
            await message.channel.send("Responding is off")

keep_alive()

client.run(token)
