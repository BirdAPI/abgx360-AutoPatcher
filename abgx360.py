from BeautifulSoup import BeautifulSoup
import urllib2
import sys
import re

def get_top_search_result(game_name):
    url = "http://abgx360.net/verified.php?f=name&q=%s" % (game_name.replace(" ", "+"))
    try:
        html = urllib2.urlopen(url).read()
    except: return
    soup = BeautifulSoup(html)
    even = soup.find(attrs = { "class" : "even" })
    tds = even.findAll("td")
    last_td = tds[len(tds) - 1]
    a = last_td.find('a')
    href = a["href"]
    link = "http://abgx360.net" + href
    return link

def get_first_ssv2(ss_link):
    try:
        html = urllib2.urlopen(ss_link).read()
    except: return
    soup = BeautifulSoup(html)
    evens = soup.findAll(attrs = { "class" : "even" })
    for even in evens:
        tds = even.findAll("td");
        if tds[0]["class"] == "rf" and tds[0].text == "2":
            ss = "http://abgx360.net" + tds[1].find("a")["href"]
            dmi = "http://abgx360.net" + tds[2].find("a")["href"]
            return (ss, dmi)
    
def main():
    link = get_top_search_result("dirt")
    print "Found: " + link
    (ss, dmi) = get_first_ssv2(link)
    print "SS: " + ss
    print "DMI: " + dmi
    
if __name__ == "__main__":
    main()
    