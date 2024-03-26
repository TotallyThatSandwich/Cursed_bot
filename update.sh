#!/bin/bash

clear

echo "What would you like to do?"

TYPE=$(gum choose "update cogs" "update main.py" "restart bot")

if [ "$TYPE" == "update cogs" ]; then
    
    clear
    echo "running this will remove existing cog files"
    gum confirm && sudo rm -r cogs/ || exit

    clear
    echo -ne '#####                                                (10%)\r'
    sleep 0.5
    echo -ne '#############                                        (33%)\r'
    sleep 0.5
    echo -ne '#########################                            (50%)\r'
    sleep 0.5
    echo -ne '################################                     (66%)\r'
    sleep 0.5
    echo -ne '##################################################   (100%)\r'
    echo -ne '\n'

    sleep 1.5

    clear

    git fetch origin develop
    git checkout origin/develop -- cogs/

    echo ""
    echo "Updated cogs"
    echo ""
    echo "please restart bot or run '/reload_all' as an admin on discord to reload the bot cogs"

elif [ "$TYPE" == "update main.py" ]; then

    clear
    echo "running this will remove existing main.py file"
    gum confirm && sudo rm -r main.py || exit

    clear
    echo -ne '#####                                                (10%)\r'
    sleep 0.5
    echo -ne '#############                                        (33%)\r'
    sleep 0.5
    echo -ne '#########################                            (50%)\r'
    sleep 0.5
    echo -ne '################################                     (66%)\r'
    sleep 0.5
    echo -ne '##################################################   (100%)\r'
    echo -ne '\n'

    sleep 1.5

    clear

    git fetch origin develop
    git checkout origin/develop -- main.py
    echo ""
    echo "Updated main.py"
    echo ""
    echo "please restart bot for changes to take effect"

elif [ "$TYPE" == "restart bot" ]; then
    gum confirm && clear || exit 
    echo "Restarting bot..."
    sleep 3
    PID=$(ps ax | grep /home/docker/Cursed_bot/main.py | head -n 1 | awk '{print $1}')
    kill $PID
    nohup python3 /home/docker/Cursed_bot/main.py && clear

    echo "bot restarted"

    exit

fi
sleep 3

echo "would you like to restart the bot?"

RESTART=$(gum choose "Yes" "No")

if [ "$RESTART" == "Yes" ]; then
    gum confirm && clear || exit 
    echo "Restarting bot..."
    sleep 3
    PID=$(ps ax | grep /home/docker/Cursed_bot/main.py | head -n 1 | awk '{print $1}')
    kill $PID
    nohup python3 /home/docker/Cursed_bot/main.py && clear

    echo "bot restarted"
fi
