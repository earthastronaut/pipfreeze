# Pip Freeze

Tool to produce better formatted pip freeze.

Instead of a flat list of requirements, this indents requirements which are dependencies and those that are primary installs. Dependencies shared by multiple packages are commented out. 

This format can be re-read by the typical `pip install -r requirements.txt` and requires not adjustment to other code. 
