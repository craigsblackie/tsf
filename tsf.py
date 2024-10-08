# Type Stuff Fast!
# Craig S. Blackie 2024

import base64
import codecs
import time
import argparse
import os
import hashlib
import zipfile
from pynput.keyboard import Key, Controller
from signal import signal, SIGINT
from sys import exit


# Handle keyboard interrupt
def handler(signal_received, frame):
    print("\nSIGINT or CTRL-C detected. Exiting gracefully")
    if args.zip:
        os.remove(target_filename)
    os.rmdir(tmp_path)
    exit(0)


# Print iterations progress
def print_progress_bar(
    iteration,
    total,
    prefix="",
    suffix="",
    decimals=1,
    length=100,
    fill="█",
    print_end="\r",
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + "-" * (length - filled_length)
    print(
        "\r%s |%s| %s%% %s [Remaining: %s]\r\r"
        % (prefix, bar, percent, suffix, total - iteration),
        end=print_end,
    )
    # Print New Line on Complete
    if iteration == total:
        print()

def make_tmpdir(path):
    try:
        os.mkdir(path)
    except OSError:
        print (f"Creation of the directory {path} failed")


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error(f"The file {arg} does not exist!")
    else:
        return open(arg, "rb")



def get_data(file_to_send):
    if args.text:
        # Attempt to detect encoding
        with open(file_to_send, 'rb') as f:
            raw = f.read(4)  # Read first 4 bytes to check for BOM
        if raw.startswith(codecs.BOM_UTF16_LE):
            encoding = 'utf-16'
        elif raw.startswith(codecs.BOM_UTF16_BE):
            encoding = 'utf-16'
        elif raw.startswith(codecs.BOM_UTF8):
            encoding = 'utf-8-sig'
        else:
            encoding = 'utf-8'  # Default to UTF-8 if no BOM found

        # Open file with the detected encoding
        with open(file_to_send, "r", encoding=encoding) as f:
            data = f.read()
    else:
        with open(file_to_send, "rb") as f:
            data = base64.b64encode(f.read()).decode()
    return data


def get_hash(file_to_hash):
    sha256_hash = hashlib.sha256()
    with open(file_to_hash, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):  
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

def get_buffer_hash(buffer_to_hash):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(buffer_to_hash.encode())
    return sha256_hash.hexdigest()

def compress_file(file):
    if zipfile.is_zipfile(file):
        print("already a zip archive")
    else:
        # create zip archive
        archive_name = tmp_path + "/" + file + ".zip"
        with zipfile.ZipFile(archive_name, "w") as zip_file_h:
            print("creating zip archive...")
            zip_file_h.write(file)
    return archive_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    keyboard = Controller()
    signal(SIGINT, handler) # Capture SIGINT signal
    tmp_path = "tsf_tmp"
    make_tmpdir(tmp_path)
    
    # These next two variables should be tuned for better reliability.
    bufferwait = 100  # wait for snooze value after this many key presses
    snooze = 0.100  # sleep for this amount after typing bufferwait keys

    dcount = 0  # counter to track when bufferwait is reached
    pcount = 0  # counter to track progress / key presses remaining
    scount = 0  # counter to track chunks of file when splitting
    fcount = 1  # counter for filenames when splitting file

    parser.add_argument(
        "-i",
        "--input",
        dest="filename",
        required=True,
        help="input file to be encoded and typed",
        metavar="FILE",
        type=lambda x: is_valid_file(parser, x),
    )
    parser.add_argument(
        "-d",
        "--delay",
        dest="delay",
        required=False,
        help="delay in seconds before typing (default=5)",
        metavar="int",
        default=5,
        type=int,
    )
    parser.add_argument(
        "-s",
        "--split",
        dest="split",
        required=False,
        help="number of parts to split file",
        metavar="int",
        default=1,
        type=int,
    )
    group.add_argument(
        "-t",
        "--text",
        dest="text",
        action="store_true",
        help="input is text not binary, will not base64 encode",
    )
    group.add_argument(
        "-z",
        "--zip",
        dest="zip",
        required=False,
        help="compress file to a zip archive (default=no)",
        action="store_true",
    )

    args = parser.parse_args()

    target_filename = args.filename.name
    if args.split == 0:
        parser.error("split value cannot be 0")

    if args.zip:
        target_filename = compress_file(target_filename)

    file_hash = get_hash(target_filename)
    print(f"{os.path.basename(target_filename)}  SHA256: {file_hash}\r")
    input(
        f"Typing will start in {args.delay} seconds after enter is pressed, ensure a text editor on the remote host is the window in focus. \n[PRESS ENTER]\r"
    )
    time.sleep(args.delay)

    dlen = len(get_data(target_filename))
    slen = len(get_data(target_filename)) // args.split
    buffer = ""

    for c in get_data(target_filename):
        keyboard.press(c)
        keyboard.release(c)

        if args.split != 1:
            buffer = buffer + c

        dcount += 1
        pcount += 1 
        scount += 1

        if dcount % bufferwait == 0:
            time.sleep(snooze)
            dcount = 0

        if args.split != 1 and pcount != dlen and scount % slen == 0:
            buffer_hash = get_buffer_hash(buffer)
            # Trailing spaces here to overwrite output buffer where it says "remaining [xxx]"
            print(f"Part {fcount} sha256 hash: {buffer_hash}         ", end="")
            confirmed = "false"
            while confirmed == "false":
                confirm = input(
                                f'\nSave file as part{fcount}.txt and use "certutil -hashfile part{fcount}.txt sha256" to verify.\nIf hash is correct, enter \'yes\' to continue or \'no\' to retry: '
                          )
                if confirm.lower() == 'yes':
                    print(f"Continuing with next part in {args.delay} seconds")
                    confirmed = "true"  
                    buffer = ""
                if confirm.lower() == 'no':
                    print(f"Last part will be retried in {args.delay} seconds")
                    time.sleep(args.delay)
                    for c in buffer:
                        keyboard.press(c)
                        keyboard.release(c)
                        dcount += 1
                        if dcount % bufferwait == 0:
                            time.sleep(snooze)
                            dcount = 0
            time.sleep(args.delay)
            scount = 0
            fcount += 1

        print_progress_bar(
            pcount, dlen, prefix="\rTyping:", suffix="Complete", length=50
        )
    if args.zip:
        os.remove(target_filename)
    os.rmdir(tmp_path)
    print("\nFinished.")
