from src.py.exceptions import RedirectCycle, TemplateError
from mwclient import Site
from mwclient.page import Page
from mwclient.errors import AssertUserFailedError

import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode, Tag, Template, Wikilink

from typing import Callable, Dict, List, Tuple, Optional, Union

# A wrapper for mwclient.
username = 'OfficialURL@CoxeterBot'
userAgent = 'CoxeterBot (eric.ivan.hdz@gmail.com)'

URL = 'polytope.miraheze.org'
fullURL = "https://polytope.miraheze.org/wiki/"

site: Site

# Does not store the password variable, which may either be good for security, or be stupid.
def login() -> None:
    global site
    site = Site(URL, clients_useragent = userAgent)
    site.login(username, open("src/txt/WIKI_PW.txt", "r").read())

# Gets all fields from a page's Infobox.
def getUnparsedFields(page: Page) -> List[Wikicode]:
    if not page.exists:
        raise TemplateError(f"The requested page {page.name} does not exist.")

    wikicode = mwparserfromhell.parse(page.text())

    for template in wikicode.filter_templates():
        if template.name.matches("Infobox polytope"):
            return template.params

    raise TemplateError("Infobox polytope not found.")

def getFields(page: Page) -> Dict[str, str]:
    return parse(getUnparsedFields(page))

# Gets a single field from a page's Infobox.
def getField(page: Page, wikiField: str) -> Tuple[str, str]:
    if not page.exists:
        raise TemplateError(f"The requested page {page.name} does not exist.")

    fieldName = getFieldName(wikiField)

    if fieldName is not None:
        for field in getUnparsedFields(page):
            if getFieldName(field.name) == fieldName:
                return parseItem(field) # type: ignore

    raise TemplateError(f"Field {wikiField} not found.")

# Returns a Page object with a given title.
# If redirect, goes through the whole redirect chain.
def page(title: str, redirect: bool = False) -> Page:
    page = Page(site, title)
    if redirect:
        page = resolveRedirect(page)

    return page

# Gets the URL of a page.
def pageToURL(page: Page) -> str:
    return titleToURL(page.name)

# Gets the URL of a page from its title.
def titleToURL(title: str) -> str:
    return fullURL + title.translate({32: '_'})

# Searches all articles with a given word in its title.
def search(key: str):
    # Sorts by length first, then alphabetically.
    def sortFun(x):
        x = x.get('title')
        return (len(x), x)

    return sorted(site.search(search = key), key = sortFun)

# From a page, which might exist or not, goes through the entire redirect chain.
# Fixes any double redirects it comes across.
# Throws an exception on a cyclic redirect.
def resolveRedirect(page: Page) -> Page:
    # If the page doesn't exist, returns itself.
    if not page.exists:
        return page

    redirectList = [] # Each page in the redirect chain.
    redirectListNames = [] # Each page title in the redirect chain.
    while page is not None and page.exists:
        if page.name in redirectListNames:
            raise RedirectCycle("Redirect cycle found.")

        redirectList.append(page)
        redirectListNames.append(page.name)

        page = page.redirects_to()

    if page is None:
        page = redirectList[-1]

    for link in redirectList[:-2]:
        redirect(link, redirectList[-1])

    return page

# Redirects a page to another.
# Does not perform any checks to see whether the pages exist, etc.
MAX_TRIES = 3
def redirect(originPage: Page, targetPage: Page, tries: int = 0) -> None:
    try:
        originPage.edit(f"#REDIRECT [[{targetPage.name}]]", minor = False, bot = True, section = None)
    except AssertUserFailedError:
        login()

        if tries < MAX_TRIES:
            redirect(originPage, targetPage, tries + 1)
        else:
            raise ConnectionRefusedError("Could not connect to the Polytope Wiki.")

def parseItem(param: Wikicode) -> Union[Tuple[str, str], Tuple[None, None]]:
    name: Wikicode = param.name
    code: Wikicode = param.value

    # Compares the param name to the list of parsers.
    newName = getFieldName(str(name))
    if newName is None:
        return None, None

    if newName in parsers:
        newCode = (parsers[newName])(code)
    else:
        newCode = code

    return newName, stringFormat(newCode)

