import src.py.wiki as Wiki

# ID of Wiki Contributor role.
ROLE_ID = "<@&699404888127569981>"

help = "Shows in-depth help for a given command."

cd = (
    "Renders a [Coxeter–Dynkin Diagram](https://polytope.miraheze.org/wiki/Coxeter_diagram), "
    "based on [Richard Klitzing's notation]"
    "(https://bendwavy.org/klitzing/explain/dynkin-notation.htm)."
)

wiki = (
    "Searches for a given article within the "
    f"[Polytope Wiki]({Wiki.fullURL}). Resolves redirects automatically."
)

redirect = (
    "Automatically creates a redirect between two articles on the wiki. "
    "Resolves existing redirects automatically. "
    f"Can only be used by {ROLE_ID}."
)

search = "Searches for an article on the wiki."

info = "Gets a shape's info from its infobox on the wiki."

space = "Returns the dimension and curvature of a CD."
