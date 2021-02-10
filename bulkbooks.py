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
    ids = load_ids(ids_file)
    with open(filename) as file:
        begin_at = process_time()
        for line in file:
            ii += 1
            line = line.strip()
            id = get_id(line)
            if id == '':
                print(f'>>>> [{ii:.>4n}] error parsing book id from: [{line}]\n')
                ++parse_err
                continue
            if id in ids:
                ++skipped
                print(f'>>>> [{ii:.>4n}] skipping previously downloaded book id:{id:<15}')
                print(f'            URL was: {line}\n')
                continue
            try:
                args = parse_args(parser, [id])
                start = process_time()
                SafariBooks(args)
                elapsed_time = process_time() - start
                actual_time += elapsed_time
                ids.add(id)
                save_ids(ids_file, ids)
                ++done
                print(f'>>>> [{ii:.>4n}] Book id:{id:<15} processed successfully in:{elapsed_time:.0f} seconds')
            except:
                print(f'>>>> [{ii:.>4n}] Exception while getting Book id:{id:<15}')

            delay_time = randint(3,19)
            print(f"+++ cooling down sockets for {delay_time} seconds +++\n")
            sleep(delay_time)

        total_processing = process_time() - begin_at
        print(f'Processed {ii:>4n} Urls in {actual_time:.0f} seconds')
        print(f'Parse errors: {parse_err:>3}')
        print(f'Skipped     : {skipped:>3}')
        print(f'Downloaded  : {done:>3}')
        print(f'Overall time: {total_processing:.>7,.0f} seconds')
        avg_processing = actual_time / done
        print(f'Average Time: {avg_processing:.>7,.0f} seconds per book')


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
