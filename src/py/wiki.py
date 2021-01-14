from src.py.exceptions import RedirectCycle
from src.py.template import Template
from src.py import parser as parser
from mwclient import Site
from mwclient.page import Page
from mwclient.errors import AssertUserFailedError

from typing import Dict

# A wrapper for mwclient.
class Wiki:
    fullURL = ""

    # Class initializer.
    def __init__(self) -> None:
        self.username = 'OfficialURL@CoxeterBot'
        self.userAgent = 'CoxeterBot (eric.ivan.hdz@gmail.com)'

        self.URL = "polytope.miraheze.org/"
        self.fullURL = 'https://' + self.URL + 'wiki/'
        Wiki.fullURL = self.fullURL

        self.site = Site(self.URL, clients_useragent = self.userAgent)
        self.login()

    # Does not store the password variable, which may either be good for security, or be stupid.
    def login(self) -> None:
        self.site.login(self.username, open("src/txt/WIKI_PW.txt", "r").read())

    # Gets all fields from a page's Infobox.
    def getFields(self, title: str) -> Dict[str, str]:
        return parser.parse( # type: ignore
            Template(
                self.page(title, redirect = True).text()
            ).getFields()
        )

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