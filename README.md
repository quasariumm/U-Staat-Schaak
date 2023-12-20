# U staat schaak
A school project of Jens Boomgaard, Sebastiaan van Straten and Patrick Vreeburg.  
We made a chess app in Python with the use of Kivy and KivyMD. This app was made between August and December of 2023

## Use
### Desktop
Once you load up the app, either with the .exe file or with `py ./src/app.py`, you are greeted with our main menu. In this menu there are the following items:
* The top bar with a button to end the game (flag icon) and one to change the global settings (gear icon), such as themes and piece sets.
* The settings before you start the game.
* The chess board.
* Two clocks, one fixed to the top and one fixed to the bottom of the chess board.
<!-- end of the list -->
When you click 'Start game' and you have selected 'Bot as white', you may experience some lag at the start. Here the bot is calculating its first move.  
Please note that the experience can vary based on the hardware you run it on. We are aware that the bot takes a long while, so please have patience when you play against a bot.
### TI-84 CE Python Edition
Once you load up the app, the chess board will begin drawing. Given the small memory capacity of the calculator, we couldn't pac as much features in as we'd hoped.  
The rules of the game are as follows: your goal is to reach the other side of the board. Once one player has succeeded, they win.  
Once a game if finished, the program will automatically reset the game 3 seconds after one player has won.  
To quit the program, you can press the `On` button on the calculator to terminate the program. You may need to press this button twice. To start the app again, press `trace` twice.

## Installation/build instructions
### Desktop
Make sure you have Python installed on your system. We tested our app with Python 3.11.6.  
When running the following commands, have your terminal in the same directory as where you cloned this repository.  
To install the required packages, run `py -m pip install -r ./requirements.txt`.  
To build the file, make sure you have `pyinstaller` installed and run `pyinstaller ./src/app.py -F -n ChessPWS --add-data ./src/themes.json:. --add-data ./src/app.kv:. --add-data ./data/:.`  
All theme data is stored in `C:\Users\<user>\AppData\Local\Quasar\ChessPWS\themes.json` on Windows, `/home/<user>/.local/share/ChessPWS` on Unix/Linux or `/Users/<user>/Library/Application Support/ChessPWS` on MacOS.

### TI-84 CE Python Edition
Before running the app, you need to take two steps:
* Upload the pieces to the calculator. Do this by dragging and dropping all the files in `./data/img/pieces/GR` into the file menu in the TI Connect CE program. For each image, under `NAME ON CALCULATOR` select `Python image...`. In the popup, give the image the same name as the filename **in uppercase** and set the width and height to the original size.
* Upload the python file to the calculator.
