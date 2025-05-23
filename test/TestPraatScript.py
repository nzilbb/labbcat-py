import unittest
import os
import labbcat

class TestPraatScript(unittest.TestCase):
    """ Unit tests for PraatScript.
    
    These tests ensure functions for generating Praat scripts work as expected. 
    """
    
    def test_praatScriptFormants(self):
        self.maxDiff = None
        # default parameters
        self.assertEqual(
            "\nmaxformant = 5500"
            "\nif participant_gender$ = \"M\""
            "\n  maxformant = 5000"
            "\nendif"
            "\nselect Sound 'sampleName$'"
            "\nTo Formant (burg): 0.0, 5, maxformant, 0.025, 50"
            "\npointoffset = targetAbsoluteStart + 0.5 * targetDuration"
            "\ntime_0_5 = pointoffset"
            "\nprint 'time_0_5' 'newline$'"
            "\npointoffset = targetStart + 0.5 * targetDuration"
            "\nf1_time_0_5 = Get value at time: 1, pointoffset, \"hertz\", \"Linear\""
            "\nprint 'f1_time_0_5:0' 'newline$'"
            "\nf2_time_0_5 = Get value at time: 2, pointoffset, \"hertz\", \"Linear\""
            "\nprint 'f2_time_0_5:0' 'newline$'"
            "\nRemove"
            "\n",
            labbcat.praatScriptFormants(),
            "default parameters")
        
        self.assertEqual(
            "\nmaxformant = 6000"
            "\nselect Sound 'sampleName$'"
            "\nTo Formant (burg): 0.01, 4, maxformant, 0.01, 60"
            "\npointoffset = targetAbsoluteStart + 0.3 * targetDuration"
            "\ntime_0_3 = pointoffset"
            "\nprint 'time_0_3' 'newline$'"
            "\npointoffset = targetStart + 0.3 * targetDuration"
            "\nf1_time_0_3 = Get value at time: 1, pointoffset, \"hertz\", \"Linear\""
            "\nprint 'f1_time_0_3:0' 'newline$'"
            "\nf2_time_0_3 = Get value at time: 2, pointoffset, \"hertz\", \"Linear\""
            "\nprint 'f2_time_0_3:0' 'newline$'"
            "\nf3_time_0_3 = Get value at time: 3, pointoffset, \"hertz\", \"Linear\""
            "\nprint 'f3_time_0_3:0' 'newline$'"
            "\npointoffset = targetAbsoluteStart + 0.5 * targetDuration"
            "\ntime_0_5 = pointoffset"
            "\nprint 'time_0_5' 'newline$'"
            "\npointoffset = targetStart + 0.5 * targetDuration"
            "\nf1_time_0_5 = Get value at time: 1, pointoffset, \"hertz\", \"Linear\""
            "\nprint 'f1_time_0_5:0' 'newline$'"
            "\nf2_time_0_5 = Get value at time: 2, pointoffset, \"hertz\", \"Linear\""
            "\nprint 'f2_time_0_5:0' 'newline$'"
            "\nf3_time_0_5 = Get value at time: 3, pointoffset, \"hertz\", \"Linear\""
            "\nprint 'f3_time_0_5:0' 'newline$'"
            "\npointoffset = targetAbsoluteStart + 0.7 * targetDuration"
            "\ntime_0_7 = pointoffset"
            "\nprint 'time_0_7' 'newline$'"
            "\npointoffset = targetStart + 0.7 * targetDuration"
            "\nf1_time_0_7 = Get value at time: 1, pointoffset, \"hertz\", \"Linear\""
            "\nprint 'f1_time_0_7:0' 'newline$'"
            "\nf2_time_0_7 = Get value at time: 2, pointoffset, \"hertz\", \"Linear\""
            "\nprint 'f2_time_0_7:0' 'newline$'"
            "\nf3_time_0_7 = Get value at time: 3, pointoffset, \"hertz\", \"Linear\""
            "\nprint 'f3_time_0_7:0' 'newline$'"
            "\nRemove"
            "\n",
            labbcat.praatScriptFormants(
                formants = [1,2,3], samplePoints = [0.3, 0.5, 0.7], timeStep = 0.01,
                maxNumberFormants = 4, maxFormant = 6000,
                maxFormantMale = 6000, genderAttribute = 'participant_gender', valueForMale = "M",
                windowLength = 0.01, preemphasisFrom = 60),
            "explicit parameters")

    def test_praatScriptFastTrack(self):
        self.maxDiff = None
        # default parameters
        self.assertEqual(
            "\ninclude utils/trackAutoselectProcedure.praat"
            "\n@getSettings"
            "\ntime_step = 0.002"
            "\nmethod$ = \"burg\""
            "\nenable_F1_frequency_heuristic = 1"
            "\nmaximum_F1_frequency_value = 1200"
            "\nenable_F1_bandwidth_heuristic = 0"
            "\nenable_F2_bandwidth_heuristic = 0"
            "\nenable_F3_bandwidth_heuristic = 0"
            "\nenable_F4_frequency_heuristic = 1"
            "\nminimum_F4_frequency_value = 2900"
            "\nenable_rhotic_heuristic = 1"
            "\nenable_F3F4_proximity_heuristic = 1"
            "\noutput_bandwidth = 1"
            "\noutput_predictions = 1"
            "\noutput_pitch = 1"
            "\noutput_intensity = 1"
            "\noutput_harmonicity = 1"
            "\noutput_normalized_time = 1"
            "\ndir$ = \".\""
            "\nsteps = 20"
            "\ncoefficients = 5"
            "\nformants = 3"
            "\nout_formant = 2"
            "\nimage = 0"
            "\nmax_plot = 4000"
            "\nout_table = 0"
            "\nout_all = 0"
            "\ncurrent_view = 0"
            "\nfastTrackMinimumDuration = 0.030000000000001"    
            "\nlowestAnalysisFrequency = 5000"
            "\nhighestAnalysisFrequency = 7000"
            "\nif participant_gender$ = \"M\""
            "\n  lowestAnalysisFrequency = 4500"
            "\n  highestAnalysisFrequency = 6500"
            "\nendif"
            "\nselect Sound 'sampleName$'"
            "\nif windowDuration >= fastTrackMinimumDuration"
            "\n  @trackAutoselect: selected(), dir$, lowestAnalysisFrequency, highestAnalysisFrequency, steps, coefficients, formants, method$, image, selected(), current_view, max_plot, out_formant, out_table, out_all"
            "\n  pointoffset = targetStart + 0.5 * targetDuration"
            "\n  f1_time_0_5 = Get value at time: 1, pointoffset, \"hertz\", \"Linear\""
            "\n  f2_time_0_5 = Get value at time: 2, pointoffset, \"hertz\", \"Linear\""
            "\n  Remove"
            "\nelse"
            "\n  f1_time_0_5 = \"\""
            "\n  f2_time_0_5 = \"\""
            "\nendif\n"
            "\npointoffset = targetAbsoluteStart + 0.5 * targetDuration"
            "\ntime_0_5 = pointoffset"
            "\nprint 'time_0_5' 'newline$'"
            "\nprint 'f1_time_0_5' 'newline$'"
            "\nprint 'f2_time_0_5' 'newline$'"
            "\n",
            labbcat.praatScriptFastTrack(),
            "default parameters")
        
        self.assertEqual(
            "\ninclude utils/trackAutoselectProcedure.praat"
            "\n@getSettings"
            "\ntime_step = 0.005"
            "\nmethod$ = \"robust\""
            "\nenable_F1_frequency_heuristic = 1"
            "\nmaximum_F1_frequency_value = 1250"
            "\nenable_F1_bandwidth_heuristic = 1"
            "\nmaximum_F1_bandwidth_value = 50"
            "\nenable_F2_bandwidth_heuristic = 1"
            "\nmaximum_F2_bandwidth_value = 60"
            "\nenable_F3_bandwidth_heuristic = 1"
            "\nmaximum_F3_bandwidth_value = 70"
            "\nenable_F4_frequency_heuristic = 0"
            "\nenable_rhotic_heuristic = 0"
            "\nenable_F3F4_proximity_heuristic = 0"
            "\noutput_bandwidth = 1"
            "\noutput_predictions = 1"
            "\noutput_pitch = 1"
            "\noutput_intensity = 1"
            "\noutput_harmonicity = 1"
            "\noutput_normalized_time = 1"
            "\ndir$ = \".\""
            "\nsteps = 25"
            "\ncoefficients = 6"
            "\nformants = 4"
            "\nout_formant = 2"
            "\nimage = 0"
            "\nmax_plot = 4000"
            "\nout_table = 0"
            "\nout_all = 0"
            "\ncurrent_view = 0"
            "\nfastTrackMinimumDuration = 0.030000000000001"    
            "\nlowestAnalysisFrequency = 5050"
            "\nhighestAnalysisFrequency = 7050"
            "\nif gender$ = \"male\""
            "\n  lowestAnalysisFrequency = 4550"
            "\n  highestAnalysisFrequency = 6550"
            "\nendif"
            "\nselect Sound 'sampleName$'"
            "\nif windowDuration >= fastTrackMinimumDuration"
            "\n  @trackAutoselect: selected(), dir$, lowestAnalysisFrequency, highestAnalysisFrequency, steps, coefficients, formants, method$, image, selected(), current_view, max_plot, out_formant, out_table, out_all"
            "\n  pointoffset = targetStart + 0.3 * targetDuration"
            "\n  f1_time_0_3 = Get value at time: 1, pointoffset, \"hertz\", \"Linear\""
            "\n  f2_time_0_3 = Get value at time: 2, pointoffset, \"hertz\", \"Linear\""
            "\n  f3_time_0_3 = Get value at time: 3, pointoffset, \"hertz\", \"Linear\""
            "\n  pointoffset = targetStart + 0.7 * targetDuration"
            "\n  f1_time_0_7 = Get value at time: 1, pointoffset, \"hertz\", \"Linear\""
            "\n  f2_time_0_7 = Get value at time: 2, pointoffset, \"hertz\", \"Linear\""
            "\n  f3_time_0_7 = Get value at time: 3, pointoffset, \"hertz\", \"Linear\""
            "\n  Remove"
            "\nelse"
            "\n  f1_time_0_3 = \"\""
            "\n  f2_time_0_3 = \"\""
            "\n  f3_time_0_3 = \"\""
            "\n  f1_time_0_7 = \"\""
            "\n  f2_time_0_7 = \"\""
            "\n  f3_time_0_7 = \"\""
            "\nendif\n"
            "\npointoffset = targetAbsoluteStart + 0.3 * targetDuration"
            "\ntime_0_3 = pointoffset"
            "\nprint 'time_0_3' 'newline$'"
            "\nprint 'f1_time_0_3' 'newline$'"
            "\nprint 'f2_time_0_3' 'newline$'"
            "\nprint 'f3_time_0_3' 'newline$'"
            "\npointoffset = targetAbsoluteStart + 0.7 * targetDuration"
            "\ntime_0_7 = pointoffset"
            "\nprint 'time_0_7' 'newline$'"
            "\nprint 'f1_time_0_7' 'newline$'"
            "\nprint 'f2_time_0_7' 'newline$'"
            "\nprint 'f3_time_0_7' 'newline$'"
            "\n",
            labbcat.praatScriptFastTrack(
                formants = [1,2,3], samplePoints = [0.3,0.7],
                lowestAnalysisFrequency = 5050, lowestAnalysisFrequencyMale = 4550,
                highestAnalysisFrequency = 7050, highestAnalysisFrequencyMale = 6550,
                genderAttribute = "gender", valueForMale = "male",
                timeStep = 0.005, trackingMethod = "robust", numberOfFormants = 4,
                maximumF1Frequency = 1250, maximumF1Bandwidth = 50,
                maximumF2Bandwidth = 60, maximumF3Bandwidth = 70, minimumF4Frequency = None,
                enableRhoticHeuristic = False, enableF3F4ProximityHeuristic = False,
                numberOfSteps = 25, numberOfCoefficients = 6),
            "explicit parameters")

    def test_praatScriptCentreOfGravity(self):
        self.maxDiff = None
        # default parameters
        self.assertEqual(
            "\nselect Sound 'sampleName$'"
            "\nfast$ = \"yes\""
            "\nTo Spectrum: fast$"
            "\ncog_2 = Get centre of gravity: 2"
            "\nprint 'cog_2:0' 'newline$'"
            "\nRemove"
            "\n",
            labbcat.praatScriptCentreOfGravity(),
            "default parameters")
        
        self.assertEqual(
            "\nselect Sound 'sampleName$'"
            "\nfast$ = \"no\""
            "\nTo Spectrum: fast$"
            "\ncog_0_6666666666666666 = Get centre of gravity: 0.6666666666666666"
            "\nprint 'cog_0_6666666666666666:0' 'newline$'"
            "\ncog_1 = Get centre of gravity: 1"
            "\nprint 'cog_1:0' 'newline$'"
            "\ncog_2 = Get centre of gravity: 2"
            "\nprint 'cog_2:0' 'newline$'"
            "\nRemove"
            "\n",
            labbcat.praatScriptCentreOfGravity(powers = [2/3,1,2], spectrumFast=False),
            "explicit parameters")

    def test_praatScriptIntensity(self):
        self.maxDiff = None
        # default parameters
        self.assertEqual(
            "\nselect Sound 'sampleName$'"
            "\nsubtractmean$ = \"yes\""
            "\n# nocheck to prevent the whole script from failing, and then check for object after"
            "\nnocheck To Intensity: 100.0, 0.0, subtractmean$"
            "\n# check that an Intensity object was created"
            "\nobjectCreated = extractWord$(selected$(), \"\") = \"Intensity\""
            "\nif objectCreated"
            "\n  maxIntensity = Get maximum: targetStart, targetEnd, \"Parabolic\""
            "\nelse"
            "\n  maxIntensity = 1/0"
            "\nendif"
            "\nprint 'maxIntensity' 'newline$'"
            "\nif objectCreated"
            "\n  Remove"
            "\nendif"
            "\n",
            labbcat.praatScriptIntensity(),
            "default parameters")
        
        self.assertEqual(
            "\nselect Sound 'sampleName$'"
            "\nsubtractmean$ = \"no\""
            "\nTo Intensity: 200.0, 0.01, subtractmean$"
            "\n# check that an Intensity object was created"
            "\nobjectCreated = extractWord$(selected$(), \"\") = \"Intensity\""
            "\npointoffset = targetAbsoluteStart + 0.4 * targetDuration"
            "\ntime_0_4_for_intensity = pointoffset"
            "\nprint 'time_0_4_for_intensity' 'newline$'"
            "\npointoffset = targetStart + 0.4 * targetDuration"
            "\nif objectCreated"
            "\n  intensity_time_0_4 = Get value at time: pointoffset, \"nearest\""
            "\nelse"
            "\n  intensity_time_0_4 = 1/0"
            "\nendif"
            "\nprint 'intensity_time_0_4:0' 'newline$'"
            "\nif objectCreated"
            "\n  Remove"
            "\nendif"
            "\n",
            labbcat.praatScriptIntensity(minimumPitch = 200.0, timeStep = 0.01, subtractMean = False, getMaximum = False, samplePoints = [0.4], interpolation = 'nearest', skipErrors = False),
            "explicit parameters")

    def test_praatScriptPitch(self):
        self.maxDiff = None
        # default parameters
        self.assertEqual(
            "\nselect Sound 'sampleName$'"
            "\npitchfloor = 60"
            "\nvoicingthreshold = 0.5"
            "\npitchceiling = 500"
            "\nveryaccurate$ = \"no\""
            "\nif participant_gender$ = \"M\""
            "\n  pitchfloor = 30"
            "\nendif"
            "\nif participant_gender$ = \"M\""
            "\n  voicingthreshold = 0.4"
            "\nendif"
            "\nif participant_gender$ = \"M\""
            "\n  pitchceiling = 250"
            "\nendif"
            "\n# nocheck to prevent the whole script from failing, and then check for object after"
            "\nnocheck To Pitch (ac): 0.0, pitchfloor, 15, veryaccurate$, 0.03, voicingthreshold, 0.01, 0.35, 0.35, pitchceiling"
            "\n# check that a Pitch object was created"
            "\nobjectCreated = extractWord$(selected$(), \"\") = \"Pitch\""
            "\nif objectCreated"
            "\n  meanPitch = Get mean: targetStart, targetEnd, \"Hertz\""
            "\nelse"
            "\n  meanPitch = 1/0"
            "\nendif"
            "\nprint 'meanPitch' 'newline$'"
            "\nif objectCreated"
            "\n  Remove"
            "\nendif"
            "\n",
            labbcat.praatScriptPitch(),
            "default parameters")
        
        self.assertEqual(
            "\nselect Sound 'sampleName$'"
            "\npitchfloor = 50"
            "\nvoicingthreshold = 0.4"
            "\npitchceiling = 600"
            "\nveryaccurate$ = \"yes\""
            "\nTo Pitch (ac): 0.001, pitchfloor, 10, veryaccurate$, 0.02, voicingthreshold, 0.02, 0.4, 0.4, pitchceiling"
            "\n# check that a Pitch object was created"
            "\nobjectCreated = extractWord$(selected$(), \"\") = \"Pitch\""
            "\nif objectCreated"
            "\n  minPitch = Get minimum: targetStart, targetEnd, \"Hertz\", \"Parabolic\""
            "\nelse"
            "\n  minPitch = 1/0"
            "\nendif"
            "\nprint 'minPitch' 'newline$'"
            "\nif objectCreated"
            "\n  maxPitch = Get maximum: targetStart, targetEnd, \"Hertz\", \"Parabolic\""
            "\nelse"
            "\n  maxPitch = 1/0"
            "\nendif"
            "\nprint 'maxPitch' 'newline$'"
            "\npointoffset = targetAbsoluteStart + 0.4 * targetDuration"
            "\ntime_0_4_for_pitch = pointoffset"
            "\nprint 'time_0_4_for_pitch' 'newline$'"
            "\npointoffset = targetStart + 0.4 * targetDuration"
            "\nif objectCreated"
            "\n  pitch_time_0_4 = Get value at time: pointoffset, \"Hertz\", \"nearest\""
            "\nelse"
            "\n  pitch_time_0_4 = 1/0"
            "\nendif"
            "\nprint 'pitch_time_0_4:0' 'newline$'"
            "\nif objectCreated"
            "\n  Remove"
            "\nendif"
            "\n",
            labbcat.praatScriptPitch(
                getMean = False, getMinimum = True, getMaximum = True,
                timeStep = 0.001, pitchFloor = 50, maxNumberOfCandidates = 10, veryAccurate = True,
                silenceThreshold = 0.02, voicingThreshold = 0.4,
                octaveCost = 0.02, octaveJumpCost = 0.4, voicedUnvoicedCost = 0.4,
                pitchCeiling = 600,
                pitchFloorMale = 50, voicingThresholdMale = 0.4, pitchCeilingMale = 600,
                genderAttribute = 'gender', valueForMale = "Male",
                samplePoints = [0.4], interpolation = 'nearest', skipErrors = False),
            "explicit parameters")

if __name__ == '__main__':
    unittest.main()
