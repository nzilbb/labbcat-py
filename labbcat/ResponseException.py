class ResponseException(Exception):
    """ Any method that creates a server request can raise this exception if an error occurs.
    
    This has one attribute, ``response``, which is a Response object representing the full 
    response from the server, from which error messages etc. can be obtained.    
    """

    response = None
    
    def __init__(self, response):        
        self.response = response        
        message = ""
        if response.errors != None and len(response.errors) > 0:
            for error in response.errors:
                if len(message) > 0:
                    message += "\n"
                message += error
        else:
            if response.code > 0:
                message = "Response code " + response.code;
            else:
                if response.httpStatus > 0:
                    message = "HTTP status " + response.httpStatus
        super().__init__(message)
        
