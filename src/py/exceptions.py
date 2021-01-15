from mwclient.errors import MwClientError

# Represents any error that's on the user's fault.
class CDError(Exception):
    pass

# Error thrown when a redirect chain is encountered.
class RedirectCycle(MwClientError):
    pass

# Error when reading a template.
class TemplateError(Exception):
    pass