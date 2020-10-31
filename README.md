# jmdict-xml-wrapper
Python wrapper/interface for JMDict xml file.

This is just an experiment of mine, so don't expect much of it. Might be useful for developing POC or understanding the JMDict xml though.

## Goal
Provide a Python interface which allow easier direct-interaction with the JMDict xml file. The interface can then be extended to be used in another application.
The implementation uses BeautifulSoup library as its core.

## Installation
Currently only available on Github.

1. Clone the repository.
2. Install the requirements by either using [Poetry](https://python-poetry.org/) or requirements.txt.
3. Download and extract the [JMDict xml](http://www.edrdg.org/jmdict/edict_doc.html) file anywhere in the system.

## How to use
The following are the 3 main classes of interest: JMDict, EntryElement, and JMDictEngine.

### JMDict & EntryElement
EntryElement contains the data of a single word in the JMDict xml and the JMDict class acts as a container for the EntryElement.
JMDict object can be instantiated in 3 ways:

1. `JMDict.from_xml("path/to/JMDict.xml"`.
2. `JMDict.from_soup(xml_soup)`.
3. `JMDict(list_of_EntryElement)`.

The JMDict entries can then be interacted with the following methods:

```
from jmdict.xml import JMDict

jmdict = JMDict.from_xml("path/to/JMDict.xml")
jmdict.count() # Outputs the number of entries inside the instance.
jmdict[0] # Retrieve the first entry.
jmdict.entries[0] # Same as previous; JMDict.entries is a Python-list of EntryElement.
jmdict.print_out() # Print the entries inside the JMDict onto the terminal.
filtered_jmdict = jmdict.filter(kanji="白", reading="しろ", glossary="white") # Returns a new JMDict instance which contains (loosely) matched entries; Multiple kwargs will be processed as OR operation.
```

### JMDictEngine
JMDictEngine provides search methods to streamline the xml parsing/query and acts as a pseudo search-engine. The search methods will return a JMDict instance. I recommend to instantiate this class, and then use it to generate the JMDict instances.

```
from jmdict.xml import JMDictEngine

# Create engine object.
engine = JMDictEngine("path/to/JMDict.xml")

# These methods will return a JMDict object.
engine.all()
engine.search_sequence(1474900)
engine.search_kanji("白")
engine.search_reading("しろ")
engine.search_glossary("white")
```

## Caveats/Missing features
1. The initial loading of the full xml file is very slow.
2. Query is obviously slow since it will be performed sequentially.
3. Currently the search-engine will return loosely-matched entries (i.e. it will search by matching the substrings).
4. Currently only support reading operation on the xml file. Adding write/update/delete entry should be possible.
5. Doesn't convert the entity code yet.
6. Might be better to change the parser from bs4 to lxml.
7. Add more robust and complete JMDict methods.

## Official Website
1. JMDict/EDict project: http://www.edrdg.org/jmdict/edict_doc.html.
