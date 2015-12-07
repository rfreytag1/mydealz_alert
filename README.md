# MyDealz Alert
This is a small Python 3 script that searches mydealz.de for things you want at a certain maximum price point and then displays
a notification via GTK with a description and the link to the MyDealz.de page. It only scans the very first page of the newest
deals page, since deals older than that are mostly gone anyway. It checks the website every 5 minutes, so it should be fine.

This is in no way affiliated with MyDealz.de, it's simply a little script I personally wrote for myself to avoid missing dealz 
that I'm interested in. The script directly links to the MyDealz.de deal page.

## Requirements
You'll need the following libraries to use this:

* BeautifulSoup
* PyGTK
* PycURL

simply install them with `pip install`

## Usage
The script uses a file called `wanted.txt` in which you specify what deals you want. It needs to be located in `/etc/mydealz/`.
It's a simple semi-colon seperated list of regular expressions and the maximum price you want. Each line is a new desired deal.
The regular expressions are matched without case sensitivity.
A simple example that will search for cameras with a price below 300€ and some 1000GB SSD below 250€ would look like this:

    (camera);300€
    (((ssd).*1000.*(gb)?)|(1000.*(gb)?.*(ssd)));250€

## Ubuntu
Since Ubuntu still has an old version of BeautifulSoup in its repositories, the search
for deals will return no result. There's a fix for that in the branch `pre-bs4.4.0`
