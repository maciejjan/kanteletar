import argparse
import csv
import os.path as P
import re
import sys


TEXT_INDENT_WIDTH = 10

def _make_type_id(*args):
    return 'kt_t' + ''.join(map(lambda s: '{:0>2}'.format(s), args))


def _make_poem_id(b_id, p_id):
    return 'kt' + '{:0>2}'.format(b_id)  + '{:0>4}'.format(p_id)


def read_and_parse_toc(fp):
    'Reads the table of contents.'
    
    results = []
    # [b]ook, [t]opic and [s]ub[t]opic IDs
    b_id, b_name, t_id, t_name, st_id, st_name = -1, None, 0, None, 0, None
    next_p_id = 1
    line = None
    while line != 'AINEHISTO':
        line = fp.readline().strip()
    while line != 'ALAVIITTEET':
        line = fp.readline().strip()
        # new book
        if line == 'ALKULAUSE' or line.endswith(' KIRJA'):
            b_id += 1
            t_id, t_name, st_id, st_name, next_p_id = 0, None, 0, None, 1
            b_name = str(b_id) + '. ' + fp.readline().strip()
            if b_name.endswith('Alkulause'):
                b_name = str(b_id) + '. ' + fp.readline().strip()
            results.append((_make_type_id(b_id, t_id, st_id), None, b_name))
        # new topic
        elif re.match('[IV]+\.', line):
            t_id += 1
            st_id, st_name = 0, None
            t_name = re.sub('\s+', ' ', line)
            results.append((_make_type_id(b_id, t_id, st_id),
                            _make_type_id(b_id, 0, 0), t_name))
        # poem
        elif re.match('[0-9]+\. ', line):
            title = line[len(str(next_p_id))+2:].strip()
            results.append((_make_poem_id(b_id, next_p_id),
                            _make_type_id(b_id, t_id, st_id), title))
            next_p_id += 1
        elif line and not re.match('\(.*\)', line) and not line.isupper():
            st_id += 1
            st_name = re.sub('\s+', ' ', line)
            results.append((_make_type_id(b_id, t_id, st_id),
                            _make_type_id(b_id, t_id, 0), st_name))
    return results


def transform_texts(infp, outfp):
    'Transforms the the texts to verses in CSV format.'
    
    b_id, p_id, nro, i = -1, 0, None, 0
    # n_empty - The number of empty lines since the last text line.
    # If it's >= 4, we conclude that the current poem has ended
    # and we are now seeing loose text lines that should be discarded.
    n_empty = 0
    writer = csv.writer(outfp)
    writer.writerow(('poem_id', 'pos', 'verse_type', 'text'))
    for line in infp:
        line = line.rstrip()
        if not line.strip():
            n_empty += 1
            continue
        if line.endswith(' KIRJA'):
            b_id += 1 
            p_id = 0
            n_empty = 0
        elif line.startswith(' ' * TEXT_INDENT_WIDTH):
            line = line.strip()
            if line.startswith(str(p_id+1) + '. '):
                p_id += 1
                nro = _make_poem_id(b_id, p_id)
                i = 1
                writer.writerow((nro, i, 'CPT', line))
                i += 1
                n_empty = 0
            elif n_empty < 4:
                writer.writerow((nro, i, 'V', line))
                i += 1
                n_empty = 0
        elif line.startswith('Poika.   ') or line.startswith('Tyttö.   '):
            writer.writerow((nro, i, 'K', line[:TEXT_INDENT_WIDTH].strip()))
            i += 1
            writer.writerow((nro, i, 'V', line[TEXT_INDENT_WIDTH:].strip()))
            i += 1
            n_empty = 0


def write_poem_types(toc, outfp):
    writer = csv.writer(outfp)
    writer.writerow(('poem_id', 'type_id', 'type_is_minor'))
    for p_id, t_id, title in toc:
        if not p_id.startswith('kt_t'):
            writer.writerow((p_id, t_id, '0'))


def write_types(toc, outfp):
    writer = csv.writer(outfp)
    writer.writerow(('type_id', 'type_name', 'type_description',
                     'type_parent_id'))
    for t_id, par_id, title in toc:
        if t_id.startswith('kt_t'):
            writer.writerow((t_id, title, None, par_id))


def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert Kanteletar to CSV.')
    parser.add_argument(
        'input_file', metavar='FILE',
        help='The input file (Kanteletar from Project Gutenberg).')
    parser.add_argument(
        '-d', '--output-dir', metavar='PATH', default='.',
        help='The directory to write output files to.')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    with open(args.input_file) as fp:
        toc = read_and_parse_toc(fp)
        with open(P.join(args.output_dir, 'types.csv'), 'w+') as outfp:
            write_types(toc, outfp)
        with open(P.join(args.output_dir, 'poem_types.csv'), 'w+') as outfp:
            write_poem_types(toc, outfp)
        with open(P.join(args.output_dir, 'verses.csv'), 'w+') as outfp:
            transform_texts(fp, outfp)
