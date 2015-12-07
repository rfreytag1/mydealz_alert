#!/usr/bin/python
'''
The MIT License (MIT)

Copyright (c) 2015 Roy Freytag

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import pycurl
from io import BytesIO
from bs4 import BeautifulSoup
import re
import datetime
from collections import deque
from gi.repository import Notify, Gtk, GObject
import webbrowser
import signal

def hasNumbers(inputstr):
	return any(char.isdigit() for char in inputstr)
		
class MainClass(GObject.GObject):

	def __init__(self):
		super().__init__()
		Notify.init("dealnoti")
		
		self.alreadyseen = deque(maxlen=20)
		self.notis = deque(maxlen=40)
		
		GObject.timeout_add_seconds(60*5, self.on_timeout)

		self.on_timeout()

	def findDeal(self, body, needle, maxprice):
		soup = BeautifulSoup(body, 'html.parser')
		listings = soup.find("main", id="main").find("ol")
		if listings is None:
			print("Kein Angebotsteil!")
			return

		elements = listings.find_all("a", text=re.compile("(?i).*("+needle+").*"), class_=re.compile("section-title-link"))
		deals = []
		for deal in elements:
			title = deal.string
			link = deal.get("href")
			pricestr = deal.parent.parent.find("strong", class_=re.compile("thread-price")).string.strip()
			if("€" in pricestr):
				price = float(pricestr.replace('\xa0€', '').replace('.', '').replace(',', '.'))
			else:
				price = 0
			timestr = deal.parent.parent.parent.find("span", class_=re.compile("thread-time")).string.strip()

			if((price < maxprice or maxprice == -1.0) and (link not in self.alreadyseen)):
				deals.append((title, link, pricestr, timestr))
				self.alreadyseen.append(link)
		return deals

	def fetchWebsite(self):
		buffer = BytesIO()
		cu = pycurl.Curl()
		cu.setopt(cu.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1')
		cu.setopt(cu.URL, 'http://www.mydealz.de/deals-new')
		cu.setopt(cu.WRITEDATA, buffer)
		cu.perform()
		cu.close()

		body = buffer.getvalue().decode("UTF-8")
		return body

	def readWantedDeals(self):
		f = open("/etc/mydealz/wanted.txt", "r")
		wantedlist = []
		for line in f:
			tup = line.rstrip().split(";")
			if(isinstance(tup, list) and len(tup) > 1 and hasNumbers(tup[1])):
				maxprice = float(tup[1].replace("€", "").replace(".", "").replace(",", "."))
			else:
				maxprice = -1.0
			wantedlist.append((tup[0].strip(), maxprice))


		f.close()
		'''
		for tup in wantedlist:
			print((tup[0] + " " + str(tup[1]) + "€"))
		'''
		return wantedlist

	def on_timeout(self):
		wlist = self.readWantedDeals()
		#print(datetime.datetime.now().strftime("%H:%M:%S"))
		website = self.fetchWebsite()
		for wanted in wlist:
			deals = self.findDeal(website, wanted[0], wanted[1])
			if(len(deals) > 0):
				#print("Deals für Filter \""+wanted[0] + " < " + str(wanted[1]) + "€\":")
				for deal in deals:
					#print("\t" + deal[3] + ": " + deal[0] + "\n\t" + deal[1] + "\n\t" + deal[2] + "\n")
					dealnoti = Notify.Notification.new("MyDealz Deal gefunden",  datetime.datetime.now().strftime("%H:%M:%S\n") + deal[0] + " für " + deal[2] + "\n" + deal[3])
					dealnoti.set_timeout(1000*60*30) #keep notification open for 30mins
					dealnoti.add_action("visit-deal", "Deal öffnen", self.on_openlink, deal[1])
					self.notis.append(dealnoti)
					dealnoti.show()

	def on_openlink(self, noti, action, userdata = None):
		print("Callback called:"+action)
		webbrowser.open(userdata, new = 2)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	mainloop = MainClass()
	Gtk.main()

