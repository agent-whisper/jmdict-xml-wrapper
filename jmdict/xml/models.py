import io
from abc import ABC, abstractmethod
from typing import List, Dict

from bs4 import BeautifulSoup
from bs4.element import Tag


class Entities(object):
    def __init__(self, xml_content: str):
        self.items = {}


class XmlElementDecorators(object):
    @classmethod
    def verify_tag(cls, decorated):
        """
        Check if the provided bs4.element.Tag name and XmlElement object's tag name matches each other.
        """

        def wrapper(*args, **kwargs):
            key_arg = len(args) == 1 and kwargs.get("item")
            positional = len(args) == 2
            if not (key_arg or positional):
                raise ValueError("Invalid number of arguments.")
            obj = args[0]
            if key_arg:
                tag = kwargs["item"]
                if not tag:
                    raise ValueError(
                        f"Received null input. Check the xml content/tag object for ({obj.tag}) element."
                    )
                if obj.tag != tag.name:
                    raise ValueError(f"Tag name mismatched ({obj.tag} != {tag.name})")
            else:
                tag = args[1]
                if not tag:
                    raise ValueError(
                        f"Received null input. Check the xml content/tag object for ({obj.tag}) element."
                    )
                if obj.tag != tag.name:
                    raise ValueError(f"Tag name mismatched ({obj.tag} != {tag.name})")
            return decorated(*args, **kwargs)

        return wrapper


class MatchValueMixin(object):
    """
    Mixin for checking if the queried value matches the object. Assumes the
    applied object has `value` attribute.
    """

    def match_value(self, value: str, exact: bool = True, case_sensitive: bool = True):
        temp_val = self.value
        if not case_sensitive:
            value = value.lower()
            temp_val = temp_val.lower()
        if exact:
            return value == temp_val
        else:
            return value in temp_val


class XmlElement(ABC):
    """
    Abstract class for JMDict xml elements (tested with Rev 1.0.9).
    """

    version: str = "1.0.9"
    tag: str = None

    @abstractmethod
    def update(self, item: Tag):
        """
        Update the element value with the provided Tag object.
        """
        raise NotImplementedError

    @abstractmethod
    def as_text(self, *args, **kwargs):
        """
        Return a more detailed string-representation of the object.
        """
        raise NotImplementedError

    def print_out(self, *args, **kwargs):
        """
        Print as_text() output on the terminal.
        """
        print(self.as_text(*args, **kwargs))

    def __repr__(self):
        cls_name = type(self).__name__
        return f"<{cls_name}>"


class KanjiElement(MatchValueMixin, XmlElement):
    tag: str = "k_ele"

    def __init__(self, item: Tag = None):
        self.value: str = None
        self.info: List[str] = []
        self.priority: List[str] = []
        if item:
            self.update(item)

    @XmlElementDecorators.verify_tag
    def update(self, item: Tag):
        self.value = item.keb.text
        for info in item.find_all("ke_inf"):
            self.info.append(info.text)
        for priority in item.find_all("ke_pri"):
            self.priority.append(priority.text)

    def as_text(self):
        return f"{self.value} (info: {self.info}, priority: {self.priority})"

    def __str__(self):
        return self.value

    def __repr__(self):
        cls_name = type(self).__name__
        return f"<{cls_name} Value: {self.value}>"


class ReadingElement(MatchValueMixin, XmlElement):
    tag: str = "r_ele"

    def __init__(self, item: Tag = None):
        self.value: str = None
        self.no_kanji: str = None
        self.reading: List[str] = []
        self.info: List[str] = []
        self.priority: List[str] = []
        if item:
            self.update(item)

    @XmlElementDecorators.verify_tag
    def update(self, item: Tag):
        self.value = item.reb.text
        if item.re_nokanji:
            self.no_kanji = item.re_nokanji.text
        for reading in item.find_all("re_restr"):
            self.reading.append(item.re_restr.text)
        for info in item.find_all("re_inf"):
            self.info.append(item.re_inf.text)
        for priority in item.find_all("re_pri"):
            self.priority.append(item.re_pri.text)

    def as_text(self):
        return f"{self.value} (no_kanji: {self.no_kanji}, reading: {self.reading}, info: {self.info}, priority: {self.priority})"

    def __str__(self):
        return self.value

    def __repr__(self):
        cls_name = type(self).__name__
        return f"<{cls_name} Value: {self.value}>"


