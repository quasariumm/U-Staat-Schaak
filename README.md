# U staat schaak
A school project of Jens Boomgaard, Sebastiaan van Straten and Patrick Vreeburg.  
We made a chess app in Python with the use of Kivy and KivyMD. This app was made between August and December of 2023

## Use
### Desktop
Once you load up the app, either with the .exe file (you may want to minimize the console window) or with `py ./src/app.py`, you are greeted with our main menu. In this menu there are the following items:
* The top bar with a button to end the game (flag icon) and one to change the global settings (gear icon), such as themes and piece sets.
* The settings before you start the game.
* The chess board.
* Two clocks, one fixed to the top and one fixed to the bottom of the chess board.
<!-- end of the list -->
When you click 'Start game' and you have selected 'Bot as white', you may experience some lag at the start. Here the bot is calculating its first move.  
Please note that the experience can vary based on the hardware you run it on. We are aware that the bot takes a long while, so please have patience when you play against a bot.
### TI-84 Plus CE / TI-83 Premium CE
To run the app, open Cesium from the `apps` menu or run arTIfiCE on your TI and run the program TICHESS. Once you load up the app, the chess board will draw.  
The rules of the game are as follows: your goal is to reach the other side of the board. Once one player has succeeded, they win.  
Once a game if finished, the program will automatically reset the game 3 seconds after one player has won.  
To quit the program, you can press the `clear` button on the calculator to terminate the program.

## Installation/build instructions
### Desktop
Make sure you have Python installed on your system. We tested our app with Python 3.11.6.  
When running the following commands, have your terminal in the same directory as where you cloned this repository.  
To install the required packages, run `py -m pip install -r ./requirements.txt`.  
To build the file, make sure you have `pyinstaller` installed and run `pyinstaller ./src/app.py -F -n ChessPWS --add-data ./src/themes.json:. --add-data ./src/app.kv:. --add-data ./data/:.`  
All theme data is stored in `C:\Users\<user>\AppData\Local\Quasar\ChessPWS\themes.json` on Windows, `/home/<user>/.local/share/ChessPWS` on Unix/Linux or `/Users/<user>/Library/Application Support/ChessPWS` on MacOS.

### TI-84 Plus CE / TI-83 Premium CE
#### Installation
To install the app, you must connect the calculator to your PC and use softawre like TI Connect CE or TILP to transfer the files to your calculator.  
The following steps guide you through the installation:
* Install arTIfiCE from [https://yvantt.github.io/arTIfiCE/](https://yvantt.github.io/arTIfiCE/). This is a 'jailbreak' that allows you to run assembly programs on your TI. You don't need to install this if you have any OS version before 5.5.0
* Optionally, you can install Cesium. This is a shell in which you can run from the `apps` menu, as supposed to via `Cabri Jr.` when you're using only arTIfiCE. You can download it here: [https://github.com/MateoConLechuga/Cesium/releases](https://github.com/MateoConLechuga/Cesium/releases)
* Install the necessary libraries at [https://tiny.cc/clibs](https://tiny.cc/clibs)
* Install the app (`TICHESS.8xp` and `VARGFX.8xv`) form the latest release or build them yourself (see build instructions)

#### Building
Make sure that you have the CE Toolchain installed from [https://github.com/CE-Programming/toolchain](https://github.com/CE-Programming/toolchain). Please also read through the *Getting Started* page on their wiki.  
To actually build it, first set your working directory to `Cpp_Version` by running `cd /path/to/U-Staat-Schaak/src/GR-version/Cpp_Version`. Then simply run `make gfx && make` to build the app. You should now see `VARGFX.8xv` in `./src/gfx` and `TICHESS.8xp` in `./bin`.
