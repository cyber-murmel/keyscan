#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from evdev import InputDevice, list_devices, ecodes, categorize, events
from asyncio import create_task, get_event_loop, gather, CancelledError
from argparse import ArgumentParser
from logging import debug, info, warning, error, critical, basicConfig as logConfig
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

from .keycodes import KEYCODE_CHAR_MAP

class NoInputDeviceError(Exception):
    pass

class KeyScanner():
    def __init__(self, callback = lambda buf : print(buf), delimiter='\n'):
        self.devices = [InputDevice(path) for path in list_devices()]
        if not self.devices:
            raise NoInputDeviceError("No input device found. Check permissions and connections")
        else:
            self.callback = callback
            self.delimiter = delimiter

    def run(self):
        loop = get_event_loop()
        tasks = gather(*[loop.create_task(self._key_event_routine(device)) for device in self.devices])
        loop.run_until_complete(tasks)

    async def _key_event_routine(self, device):
        buf = ""
        shift = False
        while True:
            async for event in device.async_read_loop():
                # handle key events only
                if event.type == ecodes.EV_KEY:
                    key_event = events.KeyEvent(event)
                    debug(f"{key_event.keycode:16s} {'down' if key_event.keystate else 'up'}")
                    # handle shift being pressed
                    if key_event.keycode in ['KEY_LEFTSHIFT', 'KEY_RIGHTSHIFT']:
                        shift = True if key_event.key_down == key_event.keystate else False
                    elif key_event.key_down == key_event.keystate and \
                        key_event.keycode in KEYCODE_CHAR_MAP:
                        char = KEYCODE_CHAR_MAP[key_event.keycode][shift]
                        if self.delimiter == char:
                            self.callback(buf)
                            buf = ""
                        else:
                            buf += char

def parse_arguments():
    parser = ArgumentParser(
        description="evdev based key scanner",
    )
    verbose = parser.add_mutually_exclusive_group()
    verbose.add_argument(   "-v",   "--verbose",    action="count",   help="set verbose loglevel")
    args = parser.parse_args()
    # configure logging
    log_format = "%(asctime)-15s %(levelname)-8s %(message)s"
    if 1 == args.verbose:
        logConfig(level=log_level, format=log_format)
        info("Log level set to INFO")
    elif 2 == args.verbose:
        logConfig(level=DEBUG, format=log_format)
        debug("Log level set to DEBUG")
    else:
        logConfig(level=WARNING, format=log_format)
    return args

def main():
    args = parse_arguments()
    keyscanner = KeyScanner()
    try:
        info("Running Scanner")
        keyscanner.run()
    except KeyboardInterrupt:
        info("Exiting")
        pass

if __name__ == '__main__':
    main()
