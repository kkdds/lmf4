import pexpect
import re

from threading import Thread
from time import sleep

class OMXPlayer(object):

    _LAUNCH_CMD = '/usr/bin/omxplayer --win 0,0,800,420 -o hdmi %s'
    _PAUSE_CMD = 'p'
    _TOGGLE_SUB_CMD = 's'
    _QUIT_CMD = 'q'
    _IMG_FILE = 'q'

    paused = False
    subtitles_visible = True

    _VOF=1

    def __init__(self, mediafile):
        cmd = self._LAUNCH_CMD % (mediafile)
        #print(cmd)
        self._process = pexpect.spawn(cmd)

        self._end_thread = Thread(target=self._get_end)
        self._end_thread.start()
 
    def _get_end(self):
        while True:
            sleep(0.5)
            index = self._process.expect([pexpect.TIMEOUT,
                                            pexpect.EOF])
            if index == 1: 
                print('video press stop EOF '+str(index))
                #self.stop()
                break
            else:
                print('video TIMEOUT '+str(index))
                #self.stop()
                #break
                continue
        self._VOF=0
        self.stop()
            
    def stop(self):
        self._process.send(self._QUIT_CMD)
        self._process.terminate(force=True)
        self._process = pexpect.spawn('feh -F '+self._IMG_FILE)
			
    def toggle_pause(self):
        if self._process.send(self._PAUSE_CMD):
            self.paused = not self.paused

    def toggle_subtitles(self):
        if self._process.send(self._TOGGLE_SUB_CMD):
            self.subtitles_visible = not self.subtitles_visible

    def set_speed(self):
        raise NotImplementedError

    def set_audiochannel(self, channel_idx):
        raise NotImplementedError

    def set_subtitles(self, sub_idx):
        raise NotImplementedError

    def set_chapter(self, chapter_idx):
        raise NotImplementedError

    def set_volume(self, volume):
        raise NotImplementedError

    def seek(self, minutes):
        raise NotImplementedError
