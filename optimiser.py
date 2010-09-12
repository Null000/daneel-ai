'''
For automatic AI battles. Automatically starts and kills the server and AI clients. Keeps score.
If manually killed you also have to kill the server. 
'''

import subprocess
import os
import time
#folder with daneel-ai
daneelAiFolder = "/home/null/5thousandparsec/fresh/daneel-ai"
#folder with config files for ther server
serverConfigFolder = "/home/null/3thousandparsec/tpserver-cpp/"

win1 = 0
win2 = 0
serverDeaths = 0
log = []

os.chdir(daneelAiFolder)
for i in range(1):
    print "round", i + 1
    kl = subprocess.Popen(["killall", "-9", "tpserver-cpp"])
    kl.wait()
    
    server = subprocess.Popen(["tpserver-cpp", "-v", "-C", serverConfigFolder + "quickstart-mtsec.conf"])
    time.sleep(5)
    ai1 = subprocess.Popen(["python", "daneel-ai.py", "-f", "mtsec", "-u", "ai:ai@localhost/aiTest", "-o", "1.0"])
    time.sleep(2)
    ai2 = subprocess.Popen(["python", "daneel-ai.py", "-f", "mtsec", "-u", "ai2:ai@localhost/aiTest", "-o", "0.7"])

    timer = 0
    while ai1.poll() == None and ai2.poll() == None and server.poll() == None:
        if timer > 3000:
            break
        time.sleep(1)
        timer += 1
        print "server", server.poll() 
        print "ai1", ai1.poll()
        print "ai2", ai2.poll()
        print "btw it's round", i + 1, "and the score is", win1, ":", win2
        print "server died", serverDeaths, "times"
        print "times says", timer
    time.sleep(10)
    print "it's the end"
    print "server", server.poll()
    print "ai1", ai1.poll()
    print "ai2", ai2.poll()

    
    if ai1.poll() == 99:
        win1 += 1
    if ai2.poll() == 99:
        win2 += 1
    if server.poll() != None:
        serverDeaths += 1
    
    log.append((i+1,ai1.poll(),ai2.poll(),server.poll()))
    
    #using ubuntu notification to make sure I don't forget about this while reading slashdot and webcomics
    notify = subprocess.Popen(["notify-send","Results",str(win1)+":"+str(win2)])
    
    try:
        server.terminate()
    except Exception:
        pass
    
    try:
        ai1.terminate()
    except Exception:
        pass
    
    try:
        ai2.terminate()
    except Exception:
        pass
    

time.sleep(5)
print "ai1 won", win1, "times"
print "ai2 won", win2, "times"
print "server died", serverDeaths, "times"
print log
kl = subprocess.Popen(["killall", "-9", "tpserver-cpp"])
notify = subprocess.Popen(["notify-send","END RESULTS",str(win1)+":"+str(win2)])