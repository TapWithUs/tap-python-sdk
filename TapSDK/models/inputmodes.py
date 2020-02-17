import logging

class TapInputModes:
    def __init__(self, mode):
        self._modes = {
                "controller" : {"name": "Controller Mode", "code": bytearray([0x3,0xc,0x0,0x1])},
                "text" : {"name": "Text Mode", "code": bytearray([0x3,0xc,0x0,0x0])}
                }
        if mode in self._modes.keys():
            self.mode = mode
        else:
            logging.warning("Invalid mode \"%s\". Set to \"text\"" % mode)
            self.mode = "text"
    
    def get_command(self):
        return self._modes[self.mode]["code"]

    def get_name(self, mode=None):
        return self._modes[self.mode]["name"]
