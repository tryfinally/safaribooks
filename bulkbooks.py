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

def mark_begin_downloading(file_name, id):
    print("lookup ")
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

# def load_ids(file_name):
#     while True:
#         try:
#             with dbm.open(file_name, 'c') as db:
#                return eval(db['ids'])
#         except dbm.error as x:
#             if x.errno == 11:
#                 print(">>locked...retry")
#                 sleep(1)
#                 continue
#             return set()

# def save_ids(file_name, ids):
#     while True:
#         try:
#             with dbm.open(file_name, 'c') as db:
#                db['ids'] = repr(ids)
#                return
#         except dbm.error as x:
#             if x.errno == 11:
#                 print(">>locked...retry")
#                 sleep(1)
#                 continue
#             raise x

def get_id(line):
    try:
        parts = line.split('/')
        id = parts.pop()
        if id != '':
            return id
        return parts.pop()
    except:
        return ''

def process(filename):
    ids_file = 'downloaded-ids.db'
    ids = set()
    parser = define_arg_parser()
    ii = 0
    actual_time = done = skipped = parse_err = 0
    # ids = load_ids(ids_file)
    with open(filename) as file:
        begin_at = process_time()
        for line in file:
            ii += 1
            line = line.strip()
            id = get_id(line)
            if id == '':
                print(f'{Display.SH_YELLOW}>>>> [{ii:.>4n}]{Display.SH_DEFAULT} error parsing book id from: [{line}]\n')
                parse_err += 1
                continue
            work_phase = mark_begin_downloading(ids_file, id)
            if work_phase  !=  BOOK_PHASE.STARTED: # == BOOK_PHASE.COMPLETED or work == BOOK_PHASE.STARTED:
                skipped += 1
                skip_reason = 'previously dwonloaded' if work_phase == BOOK_PHASE.COMPLETED else 'a concurently downloading'
                print(f'{Display.SH_YELLOW}>>>> [{ii:.>4n}]{Display.SH_DEFAULT} skipping {skip_reason} book with id:{id:<15}')
                print(f'            URL was: {line}\n')
                continue

            try:
                args = parse_args(parser, [id])
                start = process_time()
                SafariBooks(args)
                elapsed_time = process_time() - start
                actual_time += elapsed_time

                mark_done_downloading(ids_file, id)
                done += 1
                print(f'{Display.SH_YELLOW}>>>> [{ii:.>4n}]{Display.SH_DEFAULT} Book id:{id:<15} processed successfully in:{elapsed_time:.0f} seconds')

            except:
                exception = sys.exc_info()[0]
                print(f'{Display.SH_BG_RED}>>>> [{ii:.>4n}]{Display.SH_DEFAULT} Error downloading book id:{id:<15} exception: {exception}\n')
                # WORKAROUND: safaribook will delete the cookie file, restore it
                copyfile('cookies.json.saved', 'cookies.json')
                sleep(2)
                continue

            delay_time = randint(3,13)
            print(f"+++ cooling down sockets for {delay_time} seconds +++\n")
            sleep(delay_time)

        total_processing = process_time() - begin_at
        print('{}{}{}'.format(Display.SH_YELLOW,"="*20, Display.SH_DEFAULT))
        print(f'{Display.SH_YELLOW}Processed   :{Display.SH_DEFAULT} {ii:>6n} Urls in {actual_time:.0f} seconds')
        print(f'{Display.SH_YELLOW}Parse errors:{Display.SH_DEFAULT} {parse_err:>6}')
        print(f'{Display.SH_YELLOW}Skipped     :{Display.SH_DEFAULT} {skipped:>6}')
        print(f'{Display.SH_YELLOW}Downloaded  :{Display.SH_DEFAULT} {done:>6}')
        print(f'{Display.SH_YELLOW}Overall time:{Display.SH_DEFAULT} {total_processing:>6.0f} seconds')
        if done != 0:
            avg_processing = round(actual_time / done)
            print(f'{Display.SH_YELLOW}Average Time:{Display.SH_DEFAULT} {avg_processing:>6} seconds per book')


USAGE = "\n\nDownload and generate an EPUB of your favorite books from Safari Books Online.\n" + \
        "expects one argumnet: filename of a file containing books URLs or IDs\n" + \
        "[!] make sure to run sso_cookies.py first"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("[!] Error: too few arguments." + USAGE)
        exit(1)

    elif len(sys.argv) > 2:
        print("[!] Error: too much arguments, try to enclose the string with quote '\"'." + USAGE)
        exit(1)

    file_name = sys.argv[1]
    copyfile('cookies.json', 'cookies.json.saved')
    process(file_name)
