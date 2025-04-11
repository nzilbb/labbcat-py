def expressionFromAttributeValue(attribute, values, negate=False):
    """ Generates a query expression for matching a transcript/participant attribute.
    
    This function generates a query expression fragment which can be passed as
    the expression parameter of
    `getMatchingTranscriptIds <#labbcat.LabbcatView.getMatchingTranscriptIds>`_ or
    `getMatchingParticipantIds <#labbcat.LabbcatView.getMatchingParticipantIds>`_ etc.
    using a list ofpossible values for a given transcript/participant attribute. 
    
    The attribute defined by 'attribute' is expected to have exactly one value. If
    it may have multiple values, use
    `expressionFromAttributeValues() <#labbcat.expressionFromAttributeValues>`_
    instead.

    :param attribute: The transcript/participant attribute to filter by.
    :type attribute: str
    
    :param values: A list of possible values for attribute, or a single value.
    :type values: list or str
    
    :param negate: Whether to match the given values (False),
                   or everything *except* the given values (True).
    :type negate: boolean
    
    :returns: A query expression which can be passed as the *expression* parameter of
              `countMatchingParticipantIds() <#labbcat.LabbcatView.countMatchingParticipantIds>`_
              `getMatchingParticipantIds() <#labbcat.LabbcatView.getMatchingParticipantIds>`_
              `countMatchingTranscriptIds() <#labbcat.LabbcatView.countMatchingTranscriptIds>`_
              `getMatchingTranscriptIds() <#labbcat.LabbcatView.getMatchingTranscriptIds>`_
              or
              `getTranscriptAttributes() <#labbcat.LabbcatView.getTranscriptAttributes>`_
    :rtype: str
    """
    if isinstance(values, str):
        values = [ values ]
    values = list(map(lambda v: "'"+v.replace("'","\\'")+"'", values))
    valuesList = ",".join(values)
    attribute = attribute.replace("'","\\'")
    if negate:
        prefix = "!"
        operator = " <> "
    else:
        prefix = ""
        operator = " == "
    if len(values) == 1:
        return "first('"+attribute+"').label"+operator+valuesList;
    else:
        return prefix+"["+valuesList+"].includes(first('"+attribute+"').label)"

def expressionFromAttributeValues(attribute, values, negate=False):
    """ Generates a query expression for matching a transcript/participant attribute.
    
    This function generates a query expression fragment which can be passed as
    the expression parameter of
    `getMatchingTranscriptIds <#labbcat.LabbcatView.getMatchingTranscriptIds>`_ or
    `getMatchingParticipantIds <#labbcat.LabbcatView.getMatchingParticipantIds>`_ etc.
    using a list of possible values for a given transcript/participant attribute. 
    
    The attribute defined by 'attribute' is expected to have possibly more than one value. If
    it can only have one value, use
    `expressionFromAttributeValue() <#labbcat.expressionFromAttributeValue>`_
    instead.

    :param attribute: The transcript/participant attribute to filter by.
    :type attribute: str
    
    :param values: A list of possible values for attribute, or a single value.
    :type values: list or str
    
    :param negate: Whether to match the given values (False),
                   or everything *except* the given values (True).
    :type negate: boolean
    
    :returns: A query expression which can be passed as the *expression* parameter of
              `countMatchingParticipantIds() <#labbcat.LabbcatView.countMatchingParticipantIds>`_
              `getMatchingParticipantIds() <#labbcat.LabbcatView.getMatchingParticipantIds>`_
              `countMatchingTranscriptIds() <#labbcat.LabbcatView.countMatchingTranscriptIds>`_
              `getMatchingTranscriptIds() <#labbcat.LabbcatView.getMatchingTranscriptIds>`_
              or
              `getTranscriptAttributes() <#labbcat.LabbcatView.getTranscriptAttributes>`_
    :rtype: str
    """
    if isinstance(values, str):
        values = [ values ]
    values = list(map(lambda v: "'"+v.replace("'","\\'")+"'", values))
    valuesList = ",".join(values)
    attribute = attribute.replace("'","\\'")
    if negate:
        prefix = "!"
    else:
        prefix = ""
    if len(values) == 1:
        return prefix+"labels('"+attribute+"').includes("+valuesList+")";
    else:
        return prefix+"["+valuesList+"].includesAny(labels('"+attribute+"'))"