def parse(params: List[Wikicode]) -> Dict[str, str]:
    # A dictionary of parsed parameter names and values.
    parseFieldList: Dict[str, str] = {}

    # For each of the template's parameters:
    for param in params:       
        newName, newCode = parseItem(param)
        
        # Adds the new name and new value to the dictionary.
        if newName is not None and newCode is not None:
            parseFieldList[newName] = newCode

    # Adds default values for missing fields.
    return addDefaults(parseFieldList)

# Translates a wiki infobox name to a human-readable field name.
# We call the former "wiki fields", the latter simply "fields".
def getFieldName(wikiField: str) -> Optional[str]:
    wikiField = wikiField.lower().strip()

    if wikiField in fieldTranslator:
        return fieldTranslator[wikiField]
    return None

# Applies standard formating to turn a Wikicode object into a string.
# We should remove italics and bold, but preserve links.
def stringFormat(code: Wikicode) -> str:
    # Parses italics and bold.
    for innerCode in code.filter():
        if isinstance(innerCode, Tag):
            if innerCode.wiki_markup == "''":
                code.replace(innerCode, f"*{innerCode.contents}*")
            elif innerCode.wiki_markup == "'''":
                code.replace(innerCode, f"**{innerCode.contents}**")
            elif innerCode.wiki_markup == '<nowiki>':
                code.replace(innerCode, innerCode.contents)

        elif isinstance(innerCode, Template):
            if innerCode.name.matches("!"):
                code.replace(innerCode, '|')

        elif isinstance(innerCode, Wikilink):
            linkPage = page(str(innerCode.title), redirect = True)
            link = innerCode.text or innerCode.title

            if linkPage.exists:
                link = f'({link})[{pageToURL(linkPage)}]'

            code.replace(innerCode, link)

    return str(code).strip()

# Cleans up a CD.
def cd(code: Wikicode) -> Wikicode:
    # Removes all graphical CDs.
    for template in code.filter_templates():
        if template.name.matches(["CDD", "Coxeter-Dynkin Diagram"]):
            code.remove(template)

    # If the CDs were parenthesized, empty parentheses () will remain, so we remove them.
    try:
        code.replace('()', '')
    # The code throws an error if it doesn't find any matches, but we don't care.
    except ValueError:
        pass

    return code

# Cleans up a field by simply adding uppercase.
def uppercase(code: Wikicode) -> Wikicode:
    code.name = str(code).title()
    return code

def addDefaults(fieldList: Dict[str, str]) -> Dict[str, str]:
    # First removes empty attributes.
    for name, value in tuple(fieldList.items()):
        if value == '':
            del fieldList[name]

    for name, replace in defaults.items():
        if name not in fieldList:
            fieldList[name] = replace

    return fieldList

defaults: Dict[str, str] = {
    'Space': 'Spherical'
}

fieldTranslator: Dict[str, str] = {
    'dimension': "Dimensions",
    'dim': "Dimensions",
    'dimensions': "Dimensions",
    'rank': "Dimensions",
    'type': "Type",
    'space': "Space",
    'acronym': "Bowers style acronym",
    'obsa': "Bowers style acronym",
    'bsa': "Bowers style acronym",
    'ubsa': "Bowers style acronym",

    'csymbol': 'Coxeter diagram',
    'cox': 'Coxeter diagram',
    'coxeter': 'Coxeter diagram',
    'cd': 'Coxeter diagram',
    'cdd': 'Coxeter diagram',
    'schlafli': 'Schläfli symbol',
    'schläfli': 'Schläfli symbol',
    'taper': 'Tapertopic notation',
    'tapertopic': 'Tapertopic notation',
    'bracket': 'Bracket notation',
    'symmetry': 'Symmetry',
    'army': 'Army',
    'reg': 'Regiment',
    'regiment': 'Regiment',
    'company': 'Company',

    'circumradius': 'Circumradius',
    'radius': 'Circumradius',
    'circum': 'Circumradius',
    'rad': 'Circumradius',
    'cr': 'Circumradius',

    'pieces': 'Number of pieces',
    'loc': 'Level of complexity',
    'convex': 'Convex',
    'conv': 'Convex',
    'orientable': 'Orientable',
    'orient': 'Orientable',
    'nature': 'Nature',
    'nat': 'Nature',

    'dual': 'Dual',
    'conjugate': 'Conjugate',
    'conj': 'Conjugate'
}

parsers: Dict[str, Callable[[Wikicode], Wikicode]] = {
    'Coxeter diagram': cd,
    'Convex': uppercase,
    'Orientable': uppercase,
    'Nature': uppercase
}