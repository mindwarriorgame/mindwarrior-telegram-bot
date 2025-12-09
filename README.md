# mindwarrior-telegram-bot


Requires python 3.12.

```
python3.12 -m venv venv

source venv/bin/activate

pip install -r requirements.example.txt
```

# TODOs

Just a little TODO list to myself; don't want to create yet-another-file for them, sorry. 

## Refactor rendering out of game_manager

So it can be reused in e.g. standalone app

## Move "c0" logic from cat_badge to badge_manager

It has too special logic; no need to have it in 2 places

## Render "snowflake" icon on review screen + counter when cool-down period is over

Too annoying to review only to figure out that I'm in a cool-down period

## Research how long window.Telegram.app.initDataUnsafe.query_id is valid

And add a check to show a better error message. OR just handle the "expired" error message correctly

## Update the last message with a cooldown counter

## Standalone app

Figure out how to package the code as a standalone app that doesn't need network (close-to-0 permissons).

 - Probably focus on Android firstly.