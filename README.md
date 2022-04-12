# Trimble Line Code Parser

This app is used to parse the Trimble line codes into a format that rmGeo can use on its own. rmGeo needs line ends to be encoded as _-code_, whereas the Trimble Survey Controlers encode the line start as _code S_.
This app works by filtering for all the line codes defined in the current Geoterra Code List CSV file. For these codes all line starts are searched and the previous occurence of the given code encoded as the line ends. The last occurence of a line code will also be encoded as a loine end.

## Usage
Copy any observation file (Trimble Job XML, _.jxl_) that you want parsed into the Input folder. All jxl files in the folder will be parsed an the adapted files are written to the Output folder.
