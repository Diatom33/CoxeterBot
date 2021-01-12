from src.py.exceptions import RedirectCycle

from mwclient import Site
from mwclient.page import Page

# A wrapper for mwclient.
class Wiki:
    def __init__(self):
        self.username = 'OfficialURL@CoxeterBot'
        self.userAgent = 'CoxeterBot (eric.ivan.hdz@gmail.com)'

        self.URL = "polytope.miraheze.org/"
        self.fullURL = 'https://' + self.URL + 'wiki/'

        self.site = Site(self.URL, clients_useragent = self.userAgent)

        self.site.login(self.username, open("src/txt/WIKI_PW.txt", "r").read())

    def Page(self, title):
        return Page(self.site, title)

    def pageURL(self, page):
        return self.titleToURL(page.name)
        
    def search(self, key):
        def sortFun(x):
            x = x.get('title')
            return (len(x), x)
            
        return sorted(self.site.search(search = key), key = sortFun)
        
    def titleToURL(self, title):
        return self.fullURL + title.translate({32: '_'})

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
       