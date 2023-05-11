import asyncio
import re
import g
import random
import time
async def react_add(message):
    for i in range(4): #try this thrice in case of lag
        await asyncio.sleep(2) 
        for reaction in message.reactions:
            if not reaction.me:
                await message.add_reaction(reaction.emoji)
                return


async def dkTimerLoop(cooldown, message): #doesnt work sometimes?
    rand_time_add = random.randint(180,2000)
    await asyncio.sleep(cooldown +  rand_time_add) #we dont want it to be dead on. Wait . . . this may conflict with the rolls. But whatever,
    print('dked')
    await message.channel.send('$dk')
    await dkTimerLoop(20 * 3600, message)

async def resetKak(cooldown):
    await asyncio.sleep(cooldown)
    g.abilities['kak'] = True

async def resetDaily(cooldown):
    await asyncio.sleep(cooldown)
    g.abilities['daily'] = True

async def rollTimerLoop(cooldown, rollDelay, message,type):
    await asyncio.sleep(cooldown + rollDelay)
    struct_time =  time.localtime(time.time())
    clock_time = str(struct_time.tm_hour) + ':' + str(struct_time.tm_min)
    print('we are rolling ' + clock_time)
    asyncio.create_task(rollHandler(8, message, type))
    await rollTimerLoop(3600, 0, message,type)

async def roll(numRolls,message,type):
    for i in range(numRolls):
        await asyncio.sleep(3.5)
        if g.abilities['claim']:
            await message.channel.send(type)

async def rollHandler(numRolls, message,type):
    g.canClaim = True #basically, the bot can claim when it is rolling and also 5 seconds after
    await roll(numRolls,message,type)
    if g.abilities['claim'] and g.abilities['daily']: #do $daily
        await asyncio.sleep(3)
        await message.channel.send('$daily')
        g.abilities['daily'] = False
        asyncio.create_task(resetDaily(20 * 3600))
        await asyncio.sleep(3)
        await message.channel.send('$rolls')
        await roll(numRolls,message,type)
    await asyncio.sleep(5) #allow bot to claim 5 seconds after
    g.canClaim = False

async def claimTimerLoop(cooldown):
    await asyncio.sleep(cooldown)
    g.abilities['claim'] = True
    await claimTimerLoop(3 * 3600)

def parseCooldown(cooldown):
    cooldown = cooldown.split(' ')
    if len(cooldown) == 2:
        cooldown[0] = cooldown[0][0:len(cooldown[0]) - 1] #get rid of h
        cooldown[0] = int(cooldown[0]) * 3600
        cooldown[1] = int(cooldown[1]) * 60
        cooldown = cooldown[0] + cooldown[1]

    else:
        cooldown = int(cooldown[0]) * 60

    return cooldown

async def noMessageClaim(message,val):
    if val >= 240 and g.abilities['claim']: #this does not have claim to react message btw
        asyncio.create_task(react_add(message))
        await asyncio.sleep(0.6)
        if len(message.reactions) == 0: #if no reactions have appeared we can attempt this
            await message.add_reaction('🥰')

        g.abilities['claim'] = False
        print('we got a character')

async def startTimers(message, rollDelay, type): #from this content, derive all the timings
    content = message.content
    if g.initialize:
        pass

    else:
        g.initialize = True

        #claims

        claimCheck= re.search('you __can__ claim right now!',content)
        if claimCheck:
            g.abilities['claim'] = True
            cooldown = parseCooldown(re.search('The next claim reset is in \*\*(.+)\*\* min', content).group(1))
            asyncio.create_task(claimTimerLoop(cooldown))
            
        else:
            cooldown = parseCooldown(re.search('you can\'t claim for another \*\*(.+)\*\* min\.', content).group(1)) #we want modularity, so parsecooldown will simply recieve a xh y string
            asyncio.create_task(claimTimerLoop(cooldown))   

        #kakera

        kakCheck = re.search('You __can__ react to kakera right now\!', content)
        if kakCheck:
            g.abilities['kak'] = True
        else:
            cooldown = (100 - int(re.search('Power: \*\*(\d+)\%\*\*', content).group(1))) * 180 #every percent is 3 mins
            asyncio.create_task(resetKak(cooldown))

        #daily

        dailyCheck  = re.search('\$daily is available\!',content)
        if dailyCheck:
            g.abilities['daily'] = True

        else:
            cooldown = parseCooldown(re.search('Next \$daily reset in \*\*(.+)\*\* min', content).group(1))
            asyncio.create_task(resetDaily(cooldown))  

        #dk
        dkCheck = re.search('\$dk is ready\!', content)
        if dkCheck:
            cooldown = 0

        else:
            cooldown = parseCooldown(re.search('Next \$dk reset in \*\*(.+)\*\* min', content).group(1))

        asyncio.create_task(dkTimerLoop(cooldown, message))             

        #rolls

        numRolls = int(re.search('You have \*\*(\d+)\*\* rolls? left', content).group(1))
        cooldown = parseCooldown(re.search('Next rolls reset in \*\*(.+)\*\* min', content).group(1))
        asyncio.create_task(rollTimerLoop(cooldown, rollDelay, message,type))  
        await rollHandler(numRolls,message,type)
