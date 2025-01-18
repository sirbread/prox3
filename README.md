# prox3
a very simple discord bot that allows users to send anonymous messages, confessions, and polls.

## features
- 100% anonimity (yes, I can't view anything either)
- send anonymous confessions (/prox3 confession [message])
   - users can submit confessions anonymously.
   - each confession is assigned a number, fetched from the previous confession (in the channel).
   - cooldown of 10 minutes per user.
- send anonymous messages (/prox3 message [message])
   - users can send simple anonymous messages without a cooldown.
   - for talking to someone without revealing who you are :)
- create polls (/prox3 poll [title][options])
   - users can create polls with 2-4 options.
   - includes buttons for voting on each option.
   - cooldown of 30 minutes per user.
   - polls display live updates of votes.

## requirements
- python 3.11 or higher
- requirements.txt
- a discord bot token (stored in a `.env` file as `BOT_TOKEN`)

## set up
- clone thy repo.
- run `pip instal -r requirements.txt`
- create a .env file in the same directory and add your bot token (variable as `BOT_TOKEN`)
- run it :D

## acknowledgements
almost all inspo came from the [prox2](https://github.com/anirudhb/prox2) bot for slack, made by [hackclub](hackclub.com). 
