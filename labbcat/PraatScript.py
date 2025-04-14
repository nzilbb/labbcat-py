def praatScriptFormants(
        formants = [1,2], samplePoints = [0.5], timeStep = 0.0,
        maxNumberFormants = 5, maxFormant = 5500,
        maxFormantMale = 5000, genderAttribute = 'participant_gender', valueForMale = "M",
        windowLength = 0.025, preemphasisFrom = 50):
    """ 
    Generates a script for extracting formants, for use with 
    `processWithPraat() <#labbcat.LabbcatView.processWithPraat>`_
    
    This function generates a Praat script fragment which can be passed as the praat.script
    parameter of [processWithPraat], in order to extract selected formants.

    :param formants: A list of integers specifying which formants to extract, e.g [1,2]
                     for the first and second formant.
    :type formants: list of int
    
    :param samplePoints: A list of numbers (0 <= samplePoints <= 1) specifying multiple
     points at which to take the measurement. The default is a single point at 0.5 -
     this means one measurement will be taken halfway through the target interval. If,
     for example, you wanted eleven measurements evenly spaced throughout the interval,
     you would specify samplePoints as being
     [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0].
    :type samplePoints: list of float
    
    :param timeStep: Time step in seconds, or 0.0 for 'auto'.
    :type timeStep: float
    
    :param maxNumberFormants: Maximum number of formants.
    :type maxNumberFormants: int
    
    :param maxFormant: Maximum formant value (Hz) for all speakers, or for female speakers,
                       if maxFormantMale is also specified.
    :type maxFormant: int
    
    :param maxFormantMale: Maximum formant value (Hz) for male speakers, or NULL to use
                           the same value as max.formant.
    :type maxFormantMale: int
    
    :param genderAttribute: Name of the LaBB-CAT participant attribute that contains the
                            participant's gender - normally this is "participant_gender".
    :type genderAttribute: str
    
    :param valueForMale: The value that the genderAttribute has when the participant is male.
    :type valueForMale: str
    
    :param windowLength: Window length in seconds.
    :type windowLength: float
    
    :param preemphasisFrom: Pre-emphasis from (Hz)
    :type preemphasisFrom: int
    
    :returns: A script fragment which can be passed as the praatScript parameter of
              `processWithPraat() <#labbcat.LabbcatView.processWithPraat>`_
    :rtype: str
    """
    script = "\nmaxformant = "+str(maxFormant)
    if maxFormantMale != None and genderAttribute != None and maxFormant != maxFormantMale:
        ## differentiate between males and others
        script = script + "\nif "+genderAttribute+"$ = \""+valueForMale+"\""
        script = script + "\n  maxformant = " +str(maxFormantMale)
        script = script + "\nendif"
    # ensure the sound sample is selected
    script = script+"\nselect Sound 'sampleName$'"
    script = script+"\nTo Formant (burg): "+str(timeStep)+", "+str(maxNumberFormants)+", "+"maxformant, "+str(windowLength)+", "+str(preemphasisFrom)
    for point in samplePoints:
        varname = "time_"+str(point).replace(".","_")
        ## first output absolute point offset
        script = script+"\npointoffset = targetAbsoluteStart + "+str(point)+" * targetDuration"
        script = script+"\n"+varname+" = pointoffset"
        script = script+"\nprint '"+varname+"' 'newline$'"
        ## now use the relative point offset
        script = script+"\npointoffset = targetStart + "+str(point)+" * targetDuration"
        for f in formants:
            varname = "f"+str(f)+"_time_"+str(point).replace(".","_")
            script = script+"\n"+varname+" = Get value at time: "+str(f)+", pointoffset, \"hertz\", \"Linear\""
            script = script+"\nprint '"+varname+":0' 'newline$'"
    ## remove formant object
    script = script+"\nRemove\n"
    return(script)

