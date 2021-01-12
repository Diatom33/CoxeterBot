from pywikibot import family

class Family(family.Family):
    name = 'polytopewiki'
    langs = {
        'en': 'polytope.miraheze.org',
    }
    
    def protocol(self, code):
        return 'HTTPS'