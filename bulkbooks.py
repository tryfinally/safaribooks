import dbm
from random import randint
from time import sleep, time, process_time
from safaribooks import SafariBooks, define_arg_parser, parse_args


def load_ids(file_name):
    with dbm.open(file_name, 'c') as db:
        try:
            return eval(db['ids'])
        except:
            return set()

def save_ids(file_name, ids):
    with dbm.open(file_name, 'c') as db:
        db['ids'] = repr(ids)

def get_id(line):
    try:
        line = line.strip()
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
    ii = 1
    actual_time = done = skipped = parse_err = 0

    with open(filename) as file:
        begin_at = process_time()
        for line in file:
            ii += 1
            id = get_id(line)
            if id == '':
                print(f'>>>> error parsing book id from : {line}')
                ++parse_err
                continue
            ids = load_ids(ids_file)
            # print("ID >>>>>>>> " + str(ids))
            if id in ids:
                ++skipped
                print(f'>>>> skipping book id: {id}')
                print(f'>>>> from: {line}')
                continue
            args = parse_args(parser, [id])
            try:
                start = process_time()
                SafariBooks(args)
                elapsed_time = process_time() - start
                actual_time += elapsed_time
                ++done
                ids.add(id)
                save_ids(ids_file, ids)
                print(f'>>> {ii} Book: {id} processed successfully in {elapsed_time} seconds')
            except:
                print(f'>>> Error retrieving Book {id} Number {ii}')
            print(f"+++ iteration {ii} +++")
            print(f"+++ cooling down sockets+++")
            sleep(randint(3,13))
        total_processing = process_time() - begin_at
        print(f'Processed {ii} Urls in {actual_time} seconds')
        print(f'Parse errors: {parse_err}')
        print(f'Skipped     : {skipped}')
        print(f'Created     : {done}')
        print(f'Overall time: {total_processing} seconds')
        avg_processing = actual_time / done
        print(f'Average Book: {avg_processing} seconds')


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
    process(file_name)
