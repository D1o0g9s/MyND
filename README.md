
# MyND: My Neuro Detector
My Neuro Detector (MyND) is a project that attempts to characterize focus and predict distraction states through scalp EEG. 

## EEG Details

OpenBCI Cyton: 

| Pin  | Location | Function  |
|:-----|:---------|:----------|
| Bias | Fpz | Ground |
| N8P | Fp1 | EEG Left Forehead Channel |
| N7P | Fp2 | EEG Right Forehead Channel |
| N2P | HEOG (left) | Saccade Detection |
| N1P | VEOG (left) | Blink Detection |
| SRB | Earclip (right) | Reference |

EEG, EyeTracker, and PsychoPy Marker streams --> XDF 

## Project Tools
1) PsychoPy https://www.psychopy.org/ 
2) Webgazer.js https://webgazer.cs.brown.edu/ </br>
   - A decorated version was used to collect data for this project. See webgazerListener.js
3) OpenBCI Cyton Board V3 https://github.com/OpenBCI/pyOpenBCI 

## Project Versions
- V2.0.1 : Added marker bounds for calibration period.
- V2.0.0 : Reorganized data analysis pipeline. Updated calibration period strings and meme frequency. Short experiment is now similar length as long.
- V1.0.0 : Updated distractor, added memorization aid, and implemented 3 experiment sections. Usable Markers implemented. 
- V0.1.2 : Includes Psychopy, Calibration, OpenBCI, and EyeTracker
- V0.1.1 : Includes Psychopy, OpenBCI, and EyeTracker
- V0.1.0 : Includes Psychopy and OpenBCI
- V0.0.1 : NeuroSky data collection, data analysis

## Data Analysis
- 00 notebook: Data Check and Filtering -> filtered_cleaned_data
- 01 notebook: Create Data Frame -> df
- 02 notebooks: ERPs, Power Bins, PSD Analysis, FOOOF Analysis, Power By Time
- 03 notebooks: Focus Modeling

## References

### Webgazer 
- Alexandra Papoutsaki and Patsorn Sangkloy and James Laskey and Nediyana Daskalova and Jeff Huang and James Hays (2016). WebGazer: Scalable Webcam Eye Tracking Using User Interactions. Proceedings of the 25th International Joint Conference on Artificial Intelligence (IJCAI). 
https://webgazer.cs.brown.edu/ 

### Neurodsp
- Cole, S., Donoghue, T., Gao, R., & Voytek, B. (2019). NeuroDSP: A package for
neural digital signal processing. Journal of Open Source Software, 4(36), 1272.
https://doi.org/10.21105/joss.01272

### Fitting Oscillations & One Over F (FOOOF) 
- Haller M, Donoghue T, Peterson E, Varma P, Sebastian P, Gao R, Noto T, Knight RT, Shestyuk A,
Voytek B (2018) Parameterizing Neural Power Spectra. bioRxiv, 299859.
doi: https://doi.org/10.1101/299859

### de Sa Lab: Ollie's Seg Speller Offline Processing
- https://github.com/ollie-d/SegSpeller/blob/master/Offline%20Processing.ipynb 

### artifact rejection with ICA
- https://sccn.ucsd.edu/~jung/Site/EEG_artifact_removal.html 

### Article Sources
- https://sapienlabs.org/finding-an-alternative-to-connectionism/ 
- https://iopscience.iop.org/article/10.1088/1741-2552/ab355c/meta
- https://link.springer.com/article/10.1186/s13634-015-0251-9 
- https://en.wikipedia.org/wiki/Digital_signal_processing 
- https://en.wikipedia.org/wiki/Electroencephalography
- https://neurofantastic.com/ 

### Meme Sources 
- https://cleanmemes.com/ 
- https://www.reddit.com/r/memes/ 
