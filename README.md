# LunaHack

LunaHack is a program designed to streamline Pokemon ROM randomization for generations VI and VII. (X, Y, AS, OR, S, M, US, UM)
It allows you to skip the process of extraction and reconstruction, as well as performing the file operations for you.

## Installation

Extract the `.zip` file to a folder of your choice.

**------------IMPORTANT!------------**

The process utilized by this program to extract, modify, and reconstruct ROMs takes a LOT of space, (Think like, 12 - 15 GB) and while the program does clean up after itself, you MUST make sure you have enough space on the disk. If you do not, the program will behave unexpectedly.

## But why tho?
* Because having to look up a tutorial to do the same thing over and over when you lost your Nuzlocke because the game decided to start you off with a wurmple, a bidoof and a patrat is annoying.

## Usage

1. Place a `.3ds` file in the same folder as `LunaHack.exe`. Do not touch any of the other files in this folder.
2. Run `LunaHack.exe`. LunaHack will ask you which ROM (if there are multiple) you want to randomize. Select one with the arrow keys, hit enter, and LunaHack will begin extracting the ROM. Once done, pk3DS will open and you can begin randomizing the ROM.
3. Once you've done what you need to, simply close pk3DS. LunaHack will then ask you if you're ready to recompress and create the modded `.3ds` file. Select "Yes please!" to recompress.
4. LunaHack will then recompress the ROM, and create a new one named `{original_name}_modded.3ds`. The folders and files created will then be cleaned up.
5. The modified ROM can then be run with a normal 3DS emulator.

## Changelog
* 6.2 - Fixed a bug which caused the program to crash when initializing.
* 6.0 - LunaHack will now hash the ROM before proceeding to extraction. If it matches any ROM which has already been extracted it will skip the entire extraction step. This should allow for massive speedups in special but common situations.
* 5.0 - Fixed an issue which caused directories to not be merged correctly.
* 4.0 - Rewrote literally everything to make it less...awful. Added options to handle multiple ROMs, as well as fancier console output.
* 3.0 - Fixed an issue which caused failures when a ROM had spaces in the name. Also made it so that the cleanup process doesn't remove this README file. (lol oops)
* 2.0 - Made the unstaging process move `modified/ExtractedExeFS/.code.bin` to `original/ExtractedExeFS/code.bin`. This fixes an issue where TMs were not properly randomized.
* 1.0 - Was written.

## Credits
* Thanks to Asia81 for [HackingToolkit3DS](https://github.com/Asia81/HackingToolkit9DS-Deprecated-), which formed the basis for LunaHack. The extraction and reconstruction commands are entirely based on those found in HackingToolkit, and I couldn't have done it without that as a reference.
* Thanks also to kwsch for [pk3DS](https://github.com/kwsch/pk3DS), the tool which allows for randomization to happen.

## License
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)
