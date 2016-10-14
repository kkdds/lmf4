import pexpect
import re

from threading import Thread
from time import sleep

class Chromium(object):

    _LAUNCH_CMD = '/usr/bin/chromium-browser -kiosk %s'
    #_LAUNCH_CMD = '/usr/bin/chromium-browser %s'
    _QUIT_CMD = 'q'

    paused = False
    subtitles_visible = True

    _VOF=1

    def __init__(self, mediafile):
        cmd = self._LAUNCH_CMD % (mediafile)
        #print(cmd)
        #self._process = pexpect.spawn('killall -9 chromium-browser')
        self._process = pexpect.spawn(cmd)

        self._end_thread = Thread(target=self._get_end)
        self._end_thread.start()
 
    def _get_end(self):
        while True:
            sleep(1)
            index = self._process.expect([pexpect.TIMEOUT,
                                            pexpect.EOF])
            if index == 1: 
                print('KEY stop EOF '+str(index))
                #self.stop()
                break
        self._VOF=0
        self.stop()
            
    def stop(self):
        self._process.send(self._QUIT_CMD)
        self._process.terminate(force=True)
        #self._process = pexpect.spawn('feh -F '+self._IMG_FILE)

