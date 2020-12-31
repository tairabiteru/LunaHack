import os
import subprocess
import shutil
import sys
import time
import threading
from PyInquirer import prompt

__AUTHOR__ = "Taira"
__VERSION__ = "4: Electric Boogerdoor"

LOGO = f"""
         .'cdk0XWWWXKOdl:'.
       ,o0NMMMMMXx:..
    .:kNMMMMMMNd'
   ,kWMMMMMMMK:
 .lXMMMMMMMMX:
.oNMMMMMMMMMx.                       .'.
cXMMMMMMMMMWo   .;oxkOkdc'           .oc
0MMMMMMMMMMWd. ;0WMMMMMMMXd.         .O0
NMMMMMMMMMMMK,,0MMMMMMMMMMWo         cXN
MMMMMMMMMMMMWOxNMMMMMMMMMMMx.       ;0MM
WMMMMMMMMMMMMWWWMMMMMMMMMMK;      .lXMMW
XMMMMMMMMMMMMMMMMMMMMMWN0o'     'l0WMMMX
xWMMMMNKkxkOXWMMMMMMWN0xc,',:cdONMMMMMWd
'OWMNx;.    .lKMMMMMMMMWWNWWWMMMMMMMMMO'
 ,ONd.        ,0MMMMMMMMMMMMMMMMMMMMWO,
  .o,         .xMMMMMMMMMMMMMMMMMMMNx.
              ;KMMMMMMMMMMMMMMMMMWO:
           .'oKMMMMMMMMMMMMMMMWXk:.
         .;dKWMMMMMMMMMMMMWN0dc.
           .;okKNWMMMMWNKko;.

    LunaHack {__VERSION__}
"""


def log(msg, type="NORM"):
    """Simple log formatting."""
    print(f"[{type}] {msg}")

def subproc_format(rom, command):
    """Format commands with ROM names."""
    command = command.split(" ")
    out = []
    for arg in command:
        arg = arg.format(rom=rom)
        out.append(arg)
    return out

def copydir(src, dst):
    """Implement full directory copying."""
    if not os.path.exists(dst):
        os.makedirs(dst)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)


class Spinner:
    """Implement spinny thing."""
    busy = False
    delay = 0.05

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\':
                yield cursor

    def __init__(self, msg="", delay=None):
        self.msg = msg
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay):
            self.delay = delay

    def spinner_task(self):
        while self.busy:
            next_msg = f"[{next(self.spinner_generator)}] {self.msg}"
            sys.stdout.write(next_msg)
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b' * len(next_msg))
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False
        print("\n")


