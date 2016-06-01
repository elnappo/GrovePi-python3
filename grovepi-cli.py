#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import signal
import sys


def main(args):
    from grovepi import GrovePiException, analog_read, digital_read, pin_mode, analog_write, digital_write

    try:
        if args.digital and args.write:
            pin_mode(args.pin, "OUTPUT")
            digital_write(args.pin, args.value)
        elif args.digital and args.read:
            pin_mode(args.pin, "INPUT")
            print(digital_read(args.pin))
        elif args.analog and args.write:
            pin_mode(args.pin, "OUTPUT")
            analog_write(args.pin, args.value)
        elif args.analog and args.read:
            pin_mode(args.pin, "INPUT")
            print(analog_read(args.pin))
    except GrovePiException as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def sigterm_handler(_signo, _stack_frame):
    sys.exit(3)


if __name__ == "__main__":
    # catch SIGINT and SIGTERM
    signal.signal(signal.SIGINT, sigterm_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)

    parser = argparse.ArgumentParser(description="GrovePi command line tool to test sensors and actors.")

    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument("-d", "--digital", action='store_true')
    group1.add_argument("-a", "--analog", action='store_true')

    group2 = parser.add_mutually_exclusive_group(required=True)
    group2.add_argument("-r", "--read", action='store_true')
    group2.add_argument("-w", "--write", action='store_true')

    parser.add_argument('pin', type=int, help='pin')

    parser.add_argument("-v", "--value", type=int, metavar='<int>', help="value to set")

    args = parser.parse_args()
    if args.write and args.value is None:
        parser.print_usage(file=sys.stderr)
        print(parser.prog, "error: the following arguments are required when -w/--write is set: value", file=sys.stderr)
        sys.exit(2)

    main(args)
