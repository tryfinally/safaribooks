import dbm
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
    parts = line.split('/')
    id = parts.pop()
    if id != '':
        return id
    return parts.pop()

def process(filename):
    ids_file = 'downloaded-ids.db'
    ids = set()
    parser = define_arg_parser()
    ii = 1
    with open(filename) as file:
        for line in file:
            line = line.strip()
            if line == '':
                continue

            id = get_id(line)
            ids = load_ids(ids_file)
            # print("ID >>>>>>>> " + str(ids))
            if id in ids:
                print(">>>> skipping book id: " + id)
                continue
            args = parse_args(parser, [id])
            SafariBooks(args)
            ii += 1
            ids.add(id)
            print(f'>>> Finished Book {id} Number {ii}')
            save_ids(ids_file, ids)
    # print(ids)


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
