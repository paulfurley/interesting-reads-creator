import io
import sys
import datetime
import os
import webbrowser

from os.path import abspath, dirname, join as pjoin
from pprint import pprint

from pocket import Pocket, PocketException

p = Pocket(
        consumer_key='',
    access_token=''
)

HEADER = (
    '---\n'
    'title: "Interesting reads, {friendly_date}"\n'
    'permalink: /{slug}/\n'
    'category: interestingreads\n'
    '---\n\n'
    '*Interesting things I read on the Internet this week*\n\n'
    '<!--more-->\n\n'
)


def main(argv):

    today = datetime.datetime.now().date()
    current_monday = today - datetime.timedelta(days=today.weekday())
    previous_monday = current_monday - datetime.timedelta(days=7)

    print('between {} and {}'.format(previous_monday, current_monday))

    slug = make_slug(current_monday)
    filename = make_filename(slug, current_monday)

    if os.path.exists(filename):
        answer = input('Overwrite {} ? '.format(filename))
        if answer not in ('y', 'Y', 'yes'):
            print('Aborting.')
            return

    print('writing {}'.format(filename))

    with io.open(filename, 'w') as f:

        f.write(HEADER.format(
            slug=slug,
            friendly_date=current_monday.strftime('%-d %B %Y'),
            )
        )

        links = list(get_links_between(previous_monday, current_monday))
        for i, (title, url) in enumerate(links):

            print('\n{} / {}: {}\n{}'.format(i + 1, len(links), title, url))
            webbrowser.open(url)
            commentary = input('\nthoughts? ')

            f.write('- [{title}]({url})'.format(title=title, url=url))

            if commentary:
                f.write(' — {}\n\n'.format(commentary))
            else:
                f.write('\n\n')

    print('Now:\n'
          'cd ~/repo/www.paulfurley.com\n'
          'vim {filename} && git add {filename}'.format(filename=filename))


def make_slug(date):
    return 'interesting-reads-{date}'.format(date=date.isoformat())


def make_filename(slug, date):
    return pjoin(
        '/home/paul/repo/www.paulfurley.com/_posts',
        '{}-{}.markdown'.format(date.isoformat(), slug)
    )


def get_links_between(previous_monday, current_monday):
    try:
        # https://getpocket.com/developer/docs/v3/retrieve
        result = p.retrieve(
            since=to_timestamp(midnight(previous_monday))
        )
    except PocketException as e:
        print(e.message)

    else:
        if result['error']:
            raise RuntimeError(result['error'])

    pprint(result)

    def get_sort_id(id_and_entry):
        return -id_and_entry[1].get('sort_id', 0)

    for id_, entry in sorted(result['list'].items(), key=get_sort_id):
        try:
            dt = to_datetime(entry['time_added'])
        except KeyError:
            print('Skipping entry with no datetime:')
            pprint(entry)
            continue

        if dt < midnight(current_monday):
            # pprint(entry)

            title = entry['resolved_title']
            url = entry['given_url']

            yield (title, url)


def to_datetime(timestamp_string):
    return datetime.datetime.fromtimestamp(int(timestamp_string))


def to_timestamp(dt):
    from datetime import timezone

    return dt.replace(tzinfo=timezone.utc).timestamp()


def midnight(date):
    return datetime.datetime(date.year, date.month, date.day)


if __name__ == '__main__':
    main(sys.argv)