class LanguageSourceElement(MatchValueMixin, XmlElement):
    tag: str = "lsource"

    def __init__(self, item: Tag = None):
        self.value = None
        self.attrs: Dict = {
            "xml:lang": None,
            "ls_type": None,
            "ls_wasei": None,
        }
        if item:
            self.update(item)

    def as_text(self):
        return f"{self.value} (attrs: {self.attrs})"

    @XmlElementDecorators.verify_tag
    def update(self, item: Tag):
        self.value = item.text
        self.attrs.update(item.attrs)


class GlossaryElement(MatchValueMixin, XmlElement):
    tag: str = "gloss"

    def __init__(self, item: Tag = None):
        self.value = None
        self.attrs: Dict = {
            "xml:lang": None,
            "g_type": None,
            "g_gend": None,
        }
        if item:
            self.update(item)

    @XmlElementDecorators.verify_tag
    def update(self, item: Tag):
        self.attrs.update(item.attrs)
        self.value = item.text

    def as_text(self):
        return f"{self.value} (attrs: {self.attrs})"

    def __str__(self):
        return self.value


class SenseElement(XmlElement):
    tag: str = "sense"

    SUB_ELEMENTS = [
        "kanji",
        "reading",
        "xref",
        "antonym",
        "part_of_speech",
        "field",
        "misc",
        "info",
        "dialect",
        "language_src",
        "glossary",
    ]

    def __init__(self, item: Tag = None):
        self.kanji: List[str] = []
        self.reading: List[str] = []
        self.xref: List[str] = []
        self.antonym: List[str] = []
        self.part_of_speech = []
        self.field: List[str] = []
        self.misc: List[str] = []
        self.info: List[str] = []
        self.dialect: List[str] = []
        self.language_src: List[LanguageSourceElement] = []
        self.glossary: List[GlossaryElement] = []
        if item:
            self.update(item)

    @XmlElementDecorators.verify_tag
    def update(self, item: Tag):
        for kanji in item.find_all("stagk"):
            self.kanji.append(kanji.text)
        for reading in item.find_all("stagr"):
            self.reading.append(reading.text)
        for xref in item.find_all("xref"):
            self.xref.append(xref.text)
        for antonym in item.find_all("ant"):
            self.antonym.append(antonym.text)
        for pos in item.find_all("pos"):
            self.part_of_speech.append(pos.text)
        for field in item.find_all("field"):
            self.field.append(field.text)
        for misc in item.find_all("misc"):
            self.misc.append(misc.text)
        for info in item.find_all("s_inf"):
            self.info.append(info.text)
        for dialect in item.find_all("dial"):
            self.dialect.append(dialect.text)
        for lsource in item.find_all(LanguageSourceElement.tag):
            self.language_src.append(LanguageSourceElement(lsource))
        for glossary in item.find_all(GlossaryElement.tag):
            self.glossary.append(GlossaryElement(glossary))

    def as_text(
        self,
        sub_elements: List[str] = None,
        buffer: io.StringIO = None,
        indent_level: int = 0,
    ):
        indentation = lambda x: "\t" * x
        if not buffer:
            buffer = io.StringIO()
        for sub_el in sub_elements:
            if hasattr(self, sub_el):
                buffer.write(f"{indentation(indent_level)}.{sub_el}:\n")
                for val in getattr(self, sub_el, []):
                    if issubclass(type(val), XmlElement):
                        buffer.write(
                            f"{indentation(indent_level+1)}- {val.as_text()}\n"
                        )
                    else:
                        buffer.write(f"{indentation(indent_level+1)}- {val}\n")
        return buffer.getvalue()

    def match_glossary(self, value, *args, **kwargs):
        """
        Match against glossary fields.
        """
        for glos in self.glossary:
            if glos.match_value(value, *args, **kwargs):
                return True
        return False

    def __repr__(self):
        cls_name = type(self).__name__
        return f"<{cls_name} Glossary: {len(self.glossary)}>"