def praatScriptCentreOfGravity(powers = [2], spectrumFast = True):
    """ Generates a script for extracting the CoG, for use with 
    `processWithPraat() <#labbcat.LabbcatView.processWithPraat>`_
    
    This function generates a Praat script fragment which can be passed as the praat.script
    parameter of [processWithPraat], in order to extract one or more spectral centre
    of gravity (CoG) measurements. 

    :param powers: A list of numbers specifying which powers to query for to extract,
                   e.g. [1,2]. 
    :type powers: list of float
    
    :param spectrumFast: Whether to use the 'fast' option when creating the spectrum object
                         to query.
    :type spectrumFast: boolean
    
    :returns: A script fragment which can be passed as the praatScript parameter of
              `processWithPraat() <#labbcat.LabbcatView.processWithPraat>`_
    :rtype: str
    """
    # ensure the sound sample is selected
    script = "\nselect Sound 'sampleName$'"
    if spectrumFast:
        script = script + "\nfast$ = \"yes\""
    else:
        script = script + "\nfast$ = \"no\""
    script = script + "\nTo Spectrum: fast$"
    for power in powers:
        varname = "cog_"+str(power).replace(".","_")
        script = script + "\n"+varname+" = Get centre of gravity: "+str(power)
        script = script + "\nprint '"+varname+":0' 'newline$'"
    ## remove spectrum object
    script = script + "\nRemove\n"
    return(script)

def praatScriptIntensity(minimumPitch = 100.0, timeStep = 0.0, subtractMean = True, getMaximum = True, samplePoints = None, interpolation = 'cubic', skipErrors = True):
    """ 
    Generates a script for extracting maximum intensity, for use with
    `processWithPraat() <#labbcat.LabbcatView.processWithPraat>`_
    
    This function generates a Praat script fragment which can be passed as the praatScript
    parameter of `processWithPraat() <#labbcat.LabbcatView.processWithPraat>`_, in order to 
    extract one or more maximum intensity values. 

    :param minimumPitch: Minimum pitch (Hz).
    :type minimumPitch: float
    
    :param timeStep: Time step in seconds, or 0.0 for 'auto'.
    :type timeStep: float
    
    :param subtractMean: Whether to subtract the mean or not.
    :type subtractMean: boolean
    
    :param getMaximum: Extract the maximum intensity for the sample.
    :type getMaximum: boolean
    
    :param samplePoints: A list of numbers (0 <= samplePoints <= 1) specifying multiple
     points at which to take the measurement.  The default is None, meaning no
     individual measurements will be taken (only the aggregate values identified by
     getMaximum).  A single point at 0.5 means one
     measurement will be taken halfway through the target interval.  If, for example, 
     you wanted eleven measurements evenly spaced throughout the interval, you would
     specify sample.points as being 
     [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0].
    :type samplePoints: list of float
    
    :param interpolation: If samplePoints are specified, this is the interpolation to use
     when getting individual values. Possible values are 'nearest', 'linear', 'cubic',
     'sinc70', or 'sinc700'.
    :type interpolation: str
    
    :param skipErrors: Sometimes, for some segments, Praat fails to create an Intensity object. 
           If skipErrors = True, analysis those segments will be skipped, and corresponding
           pitch values will be returned as "--undefined--". If skip.errors = False, the error
           message from Praat will be returned in the Error field, but no pitch measures will
           be returned for any segments in the same recording.
    :type spectrumFast: boolean
    
    :returns: A script fragment which can be passed as the praatScript parameter of
              `processWithPraat() <#labbcat.LabbcatView.processWithPraat>`_
    :rtype: str
    """    
    # ensure the sound sample is selected
    script = "\nselect Sound 'sampleName$'"
    if subtractMean:
        script = script + "\nsubtractmean$ = \"yes\""
    else:
        script = script + "\nsubtractmean$ = \"no\""
    if skipErrors: ## use nocheck
        script = script + "\n# nocheck to prevent the whole script from failing, and then check for object after"
        script = script + "\nnocheck "
    else:
        script = script + "\n"
    script = script + "To Intensity: "+str(minimumPitch)+", "+str(timeStep)+", subtractmean$"
    
    script = script + "\n# check that an Intensity object was created"
    script = script + "\nobjectCreated = extractWord$(selected$(), \"\") = \"Intensity\""

    if getMaximum:
        script = script + "\nif objectCreated"
        script = script + "\n  maxIntensity = Get maximum: targetStart, targetEnd, \"Parabolic\""
        script = script + "\nelse"
        script = script + "\n  maxIntensity = 1/0" # --undefined--
        script = script + "\nendif"
        script = script + "\nprint 'maxIntensity' 'newline$'"

    if samplePoints != None:
        for point in samplePoints:
            varname = "time_"+str(point).replace(".","_")+"_for_intensity"
            ## first output absolute point offset
            script = script + "\npointoffset = targetAbsoluteStart + "+str(point)+" * targetDuration"
            script = script + "\n"+varname+" = pointoffset"
            script = script + "\nprint '"+varname+"' 'newline$'"
            ## now use the relative point offset
            script = script + "\npointoffset = targetStart + "+str(point)+" * targetDuration"
            varname = "intensity_time_"+str(point).replace(".","_")
            script = script + "\nif objectCreated"
            script = script + "\n  "+varname+" = Get value at time: pointoffset, \""+interpolation+"\""
            script = script + "\nelse"
            script = script + "\n  "+varname+" = 1/0" # --undefined--
            script = script + "\nendif"
            script = script + "\nprint '"+varname+":0' 'newline$'"
    ## remove spectrum object
    script = script + "\nif objectCreated"
    script = script + "\n  Remove"
    script = script + "\nendif\n"
    return(script)

