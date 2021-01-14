from src.py.exceptions import RedirectCycle, TemplateError
from src.py import parser as parser
from mwclient import Site
from mwclient.page import Page
from mwclient.errors import AssertUserFailedError

import mwparserfromhell

from typing import Dict

# A wrapper for mwclient.
class Wiki:
    fullURL = "https://polytope.miraheze.org/wiki/"

    # Class initializer.
    def __init__(self) -> None:
        self.username = 'OfficialURL@CoxeterBot'
        self.userAgent = 'CoxeterBot (eric.ivan.hdz@gmail.com)'

        self.fullURL = Wiki.fullURL
        self.URL = Wiki.fullURL[8:-5]

        self.site = Site(self.URL, clients_useragent = self.userAgent)
        self.login()

    # Does not store the password variable, which may either be good for security, or be stupid.
    def login(self) -> None:
        self.site.login(self.username, open("src/txt/WIKI_PW.txt", "r").read())

    # Gets all fields from a page's Infobox.
    def getFields(self, page: Page) -> Dict[str, str]:
        wikicode = mwparserfromhell.parse(page.text())

        for template in wikicode.filter_templates():
            if template.name.matches("Infobox polytope"):
                return parser.parse( # type: ignore
                    template.params
                )

        raise TemplateError("Infobox polytope not found.")

    # Gets a single field from a page's Infobox.
    def getField(self, title: str, field: str) -> str:
        return self.getFields(title)[field]

    # Returns a Page object with a given title.
    # If redirect, goes through the whole redirect chain.
    def page(self, title: str, redirect: bool = False) -> Page:
        page = Page(self.site, title)
        if redirect:
            page = self.resolveRedirect(page)

        return page

    # Gets the URL of a page.
    def pageURL(self, page: Page) -> str:
        return self.titleToURL(page.name)

    # Gets the URL of a page from its title.
    def titleToURL(self, title: str) -> str:
        return self.fullURL + title.translate({32: '_'})

    # Searches all articles with a given word in its title.
    def search(self, key: str):
        # Sorts by length first, then alphabetically.
        def sortFun(x):
            x = x.get('title')
            return (len(x), x)

        return sorted(self.site.search(search = key), key = sortFun)

    # From a page, which might exist or not, goes through the entire redirect chain.
    # Fixes any double redirects it comes across.
    # Throws an exception on a cyclic redirect.
    def resolveRedirect(self, page: Page) -> Page:
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
            self.redirect(link, redirectList[-1])

        return page

    # Redirects a page to another.
    # Does not perform any checks to see whether the pages exist, etc.
    MAX_TRIES = 3
    def redirect(self, originPage, targetPage, tries = 0) -> None:
        try:
            originPage.edit(f"#REDIRECT [[{targetPage.name}]]", minor = False, bot = True, section = None)
        except AssertUserFailedError:
            self.login()

            if tries < Wiki.MAX_TRIES:
                self.redirect(originPage, targetPage, tries + 1)
            else:
                raise ConnectionRefusedError("Could not connect to the Polytope Wiki.")