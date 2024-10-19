# real-time-scraper
The script scrapes the companies from the Ycombinator and LinkedIn websites matching the field F24 and writes the scraped companies  into the google spreadsheet. It does it every 6 hours.

## Set up Google spreadSheet access

To successfully execute the script you would need to enable the Google Sheets API, create a json key to access the API and a service account shared with the target google spreadsheet document where the scraped companies will be written to. The google spreadsheet should be created beforehand with at least one sheet. Please follow this [link](https://ai2.appinventor.mit.edu/reference/other/googlesheets-api-setup.html) to set up your access to Google spreadsheets. 

## Software requirements

The Python version 3.10, Selenium 4.25 and beautifulSoap 4.11 were installed. To install all the required libraries please use the command:

    pip install beautifulsoup4 gspread oauth2client schedule reportlab selenium

To use Selenium the proper browser driver should be installed and the path to its executable should be added to the env variable PATH. Only the chrome and firefox browsers are supported in the script. Follow the [instructions](https://developer.chrome.com/docs/chromedriver/downloads) to download a proper driver based on the version of your Chrome/Firefox browser. 


## Command line flags:

"-l", "--label" (default="F24") - The flag that will be matched against the companies from the Ycombinator website.

"-t", "--linkedIn-tag" (default="YC F24") - The linkedIn tag that will be matched against the companies from the linkedIn.

"-n", "--spreadsheet-name" (default=None, required: true) - The name of the google sheet to write the data to. 

"-k", "--json-key" (default=None, required=True) - The path to the json key to access the google sheets API.

"-w", "--website" (default="https://www.ycombinator.com/companies") - A website to scrape the data from.

"-b", "--browser" (default="chrome") - The browser with the selenium extension. Only values from ["chrome", "firefox"] are supported.

"-e", "--linkedIn-email" (default=None, required=True) - The linkedIn email to access linkedIn page.

"-p", "--linkedIn-password" (default=None, required=True) - The linkedIn password corresponding to provided email.

### Execute the script

To execute the script use the command:

    python3 main.py -n "<NAME_OF_THE_SPREADSHEET>" -k "ABSOLUTE_PATH_TO_THE_JSON_GOOGLE_SHEETS_API_KEY" -b "chrome" -e "<LINKEDIN_EMAIL>" -p "<LINKEDIN_PASSWORD>"

    
    