def praatScriptPitch(
        getMean = True, getMinimum = False, getMaximum = False,
        timeStep = 0.0, pitchFloor = 60, maxNumberOfCandidates = 15, veryAccurate = False,
        silenceThreshold = 0.03, voicingThreshold = 0.5,
        octaveCost = 0.01, octaveJumpCost = 0.35, voicedUnvoicedCost = 0.35, pitchCeiling = 500,
        pitchFloorMale = 30, voicingThresholdMale = 0.4, pitchCeilingMale = 250,
        genderAttribute = 'participant_gender', valueForMale = "M",
        samplePoints = None, interpolation = 'linear', skipErrors = True):
    """ Generates a script for extracting pitch, for use with
    `processWithPraat() <#labbcat.LabbcatView.processWithPraat>`_
    
    This function generates a Praat script fragment which can be passed as the praatScript
    parameter of `processWithPraat() <#labbcat.LabbcatView.processWithPraat>`_, in order to 
    extract pitch information. 

    :param getMean: Whether to extract the mean pitch for the sample
    :type getMean: boolean

    :param getMinimum: Whether to extract the minimum pitch for the sample
    :type getMinimum: boolean

    :param getMaximum: Whether to extract the maximum pitch for the sample
    :type getMaximum: boolean

    :param timeStep: Step setting for praat command
    :type timeStep: float

    :param pitchFloor: Minimum pitch (Hz) for all speakers, or for female speakers,           
           if pitchFloorMale is also specified
    :type pitchFloor: int

    :param maxNumberOfCandidates: Maximum number of candidates setting for praat command
    :type maxNumberOfCandidates: int

    :param veryAccurate: Accuracy setting for praat command
    :type veryAccurate: boolean

    :param silenceThreshold: Silence threshold setting for praat command
    :type silenceThreshold: float

    :param voicingThreshold: Voicing threshold (Hz) for all speakers, or for female speakers,
           if voicingThresholdMale is also specified
    :type voicingThreshold: int

    :param octaveCost: Octave cost setting for praat command
    :type octaveCost: float

    :param octaveJumpCost: Octave jump cost setting for praat command
    :type octaveJumpCost: float

    :param voicedUnvoicedCost: Voiced/unvoiced cost setting for praat command
    :type voicedUnvoicedCost: float

    :param pitchCeiling: Maximum pitch (Hz) for all speakers, or for female speakers,
           if pitchFloorMale is also specified
    :type pitchCeiling: int

    :param pitchFloorMale: Minimum pitch (Hz) for male speakers
    :type pitchFloorMale: int

    :param voicingThresholdMale: Voicing threshold (Hz) for male speakers
    :type voicingThresholdMale: int

    :param pitchCeilingMale: Maximum pitch (Hz) for male speakers
    :type pitchCeilingMale: int

    :param genderAttribute: Name of the LaBB-CAT participant attribute that contains the
           participant's gender - normally this is "participant_gender"
    :type genderAttribute: str

    :param valueForMale: The value that the genderAttribute has when the participant is male
    :type valueForMale: str

    :param samplePoints: A list of numbers (0 <= samplePoints <= 1) specifying multiple
           points at which to take the measurement  The default is None, meaning no
           individual measurements will be taken (only the aggregate values identified by
           getMean, getMinimum, and getMaximum).  A single point at 0.5 means one
           measurement will be taken halfway through the target interval.  If, for example, 
           you wanted eleven measurements evenly spaced throughout the interval, you would
           specify sample.points as being 
           [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0].  
    :type samplePoints:

    :param interpolation: If sample.points are specified, this is the interpolation to use
           when getting individual values. Possible values are 'nearest' or 'linear'.
    :type interpolation: str

    :param skipErrors: Sometimes, for some segments, Praat fails to create a Pitch
           object. If skipErrors = True, analysis those segments will be skipped, and corresponding
           pitch values will be returned as "--undefined--". If skip.errors = FALSE, the error
           message from Praat will be returned in the Error field, but no pitch measures will
           be returned for any segments in the same recording.
    :type skipErrors: boolean
    
    :returns: A script fragment which can be passed as the praatScript parameter of
              `processWithPraat() <#labbcat.LabbcatView.processWithPraat>`_
    :rtype: str
    """    
    # ensure the sound sample is selected
    script = "\nselect Sound 'sampleName$'"
    script = script + "\npitchfloor = "+str(pitchFloor)
    script = script + "\nvoicingthreshold = "+str(voicingThreshold)
    script = script + "\npitchceiling = "+str(pitchCeiling)
    if veryAccurate:
        script = script + "\nveryaccurate$ = \"yes\""
    else:
        script = script + "\nveryaccurate$ = \"no\""
    if genderAttribute != None:
        ## differentiate between males and others
        if pitchFloorMale != None and pitchFloor != pitchFloorMale:
            script = script + "\nif "+genderAttribute+"$ = \""+valueForMale+"\""
            script = script + "\n  pitchfloor = "+str(pitchFloorMale)
            script = script + "\nendif"
        if voicingThresholdMale != None and voicingThreshold != voicingThresholdMale:
            script = script + "\nif "+genderAttribute+"$ = \""+valueForMale+"\""
            script = script + "\n  voicingthreshold = "+str(voicingThresholdMale)
            script = script + "\nendif"
        if pitchCeilingMale != None and pitchCeiling != pitchCeilingMale:
            script = script + "\nif "+genderAttribute+"$ = \""+valueForMale+"\""
            script = script + "\n  pitchceiling = "+str(pitchCeilingMale)
            script = script + "\nendif"
    if skipErrors: ## use nocheck
        script = script + "\n# nocheck to prevent the whole script from failing, and then check for object after"
        script = script + "\nnocheck "
    else:
        script = script + "\n"    
    script = script + "To Pitch (ac): "+str(timeStep)+", pitchfloor, "+str(maxNumberOfCandidates)+", veryaccurate$, "+str(silenceThreshold)+", voicingthreshold, "+str(octaveCost)+", "+str(octaveJumpCost)+", "+str(voicedUnvoicedCost)+", pitchceiling"
    
    script = script + "\n# check that a Pitch object was created"
    script = script + "\nobjectCreated = extractWord$(selected$(), \"\") = \"Pitch\""
    if getMean:
        script = script + "\nif objectCreated"
        script = script + "\n  meanPitch = Get mean: targetStart, targetEnd, \"Hertz\""
        script = script + "\nelse"
        script = script + "\n  meanPitch = 1/0" # --undefined--
        script = script + "\nendif"
        script = script + "\nprint 'meanPitch' 'newline$'"
    if getMinimum:
        script = script + "\nif objectCreated"
        script = script + "\n  minPitch = Get minimum: targetStart, targetEnd, \"Hertz\", \"Parabolic\""
        script = script + "\nelse"
        script = script + "\n  minPitch = 1/0" # --undefined--
        script = script + "\nendif"
        script = script + "\nprint 'minPitch' 'newline$'"
    if getMaximum:
        script = script + "\nif objectCreated"
        script = script + "\n  maxPitch = Get maximum: targetStart, targetEnd, \"Hertz\", \"Parabolic\""
        script = script + "\nelse"
        script = script + "\n  maxPitch = 1/0" # --undefined--
        script = script + "\nendif"
        script = script + "\nprint 'maxPitch' 'newline$'"
    if samplePoints != None:
        for point in samplePoints:
            varname = "time_"+str(point).replace(".","_")+"_for_pitch"
            ## first output absolute point offset
            script = script + "\npointoffset = targetAbsoluteStart + "+str(point)+" * targetDuration"
            script = script + "\n"+ varname+" = pointoffset"
            script = script + "\nprint '"+varname+"' 'newline$'"
            ## now use the relative point offset
            script = script + "\npointoffset = targetStart + "+str(point)+" * targetDuration"
            varname = "pitch_time_"+str(point).replace(".","_")
            script = script + "\nif objectCreated"
            script = script + "\n  "+varname+" = Get value at time: pointoffset, \"Hertz\", \""+interpolation+"\""
            script = script + "\nelse"
            script = script + "\n  "+varname+" = 1/0" # --undefined--
            script = script + "\nendif"
            script = script + "\nprint '"+varname+":0' 'newline$'"
    ## remove pitch object
    script = script + "\nif objectCreated"
    script = script + "\n  Remove"
    script = script + "\nendif\n"
    return(script)

