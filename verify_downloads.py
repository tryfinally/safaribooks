import os
import dbm
from enum import Enum
from random import randint
from shutil import copyfile
from time import sleep, time, process_time
from safaribooks import Display, SafariBooks, define_arg_parser, parse_args

class BOOK_PHASE(Enum):
    STARTED = 1     # we marked it as BEGIN, go ahead and download
    IN_PROGRESS = 2 # some other process started it
    COMPLETED = 3   # already downloaded

def mark_clear_downloading(file_name, id):
    while True:
        try:
            with dbm.open(file_name, 'cs') as db:
                key = str(id)
                phase = db.get(key)
                if not phase is None:
                    del db[key]
                # if phase == b'STARTED':
                #     del db[key]
                #     return BOOK_PHASE.STARTED
                return

        except dbm.error as x:
            if x.errno == 11:
                print(">> mark_begin dbm locked...retry")
                sleep(randint(0,3))
            else:
                raise x

def mark_begin_downloading(file_name, id):
    while True:
        try:
            with dbm.open(file_name, 'cs') as db:
                key = str(id)
                # print(f'before db.get({key})')
                # phase ='xx'
                phase = db.get(key)
                # print(f'after db.get: {phase}')
                if phase is None:
                    db[key] = b'STARTED'
                    return BOOK_PHASE.STARTED # you can start
                elif phase == b'STARTED':
                    return BOOK_PHASE.IN_PROGRESS # another process is handling it
                elif phase == b'COMPLETED':
                    return BOOK_PHASE.COMPLETED # alreaded completed download
                else:
                    print(f'{phase}')
                    raise RuntimeError("Internal Error")

        except dbm.error as x:
            if x.errno == 11:
                print(">> mark_begin dbm locked...retry")
                sleep(randint(0,3))
            else:
                raise x

def mark_done_downloading(file_name, id):
    while True:
        try:
            with dbm.open(file_name, 'cs') as db:
                key = str(id)
                phase = db.get(key)
                if phase is None:
                    # print(">>>>>>  Internal error, db is inconsistent")
                    raise RuntimeError("Internal error, db is inconsistent: finishing a job that was not started")
                elif phase == b'COMPLETED':
                    raise RuntimeError("Internal error, db is inconsistent: finishing a job that was already finished")
                elif phase == b'STARTED':
                    db[key] = b'COMPLETED'
                    return

        except dbm.error as x:
            if x.errno == 11:
                print(">> mark_done dbm locked...retry")
                sleep(randint(0,3))
            else:
                raise x

def get_id(line):
    try:
        parts = line.split('/')
        id = parts.pop()
        if id != '':
            return id
        return parts.pop()
    except:
        return ''

def process(filename, clear):
    ids_file = 'downloaded-ids.db'

    dir_map = dict()
    rootdir = './Books'
    dirs = list(os.listdir(rootdir))
    for dir in dirs:
        id = dir[dir.rfind('(')+1 : dir.rfind(')')]
        epub_file = id + '.epub'
        epub = os.path.join(rootdir, dir, epub_file)
        found = os.path.exists(epub)
        # if not ok:
        #     print(f'missing epub {epub_file}')
        dir_map[id] = (found, dir, epub)


    missing = set()
    parse_err = 0
    ok = 0
    notok = 0
    ii = 0
    with open(filename) as file:
        for line in file:
            ii += 1
            line = line.strip()
            id = get_id(line)
            if id == '':
                print(f'{Display.SH_YELLOW}>>>> [{ii:.>4n}]{Display.SH_DEFAULT} error parsing book id from: [{line}]\n')
                parse_err += 1
                continue

            r = dir_map.get(id, (False,'',''))
            if r[0]:
                ok += 1
                # print(f'{Display.SH_YELLOW}>>>> [{ii:.>4n}]{Display.SH_DEFAULT} Have epub id:{id:<15}')
            else:
                notok += 1
                if clear:
                    print(f'{Display.SH_YELLOW}>>>> [{ii:.>4n}] {Display.SH_BG_RED}Missing{Display.SH_DEFAULT} epub id:{id:<15}')
                    mark_clear_downloading(ids_file, id)
                    print(f'\t\t{Display.SH_YELLOW} Status reset {Display.SH_DEFAULT} for epub id:{id:<15}')
                missing.add(id)

    print('{}{}{}'.format(Display.SH_YELLOW,"="*20, Display.SH_DEFAULT))
    print(f'{Display.SH_YELLOW}Processed   :{Display.SH_DEFAULT} {ii:>6n} Urls')
    print(f'{Display.SH_YELLOW}Parse errors:{Display.SH_DEFAULT} {parse_err:>6}')
    print(f'{Display.SH_YELLOW}Present     :{Display.SH_DEFAULT} {ok:>6}')
    print(f'{Display.SH_YELLOW}Missing     :{Display.SH_DEFAULT} {notok:>6}')
    if len(missing) > 0:
        print(f'{Display.SH_YELLOW}Missing epub for ids:{Display.SH_DEFAULT}\n{missing}')



USAGE = "\n\nVerify bulk download and reset book ids that were not downloaded\n";
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f'{Display.SH_BG_RED}[!]{Display.SH_DEFAULT} {USAGE}')
        print("\t{sys.argv[0]} bookd_ids")
        print("\t\t verfiy epub present for all id in file bookd_ids")
        print("\t{sys.argv[0]} bookd_ids clear")
        print("\t\t verfiy epub present for all id in file bookd_ids and reset status of missing")
        exit(1)

    # elif len(sys.argv) > 2:
    #     print("[!] Error: too much arguments, try to enclose the string with quote '\"'." + USAGE)
    #     exit(1)

    file_name = sys.argv[1]
    clear = False
    if len(sys.argv) == 3:
        clear = sys.argv[2] == 'clear'
    copyfile('cookies.json', 'cookies.json.saved')
    process(file_name, clear)