def expressionFromIds(ids, negate=False):
    """ Generates a query expression for matching transcripts or participants by ID.
    
    This function generates a query expression fragment which can be passed as
    the expression parameter of
    `getTranscriptAttributes <#labbcat.LabbcatView.getTranscriptAttributes>`_
    etc. using a list of IDs. 
        
    :param ids: A list of IDs, or a single value.
    :type ids: list or str
    
    :param negate: Whether to match the given values (False),
                   or everything *except* the given values (True).
    :type negate: boolean
    
    :returns: A query expression which can be passed as the *expression* parameter of
              `countMatchingParticipantIds() <#labbcat.LabbcatView.countMatchingParticipantIds>`_
              `getMatchingParticipantIds() <#labbcat.LabbcatView.getMatchingParticipantIds>`_
              `countMatchingTranscriptIds() <#labbcat.LabbcatView.countMatchingTranscriptIds>`_
              `getMatchingTranscriptIds() <#labbcat.LabbcatView.getMatchingTranscriptIds>`_
              or
              `getTranscriptAttributes() <#labbcat.LabbcatView.getTranscriptAttributes>`_
    :rtype: str
    """
    if isinstance(ids, str):
        ids = [ ids ]
    ids = list(map(lambda v: "'"+v.replace("'","\\'")+"'", ids))
    idsList = ",".join(ids)
    if negate:
        prefix = "!"
        operator = " <> "
    else:
        prefix = ""
        operator = " == "
    if len(ids) == 1:
        return "id"+operator+idsList;
    else:
        return prefix+"["+idsList+"].includes(id)"

def expressionFromTranscriptTypes(transcriptTypes, negate=False):
    """ Generates a transcript query expression for matching transcripts by type.
    
    This function generates a query expression fragment which can be passed as
    the expression parameter of 
    `getTranscriptAttributes <#labbcat.LabbcatView.getTranscriptAttributes>`_
    or `getMatchingTranscriptIds <#labbcat.LabbcatView.getMatchingTranscriptIds>`_
    etc. using a list of transcript types. 
        
    :param transcriptTypes: A list of transcript types, or a single transcript type.
    :type transcriptTypes: list or str
    
    :param negate: Whether to match the given values (False),
                   or everything *except* the given values (True).
    :type negate: boolean
    
    :returns: A query expression which can be passed as the *expression* parameter of
              `getMatchingTranscriptIds() <#labbcat.LabbcatView.getMatchingTranscriptIds>`_
              or
              `getTranscriptAttributes() <#labbcat.LabbcatView.getTranscriptAttributes>`_
    :rtype: str
    """
    return expressionFromAttributeValue("transcript_type", transcriptTypes, negate)

def expressionFromCorpora(corpora, negate=False):
    """ Generates a transcript query expression for matching transcripts/participants by corpus.
    
    This function generates a query expression fragment which can be passed as
    the expression parameter of 
    `getTranscriptAttributes <#labbcat.LabbcatView.getTranscriptAttributes>`_
    or `getMatchingTranscriptIds <#labbcat.LabbcatView.getMatchingTranscriptIds>`_
    etc. using a list of transcript types. 
        
    :param corpora: A list of corpus names, or a single corpus name.
    :type corpora: list or str
    
    :param negate: Whether to match the given values (False),
                   or everything *except* the given values (True).
    :type negate: boolean
    
    :returns: A query expression which can be passed as the *expression* parameter of
              `getMatchingTranscriptIds() <#labbcat.LabbcatView.getMatchingTranscriptIds>`_
              or
              `getTranscriptAttributes() <#labbcat.LabbcatView.getTranscriptAttributes>`_ etc.
    :rtype: str
    """
    return expressionFromAttributeValues("corpus", corpora, negate)