def praatScriptFastTrack(
        formants = [1,2], samplePoints = [0.5],
        lowestAnalysisFrequency = 5000, lowestAnalysisFrequencyMale = 4500,
        highestAnalysisFrequency = 7000, highestAnalysisFrequencyMale = 6500,
        genderAttribute = "participant_gender", valueForMale = "M",
        timeStep = 0.002, trackingMethod = "burg", numberOfFormants = 3,
        maximumF1Frequency = 1200, maximumF1Bandwidth = None,
        maximumF2Bandwidth = None, maximumF3Bandwidth = None, minimumF4Frequency = 2900,
        enableRhoticHeuristic = True, enableF3F4ProximityHeuristic = True,
        numberOfSteps = 20, numberOfCoefficients = 5):
    """ Generates a script for extracting formants using FastTrack, for use with 
    `processWithPraat() <#labbcat.LabbcatView.processWithPraat>`_

    This function generates a Praat script fragment which can be passed as the praat.script
    parameter of `processWithPraat() <#labbcat.LabbcatView.processWithPraat>`_, in order to
    extract selected formants using the FastTrack Praat plugin.
    
    The FastTrack Praat plugin, developed by Santiago Barreda, automatically runs multiple
    formant analyses on each segment, selects the best (the smoothest, with optional
    heuristics), and makes the winning formant object available for measurement. For more
    information, see `FastTrack <https://github.com/santiagobarreda/FastTrack>`_
    
    :param formants: A list of integers specifying which formants to extract, e.g [1,2]
                    for the first and second formant.
    :type formants: list of int

    :param samplePoints: A vector of numbers (0 <= samplePoints <= 1) specifying multiple
                         points at which to take the measurement.  The default is a single
                         point at 0.5 - this means one measurement will be taken halfway
                         through the target interval.  If, for example, you wanted eleven
                         measurements evenly spaced throughout the interval, you would
                         specify sample.points as being 
                         [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0].
    :type samplePoints: list of float

    :param lowestAnalysisFrequency: Lowest analysis frequency (Hz) by default.
    :type lowestAnalysisFrequency: int

    :param lowestAnalysisFrequencyMale: Lowest analysis frequency (Hz) for male
                                        speakers, or None to use the same value as
                                        lowestAnalysisFrequency. 
    :type lowestAnalysisFrequencyMale: int

    :param highestAnalysisFrequency: Highest analysis frequency (Hz) by default.
    :type highestAnalysisFrequency: int

    :param highestAnalysisFrequencyMale: Highest analysis frequency (Hz) for male
                                         speakers, or None to use the same value as
                                         highestAnalysisFrequency. 
    :type highestAnalysisFrequencyMale: int

    :param genderAttribute: Name of the LaBB-CAT participant attribute that contains the
                            participant's gender - normally this is "participant_gender".
    :type genderAttribute: str

    :param valueForMale: The value that the genderAttribute has when the participant is male.
    :type valueForMale: str

    :param timeStep: Time step in seconds
    :type timeStep: float

    :param trackingMethod: tracking_method parameter for trackAutoselectProcedure; 
                           "burg" or "robust". 
    :type trackingMethod: str

    :param numberOfFormants: Number of formants to track - 3 or 4. 
    :type numberOfFormants: int

    :param maximumF1Frequency: Specifying a value enables the F1 frequency heuristic: 
                               Median F1 frequency should not be higher than this value.
    :type maximumF1Frequency: int

    :param maximumF1Bandwidth: Specifying a value (e.g. 500) enables the F1 bandwidth
                               heuristic: Median F1 bandwidth should not be higher than
                               this value.
    :type maximumF1Bandwidth: int

    :param maximumF2Bandwidth: Specifying a value (e.g. 600) enables the F2 bandwidth
                               heuristic: Median F2 bandwidth should not be higher than
                               this value.  
    :type maximumF2Bandwidth: int

    :param maximumF3Bandwidth: Specifying a value (e.g. 900) enables the F3 bandwidth heuristic: 
                               Median F3 bandwidth should not be higher than this value. 
    :type maximumF3Bandwidth: int

    :param minimumF4Frequency: Specifying a value enables the F4 frequency heuristic: 
                               Median F4 frequency should not be lower than this value.
    :type minimumF4Frequency: int

    :param enable:.rhotic.heuristic Whether to enable the rhotic heuristic: 
                                    If F3 < 2000 Hz, F1 and F2 should be at least 500 Hz apart.
    :type enable: boolean

    :param enableF3F4ProximityHeuristic: Whether to enable the F3/F4 proximity heuristic: 
                                         If (F4 - F3) < 500 Hz, F1 and F2 should be
                                         at least 1500 Hz apart.
    :type enableF3F4ProximityHeuristic: boolean

    :param numberOfSteps: Number of analyses between low and high analysis limits. More
                          analysis steps may improve results, but will increase analysis time 
                          (50 percent more steps = around 50 percent longer to analyze).
    :type numberOfSteps: int

    :param numberOfCoefficients: Number of coefficients for formant prediction. More
                                 coefficients allow for more sudden, and 'wiggly' formant motion. 
    :param numberOfCoefficients: int

    :returns: A script fragment which can be passed as the praatScript parameter of
              `processWithPraat() <#labbcat.LabbcatView.processWithPraat>`_
    :rtype: str
    """
    # include FastTrack script and load default global settings
    script = "\ninclude utils/trackAutoselectProcedure.praat"
    script = script+"\n@getSettings"
    # override global settings that we know about
    script = script+"\ntime_step = "+str(timeStep)
    script = script+"\nmethod$ = \""+trackingMethod+"\""
    if maximumF1Frequency == None:
        script = script + "\nenable_F1_frequency_heuristic = 0"
    else:
        script = script+"\nenable_F1_frequency_heuristic = 1"
        script = script+"\nmaximum_F1_frequency_value = "+str(maximumF1Frequency)
    if maximumF1Bandwidth == None:
        script = script+"\nenable_F1_bandwidth_heuristic = 0"
    else:
        script = script+"\nenable_F1_bandwidth_heuristic = 1"
        script = script+"\nmaximum_F1_bandwidth_value = "+str(maximumF1Bandwidth)
    if maximumF2Bandwidth == None:
        script = script+"\nenable_F2_bandwidth_heuristic = 0"
    else:
        script = script+"\nenable_F2_bandwidth_heuristic = 1"
        script = script+"\nmaximum_F2_bandwidth_value = "+str(maximumF2Bandwidth)
    if maximumF3Bandwidth == None:
        script = script+"\nenable_F3_bandwidth_heuristic = 0"
    else:
        script = script+"\nenable_F3_bandwidth_heuristic = 1"
        script = script+"\nmaximum_F3_bandwidth_value = "+str(maximumF3Bandwidth)
    if minimumF4Frequency == None:
        script = script+"\nenable_F4_frequency_heuristic = 0"
    else:
        script = script+"\nenable_F4_frequency_heuristic = 1"
        script = script+"\nminimum_F4_frequency_value = "+str(minimumF4Frequency)
    if enableRhoticHeuristic:
        script = script+"\nenable_rhotic_heuristic = 1"
    else:
        script = script+"\nenable_rhotic_heuristic = 0"
    if enableF3F4ProximityHeuristic:
        script = script+"\nenable_F3F4_proximity_heuristic = 1"
    else:
        script = script+"\nenable_F3F4_proximity_heuristic = 0"
    script = script+"\noutput_bandwidth = 1"
    script = script+"\noutput_predictions = 1"
    script = script+"\noutput_pitch = 1"
    script = script+"\noutput_intensity = 1"
    script = script+"\noutput_harmonicity = 1"
    script = script+"\noutput_normalized_time = 1"
    script = script+"\ndir$ = \".\""
    script = script+"\nsteps = "+str(numberOfSteps)
    script = script+"\ncoefficients = "+str(numberOfCoefficients)
    script = script+"\nformants = "+str(numberOfFormants)
    script = script+"\nout_formant = 2"
    script = script+"\nimage = 0"
    script = script+"\nmax_plot = 4000"
    script = script+"\nout_table = 0"
    script = script+"\nout_all = 0"
    script = script+"\ncurrent_view = 0"
    # Segments shorter than fastTrackMinimumDuration will be ignored, and empty values returned.
    # The FastTrack limit is 0.03s (30ms), but because of possible rounding errors
    # in Praat arithemitic, the default is set slightly higher than this.
    script = script+"\nfastTrackMinimumDuration = 0.030000000000001"
    
    script = script+"\nlowestAnalysisFrequency = "+str(lowestAnalysisFrequency)
    script = script+"\nhighestAnalysisFrequency = "+str(highestAnalysisFrequency)
    if genderAttribute != None:
        # differentiate between males and others
        script = script + "\nif "+str(genderAttribute)+"$ = \""+str(valueForMale)+"\""
        if lowestAnalysisFrequencyMale != None and lowestAnalysisFrequency != lowestAnalysisFrequencyMale:
            script = script + "\n  lowestAnalysisFrequency = "+str(lowestAnalysisFrequencyMale)
        if highestAnalysisFrequencyMale != None and highestAnalysisFrequency != highestAnalysisFrequencyMale:
            script = script + "\n  highestAnalysisFrequency = "+str(highestAnalysisFrequencyMale)
        script = script + "\nendif"
    # ensure the sound sample is selected
    script = script+"\nselect Sound 'sampleName$'"
    script = script+"\nif windowDuration >= fastTrackMinimumDuration"
    script = script+"\n  @trackAutoselect: selected(), dir$, lowestAnalysisFrequency, highestAnalysisFrequency, steps, coefficients, formants, method$, image, selected(), current_view, max_plot, out_formant, out_table, out_all"
    for point in samplePoints:
        varname = "time_"+str(point).replace(".","_")
        # now use the relative point offset
        script = script + "\n  pointoffset = targetStart + "+str(point)+" * targetDuration"
        for f in formants:
            varname = "f"+str(f)+"_time_"+str(point).replace(".","_")
            script = script + "\n  "+varname+" = Get value at time: "+str(f)+", pointoffset, \"hertz\", \"Linear\""
    # remove formant object
    script = script + "\n  Remove"
    script = script + "\nelse" # sample is too short, output blank values
    for point in samplePoints:
        for f in formants:
            varname = "f"+str(f)+"_time_"+str(point).replace(".","_")
            script = script + "\n  "+str(varname)+" = \"\""
    script = script + "\nendif\n"
    
    # To ensure LaBB-CAT can interpret correctly the number of outputs,
    # only include one set of print statements:
    for point in samplePoints:
        varname = "time_"+str(point).replace(".","_")
        # first output absolute point offset
        script = script + "\npointoffset = targetAbsoluteStart + "+str(point)+" * targetDuration"
        script = script + "\n"+varname+" = pointoffset"
        script = script + "\nprint '"+varname+"' 'newline$'"
        for f in formants:
            varname = "f"+str(f)+"_time_"+str(point).replace(".","_")
            script = script + "\nprint '"+varname+"' 'newline$'"
    script = script + "\n"
    return(script)
