#This dashboard was designed to run on a Raspberry Pi Zero 2 W with a Waveshare 2.13" v4 E-Ink display
#If you are utilizing other hardware you will need to adjsut the code to match your hardware

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V4
import os, re, socket, subprocess, sys, time, datetime, logging

#global variables and directories
libdir = 'lib' #change to your lib directory
picdir = 'pic' #change to your pic directory
epddir = 'waveshare_epd' #May be able to put 'lib/waveshare_epd' and move file #change to your waveshare_epd directory
sys.path.insert(0, libdir)
sys.path.insert(0, picdir)
sys.path.insert(0, epddir)

epd = epd2in13_V4.EPD()

#set fonts
font14 = ImageFont.truetype(os.path.join(libdir, 'Font.ttc'), 14)
font15 = ImageFont.truetype(os.path.join(libdir, 'Font.ttc'), 15)
font18 = ImageFont.truetype(os.path.join(libdir, 'Font.ttc'), 18)
font20 = ImageFont.truetype(os.path.join(libdir, 'Font.ttc'), 20)
font24 = ImageFont.truetype(os.path.join(libdir, 'Font.ttc'), 24)

#set image and draw modules
image = Image.new('1', (epd.height, epd.width), 255) #255: clear the frame
draw = ImageDraw.Draw(image)

#start debug log
logging.basicConfig(level=logging.DEBUG)

#Initialize E-Ink Display
def eink_initialize():
    epd.init()
    epd.Clear()
    time.sleep(1)
    return

#Shutdown E-Ink Display
def eink_shutdown():
    epd.init()
    epd.Clear()
    epd.sleep(1)
    return

#Get device hostname
def get_hostname():
    try:
        hostname = socket.gethostname().lower()
        return hostname
    except:
        return "Hostname_Error"

#Get device temperature
def get_temp():
    try:
        temp = subprocess.check_output("usr/bin/vcgencmd easure_temp", shell=True).decode("utf-8")
        tempstring = re.search(r"temp\=(\d+\.\d+)'C", temp)
        return tempstring
    except:
        return "Temp_Error"
    
#Get IP address
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip_address = s.getsockname()[0]
        s.close()
        return local_ip_address
    except:
        return "IP_Error"
    
#Get memory usage
def get_mem():
    try:
        mem = subprocess.check_output("free -m", shell=True).decode("utf-8")
        memstring = re.search(r"Mem:\s+(\d+)\s+(\d+)\s+(\d+)", mem)
    except:
        return "Mem_Error"
    
    used = int(memstring.group(2))
    total = int(memstring.group(1))
    used_percent = int(used/total*100)
    return f"{used_percent}%"

#Get uptime
def get_uptime():
    try:
        uptimestr = subprocess.check_output("cat /proc/uptime", shell=True).decode("utf-8")
    except:
        return "Uptime_Error"
    
    match = re.search(r"(\d+\.\d+)\s+(\d+\.\d+)", uptimestr)
    total_seconds = float(match.group(1))
    idle_cores = float(match.group(2))
    up_days = float(total_seconds / 86400)
    active_percent = float((1 - idle_cores / (4 * total_seconds)) * 100)

    return f"{up_days:.2f}d, active {active_percent:.2f}%"

#Get wifi signal strength
def get_wifi_strength():
    try:
        wifistr = subprocess.check_output("usr/sbin/iwconfig wlan0", shell=True).decode("utf-8")
    except:
        return "Wifi_Str_Error"
    
    match = re.search(r"Link Quality=(\d+)/(\d+).+Signal level=(-\d+) dBm", wifistr)
    return f"{match.group(1)}/{match.group(2)} {match.group(3)} dBm"

#Get disk usage
def get_disk():
    try:
        diskstr = subprocess.check_output("df -k", shell=True).decode("utf-8")
    except:
        return "Disk_Error"
    
    lines = diskstr.split("\n")
    # Find line ending in "/\s*":
    [line] = [line for line in lines if re.search(r"/\s*$", line)]

    (dev, total, used, avail, percent, mount, *_) = line.split()
    return f"{int(used)//1000000}G/{int(total)//1000000}G {percent}"

#Get current time
def get_datetime():
    now = datetime.datetime.now()
    return time.strftime("%Y-%m-%d %H:%M", time.localtime())

#Configure fields array
fields = [
    [None, get_hostname(), font24, [0, 0]],
    [None, get_ip(), font14, [0, 40]],
    ["WiFi", get_wifi_strength(), font14, [120, 40]],
    [None, get_datetime(), font14, [0, 60]],
    ["Mem", get_mem(), font14, [120, 60]],
    ["Disk", get_disk(), font14, [0, 80]],
    [None, get_temp(), font14, [120, 80]],
    ["Up", get_uptime(), font14, [0, 100]],
]

def main():
    
    #Initailize E-Ink display
    try:
        eink_initialize()
    except:
        print("Error initializing E-Ink display")

    #Draw fields on E-Ink display
    try:
        image = Image.new("1", (250, 122), 255)
        draw = ImageDraw.Draw(image)
        for name, field, font, (x, y) in fields:
            print(name, field, x, y)
            if name:
                draw.text((x, y), f"{name} {field}", font=font, fill=0)
            else:
                draw.text((x, y), f"{field}", font=font, fill=0)
        try:
            epd.display(epd.getbuffer(image))
        except:
            image.save("proto.png")
            print("Error displaying E-Ink image")
            epd.sleep()
        epd.sleep()
    except:
        print("Error drawing on E-Ink display")
        epd.sleep()


if __name__ == "__main__":
    main()
