import csv
import sys

reader = csv.DictReader(sys.stdin)
cur_poem_id = None
print('<?xml version="1.0" encoding="UTF-8"?>')
print('<KOKONAISUUS>')
for r in reader:
    if cur_poem_id != r['poem_id']:
        if cur_poem_id is not None:
            print('</TEXT>')
            print('</ITEM>')
        cur_poem_id = r['poem_id']
        print('<ITEM nro="{}" y="1840" k="skvr_77">'.format(cur_poem_id))
        print('<META>')
        print('<TEOS>Kanteletar</TEOS>')
        print('<OSA>{}</OSA>'.format(int(cur_poem_id[2:4])))
        print('<ID>{}</ID>'.format(int(cur_poem_id[4:])))
        print('</META>')
        print('<TEXT>')
    print('<{}>{}</{}>'.format(r['verse_type'], r['text'], r['verse_type']))
if cur_poem_id is not None:
    print('</TEXT>')
    print('</ITEM>')
print('</KOKONAISUUS>')

