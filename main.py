#A discord bot requiring discord.py-self package. It will roll, claim, claim kak, and use daily. The kakera claiming feature on this bot is very limited, and daily can be improved
#bot should be reset every now and then as the timers will become out of sync after a while. 
#we need to implement a feature later on that will be smarter about rolls perhaps send $ha then check for message or spam until stop.
import discord
from functions import *
client = discord.Client(self_bot = True)
claimAll = False 
is_ready = False
targ_serv_id = input('enter your server id\n')
targ_channel_id = input('enter your channel id\n')
@client.event
async def on_ready():
     #we cant have inputs in the ready statement in case the bot disconnects
    global targ_channel
    global is_ready
    targ_channel = client.get_channel(targ_channel_id) 
    print('online, name: {}'.format(client.user.name))
    is_ready = True
    #set the timer now
    while not g.initialize: #continue until we get the tu off
        await targ_channel.send('$tu')
        await asyncio.sleep(5)

@client.event
async def on_message(message): 
    if is_ready:
        if message.author.id == 432610292342587392 and message.guild.id == targ_serv_id: #if it appears to be a roll from mudae on proper server
            if message.content.startswith('**{}**, you __can__ claim right now!'.format(client.user.name)) or message.content.startswith('**{}**, you can\'t claim for another'.format(client.user.name)):
                await startTimers(message, rollDelay, type)

            elif (message.channel.id == targ_channel_id and g.canClaim) or claimAll: #we only want to do anything if can claim is true and correct lobby
                if message.embeds:
                    emb = message.embeds[0]
                    desc = emb.description.split('\n')
                    if desc[len(desc)-1] == 'React with any emoji to claim!' and g.abilities['claim']:# we know this is a roll
                        kakeraString = desc[len(desc)-2]
                        val =int(re.search('\d+', kakeraString).group())
                        if val >= 240 :# we want to claim this with any emoji
                            await asyncio.sleep(0.6)
                            await message.add_reaction('🥰')
                            print('we got a character')
                            g.abilities['claim'] = False
                            
                    else: #might not even be a roll, we can check using regex
                        kakeraString = desc[len(desc)-1]
                        val = re.search('^\*\*(\d+)',kakeraString)
                        if val != None: #the last thing is kakera in the correct form as well so we know this is a roll
                            if emb.footer.text != discord.Embed.Empty: 
                                if 'Belongs to' in emb.footer.text: #is already claimed roll, claim the kakera. We should eventually check to see if the kakera is of good enough quality too, but later.
                                    if g.abilities['kak']:
                                        asyncio.create_task(react_add(message))
                                        print('kakeraaa')
                                        g.abilities['kak'] = False
                                        await asyncio.sleep(3600 * 5)
                                        g.abilities['kak'] = True

                                else: #irrelevant footer
                                    await noMessageClaim(message,int(val.group(1)))

                            else: #could be either heart react or wish/perstogglereact 
                                await noMessageClaim(message,int(val.group(1)))

type = input('what type of roll you want? ')
rollDelay = int(input('type your roll delay here (should be value between 100 and 3500 but you should try to space them as well as possible '))
client.run(input('type token here '))

