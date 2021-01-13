from src.py.exceptions import RedirectCycle
from src.py.template import Template

from mwclient import Site
from mwclient.page import Page

# A wrapper for mwclient.
class Wiki:
    # Class initializer.
    def __init__(self):
        self.username = 'OfficialURL@CoxeterBot'
        self.userAgent = 'CoxeterBot (eric.ivan.hdz@gmail.com)'

        self.URL = "polytope.miraheze.org/"
        self.fullURL = 'https://' + self.URL + 'wiki/'

        self.site = Site(self.URL, clients_useragent = self.userAgent)

        self.site.login(self.username, open("src/txt/WIKI_PW.txt", "r").read())


    keywords = [
        {"list": ['dimension', 'dimensions', 'dim', 'rank'], "format": 'The number of **dimensions** of {shape} is: {result}'},
        {"list": ['type'], "fieldName": 'type'},
        {"list": ['space'], "alt": 'spherical'},

        {"list": ['acronym', 'obsa', 'bsa', 'ubsa']},

        {"list": ['csymbol', 'cox', 'coxeter', 'cd']},
        {"list": ['schlafli', 'schläfli']},
        {"list": ['symmetry']},

        {"list": ['army']},
        {"list": ['reg', 'regiment']},
        {"list": ['company']},

        {"list": ['circum', 'circumradius', 'rad', 'radius']}
    ]

    # Gets all fields from a page's Infobox.
    def info(self, title):
        page = self.Page(title, redirect = True)
        fields = Template(page.text()).getFields()
        result = ""

        for field, value in fields.items():
            result += f"**{field}**: {value}"

        return result

    # Gets a field matching an element from a list from a page's Infobox.
    def __get(self, text, keyword):
        if hasattr(keyword, "alt"):
            alt = keyword["alt"]
        else:
            alt = None

        return Template(text).getField(keyword["list"]) or alt

    # Returns a Page object with a given title.
    # If redirect, goes through the whole redirect chain.
    def Page(self, title, redirect = False):
        page = Page(self.site, title)
        if redirect:
            page = self.resolveRedirect(page)

        return page

    # Gets the URL of a page.
    def pageURL(self, page):
        return self.titleToURL(page.name)

    # Gets the URL of a page from its title.
    def titleToURL(self, title):
        return self.fullURL + title.translate({32: '_'})

    # Searches all articles with a given word in its title.
    def search(self, key):
        # Sorts by length first, then alphabetically.
        def sortFun(x):
            x = x.get('title')
            return (len(x), x)

        return sorted(self.site.search(search = key), key = sortFun)

    # From a page, which might exist or not, goes through the entire redirect chain.
    # Fixes any double redirects it comes across.
    # Throws an exception on a cyclic redirect.
    def resolveRedirect(self, page):
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
    def redirect(self, originPage, targetPage):
        originPage.edit(f"#REDIRECT [[{targetPage.name}]]", minor = False, bot = True, section = None)
       