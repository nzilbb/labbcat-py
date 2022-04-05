class ResponseException(Exception):
    """ Any method that creates a server request can raise this exception if an error occurs.
    
    This has one attribute, ``response``, which is a Response object representing the full 
    response from the server, from which error messages etc. can be obtained.    
    """

    response = None
    message = None
    
    def __init__(self, response):
        if isinstance(response, str):
            self.message = response
        else: # response is a Response object
            self.response = response        
            self.message = ""
            if response.errors != None and len(response.errors) > 0:
                for error in response.errors:
                    if len(self.message) > 0:
                        self.message += "\n"
                    self.message += error
            else:
                if response.code > 0:
                    self.message = "Response code " + str(response.code);
                else:
                    if response.httpStatus > 0:
                        self.message = "HTTP status " + str(response.httpStatus) + " : " + response.text
        super().__init__(self.message)
        
