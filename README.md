# Trimble Line Code Parser

This app is used to parse the Trimble line codes into a format that rmGeo can use on its own. rmGeo needs line ends to be encoded as _-code_, whereas the Trimble Survey Controlers encode the line start as _code S_.
This app works by filtering for all the line codes defined in the current Geoterra Code List CSV file. For these codes all line starts are searched and the previous occurence of the given code encoded as the line ends. The last occurence of a line code will also be encoded as a loine end.

## Usage
Copy any observation file (Trimble Job XML, _.jxl_) that you want parsed into the Input folder. All jxl files in the folder will be parsed an the adapted files are written to the Output folder. The original file is copied to the Archive folder.

Alternatively there is a Batch file available, which will copy the file that is dragged on top of it to the proper directoriy, executes the program and copies the result back.

## Creation of an executable
To deploy a python script to an executable program, cd to the directory of the file that should be deployed. Then run the following command
```
pyinstaller --onefile Trimble_Line_Code_Converter.py
```

_NOTE:_ This will only work if in a virtual environment with all the packages in requirements installed. To create a virtual environment refer to the virtualenv documentation. To install the packages in requirements.txt cd to the project directory and run `pip install -r requirements.txt`.
