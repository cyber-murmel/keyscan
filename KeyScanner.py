#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from evdev import InputDevice, list_devices, ecodes, categorize, events
from asyncio import create_task, get_event_loop, gather, CancelledError
from argparse import ArgumentParser
from logging import debug, info, warning, error, critical, basicConfig as logConfig
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

KEYCODE_CHAR_MAP = {
    'KEY_1':            {False: '1', True: '!'},
    'KEY_2':            {False: '2', True: '@'},
    'KEY_3':            {False: '3', True: '#'},
    'KEY_4':            {False: '4', True: '$'},
    'KEY_5':            {False: '5', True: '%'},
    'KEY_6':            {False: '6', True: '^'},
    'KEY_7':            {False: '7', True: '&'},
    'KEY_8':            {False: '8', True: '*'},
    'KEY_9':            {False: '9', True: '('},
    'KEY_0':            {False: '0', True: ')'},
    'KEY_MINUS':        {False: '-', True: '_'},
    'KEY_EQUAL':        {False: '=', True: '+'},
    'KEY_A':            {False: 'a', True: 'A'},
    'KEY_B':            {False: 'b', True: 'B'},
    'KEY_C':            {False: 'c', True: 'C'},
    'KEY_D':            {False: 'd', True: 'D'},
    'KEY_E':            {False: 'e', True: 'E'},
    'KEY_F':            {False: 'f', True: 'F'},
    'KEY_G':            {False: 'g', True: 'G'},
    'KEY_H':            {False: 'h', True: 'H'},
    'KEY_I':            {False: 'i', True: 'I'},
    'KEY_J':            {False: 'j', True: 'J'},
    'KEY_K':            {False: 'k', True: 'K'},
    'KEY_L':            {False: 'l', True: 'L'},
    'KEY_M':            {False: 'm', True: 'M'},
    'KEY_N':            {False: 'n', True: 'N'},
    'KEY_O':            {False: 'o', True: 'O'},
    'KEY_P':            {False: 'p', True: 'P'},
    'KEY_Q':            {False: 'q', True: 'Q'},
    'KEY_R':            {False: 'r', True: 'R'},
    'KEY_S':            {False: 's', True: 'S'},
    'KEY_T':            {False: 't', True: 'T'},
    'KEY_U':            {False: 'u', True: 'U'},
    'KEY_V':            {False: 'v', True: 'V'},
    'KEY_W':            {False: 'w', True: 'W'},
    'KEY_X':            {False: 'x', True: 'X'},
    'KEY_Y':            {False: 'y', True: 'Y'},
    'KEY_Z':            {False: 'z', True: 'Z'},
    'KEY_SEMICOLON':    {False: ';', True: ':'},
    'KEY_LEFTBRACE':    {False: '[', True: '{'},
    'KEY_RIGHTBRACE':   {False: ']', True: '}'},
    'KEY_APOSTROPHE':   {False: '\'', True: '"'},
    'KEY_BACKSLASH':    {False: '\\', True: '|'},
    'KEY_GRAVE':        {False: '`', True: '~'},
    'KEY_COMMA':        {False: ',', True: '<'},
    'KEY_DOT':          {False: '.', True: '>'},
    'KEY_SLASH':        {False: '/', True: '?'},
    'KEY_KP0':          {False: '0', True: ''},
    'KEY_KP0':          {False: '1', True: ''},
    'KEY_KP0':          {False: '2', True: ''},
    'KEY_KP0':          {False: '3', True: ''},
    'KEY_KP0':          {False: '4', True: ''},
    'KEY_KP0':          {False: '5', True: ''},
    'KEY_KP0':          {False: '6', True: ''},
    'KEY_KP0':          {False: '7', True: ''},
    'KEY_KP0':          {False: '8', True: ''},
    'KEY_KP0':          {False: '9', True: ''},
    'KEY_KPDOT':        {False: '.', True: ''},
    'KEY_KPPLUS':       {False: '+', True: '+'},
    'KEY_KPMINUS':      {False: '-', True: '-'},
    'KEY_KPASTERISK':   {False: '*', True: '*'},
    'KEY_KPSLASH':      {False: '/', True: '/'},
    'KEY_ENTER':        {False: '\n', True: '\n'},
}

class NoInputDeviceError(Exception):
    """No input device found. Check permissions and connections"""
    pass

class KeyScanner():
    def __init__(self, callback = lambda buf : print(buf), delimiter='\n'):
        self.devices = [InputDevice(path) for path in list_devices()]
        if not self.devices:
            raise NoInputDeviceError
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
    return args

def main():
    args = parse_arguments()
    log_level=WARNING
    if 1 == args.verbose:
        log_level=INFO
    if 2 == args.verbose:
        log_level=DEBUG
    logConfig(level=log_level, format="%(asctime)-15s %(levelname)-8s %(message)s")
    keyscanner = KeyScanner()
    try:
        info("Running Scanner")
        keyscanner.run()
    except KeyboardInterrupt:
        info("Exiting")
        pass

if __name__ == '__main__':
    main()
