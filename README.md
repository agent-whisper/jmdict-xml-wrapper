# jmdict-xml-wrapper
Python wrapper/interface for JMDict-XML file.

## Goal
Provide a Python interface which allow easier direct-interaction with the JMDict-XML file. The interface can then be extended to be used in another application.
The implementation uses BeautifulSoup library as its core.

My personal goals for this repository are to understand the JMDict-XML itself and to improve my coding skill in general, so any constructive feedbacks are appreciated :)

## Installation
Currently only available on Github.

1. Clone the repository.
2. Install the requirements by either using [Poetry](https://python-poetry.org/) or requirements.txt.
3. Download and extract the [JMDict-XML](http://www.edrdg.org/jmdict/edict_doc.html) file anywhere in the system.

## How to use
The following are the 3 main classes of interest: JMDict, EntryElement, and JMDictEngine.

### JMDict & EntryElement
EntryElement contains the data of a single word in the JMDict-XML and the JMDict class acts as a container for the EntryElement.
JMDict is akin to Django's Queryset object and can be instantiated in 3 ways:

1. `JMDict.from_xml("path/to/JMDict.xml"`.
2. `JMDict.from_soup(xml_soup)`.
3. `JMDict(list_of_EntryElement)`.

The JMDict entries can then be interacted with the following methods:

```
from jmdict.xml import JMDict

jmdict = JMDict.from_xml("path/to/JMDict.xml")
jmdict.count() # Outputs the number of entries inside the instance.
jmdict[0] # Retrieve the first entry.
jmdict.print_out() # Print the entries inside the JMDict onto the terminal.
filtered_jmdict = jmdict.filter(kanji="白", reading="しろ", glossary="white") # Returns a new JMDict instance which contains (loosely) matched entries.
```

### JMDictEngine
JMDictEngine provides search methods to streamline the XML parsing/query and acts as a pseudo search-engine. It's recommended to instantiate this class, and then use it to generate the JMDict instances.

```
# How to use
engine = JMDictEngine("path/to/JMDict.xml")

# These methods will return a JMDict object.
engine.all()
engine.search_kanji("白")
engine.search_reading("しろ")
engine.search_glossary("white")
```

## Caveats
1. The initial loading of the full XML file can be considered to be very slow (~5 minutes).
2. Query speed can also be considered slow since it will be performed sequentially.
3. Currently the search-engine will return loosely-matched entries (i.e. it will search by matching the substrings).
4. Currently only support reading operation on the XML file.

The current implementation is certainly not suited for any serious projects, but maybe useful for POC development or small projects that do not want to use database right away.

## Official Website
1. JMDict/EDict project: http://www.edrdg.org/jmdict/edict_doc.html.
