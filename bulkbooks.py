from safaribooks import SafariBooks, define_arg_parser, parse_args

def get_id(line):
    parts = line.split('/')
    id = parts.pop()
    if id != '':
        return id
    return parts.pop()

def process(filename):
    parser = define_arg_parser()
    ids = set()
    ii = 1
    with open(filename) as file:
        for line in file:
            line = line.strip()
            if line == '':
                continue
            id = get_id(line)
            if id in ids:
                continue
            args = parse_args(parser, [id])
            SafariBooks(args)
            ii += 1
            ids.add(id)

    print(ids)



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
