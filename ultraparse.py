import re
import logging
from os.path import join

class SongFile:
    def __init__(self, file, filename, dir):
        self.dir = dir
        self.textfile = file
        self.filename = filename
        self.duetsingers = []
        self.is_duet = False

    def parse(self):
        line = self.next_line().strip()
        while (line and line != "E"):
            self.parse_line(line)
            line = self.next_line()
        if not self.is_duet:
            del self.duetsingers
        if not (hasattr(self, "title") and hasattr(self, "artist")):
            logging.error("File " + self.filename + " is missing essential data. Ignoring...")
            return False
        else:
            return True

    def load_cover(self):
        with open(join(self.dir, self.cover_path), mode='rb') as f:
            return f.read()

    def load_bg(self):
        with open(join(self.dir, self.background_path), mode='rb') as f:
            return f.read()

    def parse_line(self, line):
        if line[0] == "#":
            try:
                [com, val] = line.split(':', 1)
            except ValueError:
                # Badly formatted line. We shall skip
                line = self.next_line()
                self.parse_line(line)
                return
            com = str.strip(com[1:]).upper()
            val = str.strip(val)
            #Metadata tag
            if com == "TITLE":
                self.title = val
            elif com == "ARTIST":
                self.artist = val
            elif com == "MP3":
                self.mp3file = val
            elif com == "GAP":
                self.startdelay = float(val.replace(',', '.'))
            elif com == "BPM":
                self.bpm = float(val.replace(',', '.'))
            elif com == "GENRE":
                self.genre = val
            elif com == "EDITION":
                self.edition = val
            elif com == "COVER":
                self.cover_path = val
            elif com == "VIDEO":
                self.video_path = val
            elif com == "BACKGROUND":
                self.background_path = val
            elif com == "LANGUAGE":
                self.language = val
            elif com == "YEAR":
                self.year = int(val)
            elif com == "CREATOR":
                self.creator = val
            elif com == "SOURCE":
                self.source = val
            elif re.match(r'DUETSINGER\d+', com):
                singer_no = re.match(r'DUETSINGER(\d+)', com).group(1)
                self.duetsingers[int(singer_no)] = val
                self.is_duet = True
        elif line[0] == "P":
            part_data = []
            #The actual lyric data will follow, discard this for now
            line = self.next_line()
            while line and line[0] != "P" and line[0] != "E":
                part_data.append(line)
                line = self.next_line()
            #Recurse for the next section
            self.parse_line(line)
        elif line[0] == ":" or line[0] == "-" or line[0] == "*" or line[0] == "F":
            #This is a standard lyrics line
            part_data = []
            while line and line[0] != "P" and line[0] != "E":
                part_data.append(line)
                line = self.next_line()
            #Recurse for the next section
            self.parse_line(line)
        elif str.strip(line) == "E":
            #File is finished
            return
        elif not line.rstrip("\n\r\0 "):
            #Empty line
            return
        else:
            logging.warning("Error in file " + self.filename)
            logging.warning("Unexpected character found at the start of the following line: '" + str.strip(line) + ". Ignoring line and continuing...")

    def next_line(self):
        try:
            return next(self.textfile)
        except StopIteration:
            return None
