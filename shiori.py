#!/bin/python3

from os import listdir
from os.path import isfile, isdir, join, splitext
import logging
import codecs
import argparse
import importlib

import ultraparse

class LibraryManager:
    def __init__(self, directory):
        self.directory = directory
        self.library = []

    def scan(self):
        self.scan_directory(self.directory)

    def scan_directory(self, directory):
        subdirs = [f for f in listdir(directory) if isdir(join(directory, f))]
        if len(subdirs) == 0:
            #No subdirectories, so this might be an ultrastar songdir
            files = [f for f in listdir(directory) if isfile(join(directory, f))]
            if self.is_songdir(files):
                txtfiles = [t for t in files if splitext(t)[1] == ".txt"]
                if (len(txtfiles) > 1):
                    logging.info("Found 2 or more text files in likely song directory " + directory)
                    map(lambda n: self.parse_songfile(join(directory, n)), txtfiles)
                elif (len(txtfiles) == 0):
                    logging.warning("Could not find text file in likely song directory " + directory)
                else:
                    logging.info("Found likely ultrastar file in directory " + directory)
                    self.parse_songfile(join(directory, txtfiles[0]))
        else:
            #If there are subdirectories, search them
            for subdir in subdirs:
                self.scan_directory(join(directory, subdir))

    def is_songdir(self, filenames):
        #All valid songs should have an audio file and a text file
        extensions = map(lambda n: splitext(n)[1], filenames)
        return (".mp3" in extensions or ".ogg" in extensions or ".aac" in extensions) and (".txt" in extensions)

    def parse_songfile(self, filename):
        logging.info("Now parsing file" + filename)
        try:
            #Is it UTF-8?
            f = open(filename, encoding="utf-8-sig", errors="strict")
            for line in f:
                pass
            f.seek(0)
            song_data = ultraparse.SongFile(iter(f.readlines()), filename)
            song_data.parse()
            self.library.append(song_data)
            f.close()
        except UnicodeDecodeError:
            #Apparently not, just let python take a guess
            f = open(filename, encoding=None, errors="strict")
            song_data = ultraparse.SongFile(iter(f.readlines()), filename)
            song_data.parse()
            self.library.append(song_data)
            f.close()
        """except Exception as e:
            logging.warn("Encountered unexpected error parsing file " + filename + ": " + str(e))"""

def run_scan():
    parser = argparse.ArgumentParser(description = "Scan directory for ultrastar songs, then export them in a given format")
    parser.add_argument('dir', metavar='dir', default="./", type=str,
                        help="the path to the directory which should be scanned")
    parser.add_argument('store', metavar='store', default="json", type=str,
                        help="the backed which should be used to export song data")
    parser.add_argument('--load_covers', action='store_true',
                        help="also load image files for the covers")
    parser.add_argument('--load-bg', action='store_true',
                        help="also load image files for the background images")
    parser.add_argument('-o', '--export_opts', metavar='export_opts', default="",
                        type=str,
                        help="options to be passed to the exporter backend in the format `key1=val1,key2=val2...`")
    args = parser.parse_args()
    backend = importlib.import_module("export_formats." + args.store)
    lib = LibraryManager(args.dir)
    lib.scan()


if __name__ == "__main__":
    run_scan()
