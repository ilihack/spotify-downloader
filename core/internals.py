import argparse
import spotipy.oauth2 as oauth2
from urllib.request import quote
from slugify import SLUG_OK, slugify

import sys
import os
from core.logger import log, log_leveller, _LOG_LEVELS_STR


def input_link(links):
    """ Let the user input a choice. """
    while True:
        try:
            log.info('Choose your number:')
            the_chosen_one = int(input('> '))
            if 1 <= the_chosen_one <= len(links):
                return links[the_chosen_one - 1]
            elif the_chosen_one == 0:
                return None
            else:
                log.warning('Choose a valid number!')
        except ValueError:
            log.warning('Choose a valid number!')


def trim_song(file):
    """ Remove the first song from file. """
    with open(file, 'r') as file_in:
        data = file_in.read().splitlines(True)
    with open(file, 'w') as file_out:
        file_out.writelines(data[1:])


def get_arguments():
    parser = argparse.ArgumentParser(
        description='Download and convert songs from Spotify, Youtube etc.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '-s', '--song', help='download song by spotify link or name')
    group.add_argument(
        '-l', '--list', help='download songs from a file')
    group.add_argument(
        '-p', '--playlist', help='load songs from playlist URL into <playlist_name>.txt')
    group.add_argument(
        '-b', '--album', help='load songs from album URL into <album_name>.txt')
    group.add_argument(
        '-u', '--username',
        help="load songs from user's playlist into <playlist_name>.txt")
    parser.add_argument(
        '-m', '--manual', default=False,
        help='choose the song to download manually', action='store_true')
    parser.add_argument(
        '-nm', '--no-metadata', default=False,
        help='do not embed metadata in songs', action='store_true')
    parser.add_argument(
        '-a', '--avconv', default=False,
        help='Use avconv for conversion otherwise set defaults to ffmpeg',
        action='store_true')
    parser.add_argument(
        '-f', '--folder', default=(os.path.join(sys.path[0], 'Music')),
        help='path to folder where files will be stored in')
    parser.add_argument(
        '--overwrite', default='prompt',
        help='change the overwrite policy',
        choices={'prompt', 'force', 'skip'})
    parser.add_argument(
        '-i', '--input-ext', default='.m4a',
        help='prefered input format .m4a or .webm (Opus)')
    parser.add_argument(
        '-o', '--output-ext', default='.mp3',
        help='prefered output extension .mp3 or .m4a (AAC)')
    parser.add_argument(
        '-d', '--dry-run', default=False,
        help='Show only track title and YouTube URL',
        action='store_true')
    parser.add_argument(
        '-mo', '--music-videos-only', default=False,
        help='Search only for music on Youtube',
        action='store_true')
    parser.add_argument(
        '-ll', '--log-level', default='INFO',
        choices=_LOG_LEVELS_STR,
        type=str.upper,
        help='set log verbosity')

    parsed = parser.parse_args()
    parsed.log_level = log_leveller(parsed.log_level)

    return parsed


def is_spotify(raw_song):
    """ Check if the input song is a Spotify link. """
    status = len(raw_song) == 22 and raw_song.replace(" ", "%20") == raw_song
    status = status or raw_song.find('spotify') > -1
    return status


def is_youtube(raw_song):
    """ Check if the input song is a YouTube link. """
    status = len(raw_song) == 11 and raw_song.replace(" ", "%20") == raw_song
    status = status and not raw_song.lower() == raw_song
    status = status or 'youtube.com/watch?v=' in raw_song
    return status


def sanitize_title(title):
    """ Generate filename of the song to be downloaded. """
    title = title.replace(' ', '_')
    title = title.replace('/', '_')

    # slugify removes any special characters
    title = slugify(title, ok='-_()[]{}', lower=False)
    return title


def generate_token():
    """ Generate the token. Please respect these credentials :) """
    credentials = oauth2.SpotifyClientCredentials(
        client_id='4fe3fecfe5334023a1472516cc99d805',
        client_secret='0f02b7c483c04257984695007a4a8d5c')
    token = credentials.get_access_token()
    return token


def filter_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
    for temp in os.listdir(path):
        if temp.endswith('.temp'):
            os.remove(os.path.join(path, temp))


def videotime_from_seconds(time):
    if time<60:
        return str(time)
    if time<3600:
        return '{}:{}'.format(str(time//60), str(time%60).zfill(2))

    return '{}:{}:{}'.format(str(time//60),
                             str((time%60)//60).zfill(2),
                             str((time%60)%60).zfill(2))