class Session:
    """Implement extraction/modification/compression session."""
    def __init__(self):
        self.original = "original/"
        self.modded = "modded/"
        self.bin = "3dstool.exe"

        self.partitions = {
            "0": "",
            "1": "Manual",
            "2": "DownloadPlay",
            "6": "N3DSUpdate",
            "7": "O3DSUpdate"
        }

        self.roms = []
        for file in os.listdir(os.getcwd()):
            if file.lower().endswith(".3ds") and not file.lower().endswith("_modded.3ds"):
                self.roms.append(file)

    def extract(self):
        log("Beginning extraction...", type="-")
        path = self.original
        os.makedirs(path)

        stage1_cmds = []

        cmd = "-xtf 3ds {rom} --header " + f"{path}HeaderNCCH.bin "
        for part in self.partitions:
            cmd += f"-{part} {path}DecryptedPartition{part}.bin "
        stage1_cmds.append(cmd[:-1])

        for part, name in self.partitions.items():
            if part == "0":
                cmd = f"-xtf cxi {path}DecryptedPartition{part}.bin --header {path}HeaderNCCH{part}.bin --exh {path}DecryptedExHeader.bin --exefs {path}DecryptedExeFS.bin --romfs {path}DecryptedRomFS.bin --logo {path}LogoLZ.bin --plain {path}PlainRGN.bin"
            else:
                cmd = f"-xtf cfa {path}DecryptedPartition{part}.bin --header {path}HeaderNCCH{part}.bin --romfs {path}Decrypted{name}.bin"
            stage1_cmds.append(cmd)

        stage2_cmds = [
            f"-xtf romfs {path}DecryptedRomFS.bin --romfs-dir {path}ExtractedRomFS",
            f"-xtf romfs {path}DecryptedManual.bin --romfs-dir {path}ExtractedManual",
            f"-xtf romfs {path}DecryptedDownloadPlay.bin --romfs-dir {path}ExtractedDownloadPlay",
            f"-xtf romfs {path}DecryptedN3DSUpdate.bin --romfs-dir {path}ExtractedN3DSUpdate",
            f"-xtf romfs {path}DecryptedO3DSUpdate.bin --romfs-dir {path}ExtractedO3DSUpdate",
            f"-xtf exefs {path}DecryptedExeFS.bin --exefs-dir {path}ExtractedExeFS --header {path}HeaderExeFS.bin"
        ]

        stage3_cmds = [
            f"-x -t banner -f {path}banner.bin --banner-dir {path}ExtractedBanner\\"
        ]

        with Spinner(msg="Executing stage I extraction commands..."):
            for cmd in stage1_cmds:
                cmd = subproc_format(self.rom, f"{self.bin} {cmd}")
                out = subprocess.run(cmd, stdout=subprocess.PIPE)

        for part in self.partitions:
            try:
                os.remove(f"{path}DecryptedPartition{part}.bin")
            except FileNotFoundError:
                pass
        log("Stage I is complete.", type="S")

        with Spinner(msg="Executing stage II extraction commands..."):
            for cmd in stage2_cmds:
                cmd = subproc_format(self.rom, f"{self.bin} {cmd}")
                subprocess.run(cmd, stdout=subprocess.PIPE)

        os.rename(f"{path}ExtractedExeFS/banner.bnr", f"{path}ExtractedExeFS/banner.bin")
        os.rename(f"{path}ExtractedExeFS/icon.icn", f"{path}ExtractedExeFS/icon.bin")
        shutil.copyfile(f"{path}ExtractedExeFS/banner.bin", f"{path}banner.bin")
        log("Stage II is complete.", type="S")

        with Spinner(msg="Executing stage III extraction commands..."):
            for cmd in stage3_cmds:
                cmd = subproc_format(self.rom, f"{self.bin} {cmd}")
                subprocess.run(cmd, stdout=subprocess.PIPE)

        os.remove(f"{path}banner.bin")
        os.rename(f"{path}ExtractedBanner/banner0.bcmdl", f"{path}ExtractedBanner/banner.cgfx")
        log("Stage III is complete.", type="S")
        log("Extraction has completed successfully.", type="S")

    def rebuild(self):
        path = self.original
        log("Beginning reconstruction process.", "-")
        with Spinner(msg="Executing stage I reconstruction commands..."):
            cmd = f"{self.bin} -ctf romfs {path}CustomRomFS.bin --romfs-dir {path}ExtractedRomFS".split(" ")
            subprocess.run(cmd, stdout=subprocess.PIPE)

            os.rename(f"{path}ExtractedExeFS/banner.bin", f"{path}ExtractedExeFS/banner.bnr")
            os.rename(f"{path}ExtractedExeFS/icon.bin", f"{path}ExtractedExeFS/icon.icn")

            cmd = f"{self.bin} -ctf exefs {path}CustomExeFS.bin --exefs-dir {path}ExtractedExeFS --header {path}HeaderExeFS.bin".split(" ")
            subprocess.run(cmd, stdout=subprocess.PIPE)

            os.rename(f"{path}ExtractedExeFS/banner.bnr", f"{path}ExtractedExeFS/banner.bin")
            os.rename(f"{path}ExtractedExeFS/icon.icn", f"{path}ExtractedExeFS/icon.bin")
        log("Stage I is complete.", "S")

        stage2_cmds = []
        for part, name in self.partitions.items():
            if part == "0":
                continue
            cmd = f"-ctf romfs {path}Custom{name}.bin --romfs-dir {path}Extracted{name}"
            stage2_cmds.append(cmd)

        for part, name in self.partitions.items():
            if part == "0":
                cmd = f"-ctf cxi {path}CustomPartition{part}.bin --header {path}HeaderNCCH{part}.bin --exh {path}DecryptedExHeader.bin --exefs {path}CustomExeFS.bin --romfs {path}CustomRomFS.bin --logo {path}LogoLZ.bin --plain {path}PlainRGN.bin"
            else:
                cmd = f"-ctf cfa {path}CustomPartition{part}.bin --header {path}HeaderNCCH{part}.bin --romfs {path}Custom{name}.bin"
            stage2_cmds.append(cmd)

        with Spinner(msg="Executing stage II reconstruction commands..."):
            for cmd in stage2_cmds:
                cmd = subproc_format(self.rom, f"{self.bin} {cmd}")
                out = subprocess.run(cmd, stdout=subprocess.PIPE)

        for file in os.listdir(path):
            if file.startswith("Custom") and file.endswith(".bin"):
                if os.path.getsize(os.path.join(path, file)) <= 20000:
                    os.remove(os.path.join(path, file))
        log("Stage II is complete.", "S")

        with Spinner(msg="Executing stage III reconstruction commands, and building final ROM..."):
            cmd = "-ctf 3ds {rom} --header " + f"{path}HeaderNCCH.bin "
            for part in self.partitions:
                cmd += f"-{part} {path}CustomPartition{part}.bin "
            cmd = subproc_format(self.opt_rom, f"{self.bin} {cmd}")
            out = subprocess.run(cmd[:-1], stdout=subprocess.PIPE)
        log("Stage III is complete. Final ROM has been built.", "S")
        log("Reconstruction process has completed.", "S")

    def obtain_rom(self):
        if len(self.roms) == 0:
            prompt([{'type': 'list', 'name': 'darn', 'message': 'No ROMs were found. Please move one into the same folder as LunaHack. The program will now exit.', 'choices': ['Shoot.']}])
            sys.exit(0)
        elif len(self.roms) == 1:
            self.rom = self.roms[0]
        else:
            p = [
                {
                    'type': 'list',
                    'name': 'rom',
                    'message': "Please select from the following ROMs:",
                    'choices': self.roms
                }
            ]
            self.rom = prompt(p)['rom']
        self.opt_rom = self.rom[:-4] + "_modded.3ds"

    def cleanup(self, remove_rom=False):
        if os.path.exists(self.original):
            shutil.rmtree(self.original)
        if os.path.exists(self.modded):
            shutil.rmtree(self.modded)
        if os.path.exists(self.opt_rom) and remove_rom:
            os.remove(self.opt_rom)

    def prompt_recompression(self):
        p = [
            {
                'type': 'list',
                'name': 'choice',
                'message': 'PK3DS has been closed. Are you ready to rebuild the modded ROM?',
                'choices': [
                    'Yes please!',
                    'No, bring me back to PK3DS.',
                    'No, I want to quit.'
                ]
            }
        ]
        choice = prompt(p)['choice']
        if choice == "Yes please!":
            return
        elif choice == "No, bring me back to PK3DS.":
            subprocess.run(["pk3DS.exe", self.modded])
            return self.prompt_recompression()
        else:
            sys.exit(0)

    def process(self):
        self.obtain_rom()
        os.system('CLS')
        self.cleanup(remove_rom=True)
        self.extract()

        with Spinner(msg="Creating modding directory. This may take a while..."):
            copydir(self.original, self.modded)
        log("Modding directory created.", type="S")

        with Spinner(msg="Waiting for PK3DS to be closed..."):
            subprocess.run(["pk3DS.exe", self.modded])

        self.prompt_recompression()
        self.rebuild()

        with Spinner(msg="Cleaning up..."):
            self.cleanup()

        log("Grand success!", type="S")
        log(f"Your modded ROM has been created, and is named '{self.opt_rom}'.", type="S")
        input("Press enter to exit...")
        log("Bye now!", type="S")


if __name__ == "__main__":
    print(LOGO)
    print("\nPress enter to continue...")
    input()

    session = Session()
    session.process()
