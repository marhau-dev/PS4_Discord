
from ftplib import FTP
import psutil
import re
import requests
import json
from pypresence import Presence 
from pypresence.exceptions import DiscordNotFound 
from pypresence.exceptions import PipeClosed  
import time 
import hmac  
from hashlib import sha1 
import os
def messege_from_system(msg:str,time:int):
    from plyer import notification

    notification.notify(
        title='PS4 Discord',
        message=f'{msg}',# masseges
        app_name='PS4 Discord', #app name
        timeout=time  # Duration in seconds
        
    )

#function to check settings.json if it not exist create it
def setting_check(info: str):
    file_path = 'settings.json'

    # Default values if the file does not exist
    default_settings = {
        'ps4ip': '192.168.0.0'
    }
    #reading a settings from settings.json
    def read_from_file(path):
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


           




# Loading settings and global veriable 
setting_check("ps4ip")
#application id 
aplication_id = '858345055966461973'
ips = setting_check("ps4ip")
#discord status refresh default is 120s = 2m
refreshtime = 120
tmdb_key = bytearray.fromhex('F5DE66D2680E255B2DF79E74F890EBF349262F618BCAE2A9ACCDEE5156CE8DF2CDF2D48C71173CDC2594465B87405D197CF1AED3B7E9671EEB56CA6753C2E6B0')
game_id_dict = {
    "PS4": "CUSA",
}
presence = Presence(aplication_id)

# function to check discord if discord works it return true else false
def discord_stat():

    for process in psutil.process_iter(attrs=['name']):
        if process.info['name'] == 'Discord.exe':
            return True
    return False
def get_game_inf(f):    # Uses Sony TMDB api to resolve a titleID to a name and image

        title_id = get_game_id()
        title_id = title_id+"_00"
        title_id_hash = hmac.new(tmdb_key, bytes(title_id, "utf-8"), sha1)    # get a hash of tmdb key using sha1
        title_id_hash = title_id_hash.hexdigest().upper()
        url = f"http://tmdb.np.dl.playstation.net/tmdb2/{title_id}_{title_id_hash}/{title_id}.json"
        urlrequest = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}) # get info from url
        if urlrequest.ok:     # do webpage exists 
            j = json.loads(urlrequest.text)   # convert from string to dict
            game_name = j["names"][0]["name"]
            game_icon = j["icons"][0]["icon"]
        else:   # if webpage do not exist
            print(f"get_game_inf():     No entry found in TMDB for {title_id}")
            game_name = title_id
            game_icon = title_id.lower()
        if f == "name":
            return game_name 
        elif f == "icon":
            return game_icon
# check if pc have wifi if pc connected to wifi it return true else false
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
     test_ps4(ips,ips)

def get_game_id():     # this function get a id of game using ftp
        ftp = FTP()
        ftp.set_pasv(False)     
        data = []
        title_id, game_type, = None, None     # reset every run
        
        ftp.connect(ips, 2121)  # uses port 2121 for ftp
        ftp.login("", "")   # no login needed
        ftp.cwd("/mnt/sandbox")     # change dir
        ftp.dir(data.append)    # get dir listing add each item to list
        ftp.quit()  # close ftp connection
        
        for item in data:   # loop through each folder found from dir
            if (res := re.search("(?!NPXS)([a-zA-Z0-9]{4}[0-9]{5})", item)) is not None:
                    title_id = res.group(0)     # remove junk
            if title_id is None:    # user is on homescreen if no game found
                title_id = "main_menu"     # discord art asset naming conventions (no spaces, no capitals)
                
            else:   # user is in some program (PS4 game, homebrew, retro game, etc)
                if title_id[:4] in game_id_dict.get("PS4"):    # first 4 characters from title_id removes numbers
                    game_type = "PS4"
                else:
                    game_type = "Homebrew"
        
        return title_id
#test did your ps4 device is online and if ps4 online return true else false
def test_ps4(self, ip):
        if test_wifi() == False:
             import time 
             print("pls connect pc to wifi")
             time.sleep(600)
             
             repeat_search(5)
        else:
             
            ftp = FTP()
            ftp.set_pasv(False)    
            try:
                ftp.connect(ip, 2121)  # device uses port 2121
                ftp.login("", "")  # device has no creds by default
                ftp.cwd("/mnt/sandbox/NPXS20001_000")  # device has path as specified (NPXS20001: SCE_LNC_APP_TYPE_SHELL_UI)
                ftp.quit()  # close ftp connection
            except Exception as e:
                repeat_search(120)
                return False  # some error was encountered, ftp server required not exist on given IP
            else:

                return True  # no errors were encountered, an ftp server with no login, and "/mnt/sandbox" exists
#messege if discord is on and ps4 is on 
if test_ps4(ips,ips) == True and discord_stat() == True:
    messege_from_system("PS4 is online and connected to Discord",10)  
while True:
    #if ps4 and discord online we stat getting a name and icon of game
    if test_ps4(ips,ips) == True and discord_stat() == True:
            


            
            try:
                
                try:
                 presence.close()
                 presence.connect()
                except:
                 presence.connect()
                # Set the status
                presence.update(
                    state=f'{get_game_inf("name")}',  # game name
                    large_image=f'{get_game_inf("icon")}',  # game icon
                    large_text=f'{get_game_inf("name")}',  # alt of icon 
                )
                print(f'chenged {get_game_inf("name")}')
                
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