class EntryElement(XmlElement):
    tag = "entry"

    def __init__(self, item: Tag = None):
        self.sequence: int = None
        self.kanji: List[KanjiElement] = []
        self.reading: List[ReadingElement] = []
        self.sense: List[SenseElement] = []
        if item:
            self.update(item)

    @XmlElementDecorators.verify_tag
    def update(self, item: Tag):
        if item.ent_seq:
            self.sequence = int(item.ent_seq.text)
        for kanji in item.find_all(KanjiElement.tag):
            self.kanji.append(KanjiElement(kanji))
        for reading in item.find_all(ReadingElement.tag):
            self.reading.append(ReadingElement(reading))
        for sense in item.find_all(SenseElement.tag):
            self.sense.append(SenseElement(sense))

    def as_text(self):
        result = io.StringIO()
        result.write(f"Entry ({self.sequence}):\n")
        result.write("\t> Kanji(s):\n")
        for kanji in self.kanji:
            result.write(f"\t\t- {kanji.as_text()}\n")
        result.write("\n")

        result.write("\t> Reading(s):\n")
        for reading in self.reading:
            result.write(f"\t\t- {reading.as_text()}\n")
        result.write("\n")

        result.write("\t> Sense(s):\n")
        for i, sense in enumerate(self.sense):
            result.write(f"\t--- {i+1} ---\n")
            sense.as_text(
                sub_elements=SenseElement.SUB_ELEMENTS, buffer=result, indent_level=2
            )
        return result.getvalue()

    def match_kanji(self, value, *args, **kwargs):
        """
        Match against glossary fields.
        """
        for kanji in self.kanji:
            if kanji.match_value(value, *args, **kwargs):
                return True
        return False

    def match_reading(self, value, *args, **kwargs):
        """
        Match against glossary fields.
        """
        for reading in self.reading:
            if reading.match_value(value, *args, **kwargs):
                return True
        return False

    def match_glossary(self, value, *args, **kwargs):
        """
        Match against glossary fields.
        """
        for sense in self.sense:
            if sense.match_glossary(value, *args, **kwargs):
                return True
        return False

    def match(
        self,
        kanji: str = None,
        reading: str = None,
        glossary: str = None,
    ):
        if not (kanji or reading or glossary):
            return ValueError("Query input required.")
        if kanji:
            if self.match_kanji(kanji, exact=False, case_sensitive=False):
                return True
        if reading:
            if self.match_reading(reading, exact=False, case_sensitive=False):
                return True
        if glossary:
            if self.match_glossary(glossary, exact=False, case_sensitive=False):
                return True
        return False

    def __repr__(self):
        cls_name = type(self).__name__
        return f"<{cls_name} Sequence: {self.sequence}, Kanji: {len(self.kanji)}, Reading: {len(self.reading)}, Sense: {len(self.sense)}>"


class JMDict(object):
    """
    JMDict-entries container. This class is analogous to Django's Queryset.
    """

    tag: str = "jmdict"

    @classmethod
    def _read_xml_soup(cls, item: BeautifulSoup):
        if item is None:
            raise ValueError("Received None value as input.")
        entries = []
        for entry in item.find_all(EntryElement.tag):
            entries.append(EntryElement(entry))
        return entries

    @classmethod
    def from_soup(cls, soup: BeautifulSoup):
        entries = cls._read_xml_soup(soup)
        return cls(entries)

    @classmethod
    def from_xml(cls, xml_dir: str):
        """
        Create a JMDict instance by reading a JMDict-XML. This will load all
        entries inside the file.
        """
        with open(xml_dir, "r") as xml:
            content = BeautifulSoup(xml, "lxml")
            entries = cls._read_xml_soup(content.jmdict)
            return cls(entries)

    def __init__(self, entries: List[EntryElement] = []):
        self.entries: List[EntryElement] = entries

    def __getitem__(self, item):
        return self.entries[item]

    def as_text(self, start: int = None, end: int = None, buffer: io.StringIO = None):
        """
        Display entries contained in this instance as a formatted string.
        """
        if (start is not None and start >= len(self.entries)) or (
            end is not None and end > len(self.entries)
        ):
            raise IndexError("Index out of range.")

        if not buffer:
            buffer = io.StringIO()

        if start is not None and end is not None:
            entries = self.entries[start:end]
        elif start and end is None:
            entries = self.entries[start:]
        elif start is None and end:
            entries = self.entries[:end]
        else:
            entries = self.entries
        for entry in entries:
            buffer.write(entry.as_text())
        return buffer.getvalue()

    def print_out(self, *args, **kwargs):
        print(self.as_text(*args, **kwargs))

    def count(self):
        return len(self.entries)

    def filter(
        self,
        sequence: int = None,
        kanji: str = None,
        reading: str = None,
        glossary: str = None,
        limit: int = None,
    ):
        """
        Filter entries contained in this instance and return them as a new
        JMDict instance.
        """
        if not (kanji or reading or glossary):
            return ValueError("Query input required.")
        results = []
        i = 0
        if limit is None or limit < 0:
            limit = len(self.entries)
        while i < len(self.entries) and len(results) <= limit:
            entry = self.entries[i]
            if entry.match(kanji=kanji, reading=reading, glossary=glossary):
                results.append(entry)
            i += 1
        return JMDict(results)

    def __repr__(self):
        cls_name = type(self).__name__
        return f"<{cls_name} Entries: {len(self.entries)}>"
