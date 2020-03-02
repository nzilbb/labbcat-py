import requests
from labbcat.ResponseException import ResponseException

class Response:
    """ Standard LaBB-CAT response object.

    :Attributes:

    - ``model`` - The model or result returned if any.
    - ``httpStatus`` - The HTTP status code, or -1 if not known.
    - ``title`` - The title reqturned by the server.
    - ``version`` - The server version. 
    - ``code`` - The numeric request code (0 or 1 means no error).
    - ``errors`` - Errors returned.
    - ``messages`` - Messages returned.
    - ``text`` - The full plain text of the HTTP response.
    """

    httpStatus = -1
    title = ""
    version = ""
    code = -1
    errors = []
    messages = []
    model = None
    text = None
    
    verbose = False

    def __init__(self, resp, verbose=False):
        self.verbose = verbose
        self.httpStatus = resp.status_code
        self.text = resp.text

        try:
            json = resp.json()
            if "title" in json:
                if self.verbose: print("title " + json["title"])
                self.title = json["title"]
            if "version" in json:
                if self.verbose: print("version " + json["version"])
                self.version = json["version"]
            if "code" in json:
                if self.verbose: print("code " + str(json["code"]))
                self.code = json["code"]
            if "messages" in json:
                if self.verbose:
                    for m in json["messages"]:
                        print("message " + m)
                self.messages = json["messages"]
            if "errors" in json:
                if self.verbose:
                    for m in json["errors"]:
                        print("error " + m)
                self.errors = json["errors"]
            if self.verbose: print("model " + str(json["model"]))
            if "model" in json:
                if self.verbose: print("model " + str(json["model"]))
                self.model = json["model"]
        except Exception as x:
            if self.verbose: print("EXCEPTION " + x)
            errors = [ "Response not JSON:" + self.text ]

    def checkForErrors(self):
        """ Convenience method for checking whether the response any errors. 

        If so, a corresponding ResponseException will be thrown.
        """
        if self.errors != None and len(self.errors) > 0:
            raise ResponseException(self)
        if self.code > 0:
            raise ResponseException(self)
        if self.httpStatus > 0 and self.httpStatus != requests.codes.ok:
            raise ResponseException(self)
            
