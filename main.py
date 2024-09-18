
from ftplib import FTP
import psutil
import re
import requests
import json
from pypresence import Presence  # sends presence data to Discord client
from pypresence.exceptions import DiscordNotFound  # handles when Discord cannot be found as process
from pypresence.exceptions import PipeClosed  
import time
import hmac     # generate link for tmdb
from hashlib import sha1    # generate link for tmdb
import os
def messege_from_system(msg:str,time:int):
    from plyer import notification

    notification.notify(
        title='PS4 Discord',
        message=f'{msg}',
        app_name='PS4 Discord',  # Optional
        timeout=time  # Duration in seconds
        
    )
def setting_check(info: str):
    file_path = 'settings.json'

    # Default values if the file does not exist
    default_settings = {
        'ps4ip': '192.168.0.0'
    }

    def read_from_file(path):
        """Read values from a JSON file, creating it with default values if it doesn't exist."""
        if not os.path.isfile(path):
            # File does not exist, create it with default settings
            with open(path, 'w') as file:
                messege_from_system("Change Default PS4 IP in settings.json and restart app", 25)
                json.dump(default_settings, file)
            # Return default value if file was created
            return default_settings.get(info, str)

        # File exists, read the data from it
        with open(path, 'r') as file:
            data = json.load(file)
            return data.get(info, default_settings.get(info))  # Directly return the value

    # Get the value based on the info parameter
    value = read_from_file(file_path)
    return value


           
client_id = '858345055966461973'


presence = Presence(client_id)
# Example usage
setting_check("ps4ip")
ips = setting_check("ps4ip")
refreshtime = 120
tmdb_key = bytearray.fromhex('F5DE66D2680E255B2DF79E74F890EBF349262F618BCAE2A9ACCDEE5156CE8DF2CDF2D48C71173CDC2594465B87405D197CF1AED3B7E9671EEB56CA6753C2E6B0')
title_id_dict = {
    "PS4": "CUSA",
}
def discord_stat():

    for process in psutil.process_iter(attrs=['name']):
        if process.info['name'] == 'Discord.exe':
            return True
    return False
def get_ps4_game_info(f):    # Uses Sony's TMDB api to resolve a titleID to a name and image
        # note that some titleIDs do NOT have an entry in the TMDB

        title_id = get_title_id()
        title_id = title_id+"_00"
        title_id_hash = hmac.new(tmdb_key, bytes(title_id, "utf-8"), sha1)    # get hash of tmdb key using sha1
        title_id_hash = title_id_hash.hexdigest().upper()
        url = f"http://tmdb.np.dl.playstation.net/tmdb2/{title_id}_{title_id_hash}/{title_id}.json"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})     # get data from url
        if response.ok:     # webpage exists
            j = json.loads(response.text)   # convert from string to dict
            game_name = j["names"][0]["name"]
            game_image = j["icons"][0]["icon"]
        else:   # webpage does not exist
            print(f"get_ps4_game_info():     No entry found in TMDB for {title_id}")
            game_name = title_id
            game_image = title_id.lower()
        if f == "name":
            return game_name 
        elif f == "icon":
            return game_image
def test_wifi():
    import socket
    try:
        b = socket.create_connection(["8.8.8.8",53])
        return True
    except:
         return False
def repeat_search(sec:int):
     import time
     if sec is float:
          sec = float(sec)
     time.sleep(sec)
     print("nah no ps4 try later")
     test_for_ps4(ips,ips)
def get_title_id():     # function always called
        ftp = FTP()
        ftp.set_pasv(False)     # Github issue #4, need Active mode to work with Pi-Pwn
        data = []
        title_id, game_type, = None, None     # reset every run
        
        ftp.connect(ips, 2121)  # uses port 2121 for ftp
        ftp.login("", "")   # no login credentials
        ftp.cwd("/mnt/sandbox")     # change directory
        ftp.dir(data.append)    # get directory listing, add each item to list
        ftp.quit()  # close FTP connection
        
        for item in data:   # loop through each folder found from directory
            if (res := re.search("(?!NPXS)([a-zA-Z0-9]{4}[0-9]{5})", item)) is not None:    # Assignment expression,
                    # do not match NPXS, do match 4 characters followed by 5 numbers (Homebrew can use titleIDs with prefix other than "CUSA")
                    title_id = res.group(0)     # remove regex junk
            if title_id is None:    # user is on homescreen
                title_id = "main_menu"     # discord art asset naming conventions (no spaces, no capitals)
                game_image = title_id
            else:   # user is in some program (PS4 game, homebrew, retro game, etc)
                if title_id[:4] in title_id_dict.get("PS4"):    # first 4 characters from title_id removes numbers
                    game_type = "PS4"
                else:
                    game_type = "Homebrew"
        
        return title_id
def test_for_ps4(self, ip):
        if test_wifi() == False:
             import time 
             print("pls connect pc to wifi")
             time.sleep(600)
             
             repeat_search(5)
        else:
             
            ftp = FTP()
            ftp.set_pasv(False)     # Github issue #4, need Active mode to work with Pi-Pwn
            try:
                ftp.connect(ip, 2121)  # device uses port 2121
                ftp.login("", "")  # device has no creds by default
                ftp.cwd("/mnt/sandbox/NPXS20001_000")  # device has path as specified (NPXS20001: SCE_LNC_APP_TYPE_SHELL_UI)
                ftp.quit()  # close FTP connection
            except Exception as e:
                repeat_search(120)
                return False  # some error was encountered, FTP server required does not exist on given IP
            else:

                return True  # no errors were encountered, an FTP server with no login creds, and "/mnt/sandbox" exists
if test_for_ps4(ips,ips) == True and discord_stat() == True:
    messege_from_system("PS4 is online and connected to Discord",10)  
while True:
    
    if test_for_ps4(ips,ips) == True and discord_stat() == True:
            


            
            try:
                
                try:
                 presence.close()
                 presence.connect()
                except:
                 presence.connect()
                # Set the status
                presence.update(
                    state=f'{get_ps4_game_info("name")}',  # The text to show in the "state" field
                    large_image=f'{get_ps4_game_info("icon")}',  # The key of the large image you want to display (optional)
                    large_text=f'{get_ps4_game_info("name")}',  # The tooltip text for the large image (optional)
                    small_image='small_image_key',  # The key of the small image you want to display (optional)
                    small_text='Small Image Text'   # The tooltip text for the small image (optional)
                )
                print(f'chenged {get_ps4_game_info("name")}')
                
                time.sleep(refreshtime)  # Update every 120 seconds

            except DiscordNotFound:
                print("Discord client not found. Make sure Discord is running.")
            except PipeClosed:
                print("Connection to Discord was closed.")

    else:
            if discord_stat == False:
                 time.sleep(300)
            else:
                 time.sleep(280)

