import re
from pathlib import Path

from bs4 import BeautifulSoup

from .models import JMDict, EntryElement


class JMDictEngine(object):
    """
    Wrapper for JMDict-XML BeautifulSoup-query which can be used as a pseudo
    search-engine.
    """

    def __init__(self, xml_dir: str):
        self.xml_dir = Path(xml_dir).absolute()
        with open(xml_dir, "r") as xml:
            self.xml_soup = BeautifulSoup(xml.read(), "lxml")

    def all(self):
        return JMDict.from_soup(self.xml_soup)

    def search_sequence(self, value: int):
        results = []
        value = str(value)
        for ent_seq in self.xml_soup.find_all("ent_seq", text=re.compile(value)):
            results.append(EntryElement(ent_seq.find_parent("entry")))
        return JMDict(results)

    def search_kanji(self, value: str):
        results = []
        for keb in self.xml_soup.find_all("keb", text=re.compile(value)):
            results.append(EntryElement(keb.find_parent("entry")))
        return JMDict(results)

    def search_reading(self, value: str):
        results = []
        for reb in self.xml_soup.find_all("reb", text=re.compile(value)):
            results.append(EntryElement(reb.find_parent("entry")))
        return JMDict(results)

    def search_glossary(self, value: str):
        results = []
        for gloss in self.xml_soup.find_all("gloss", text=re.compile(value)):
            results.append(EntryElement(gloss.find_parent("entry")))
        return JMDict(results)

    def __repr__(self):
        return f"<JMDictEngine source: {self.xml_dir}>"
