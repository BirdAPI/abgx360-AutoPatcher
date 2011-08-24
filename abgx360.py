from BeautifulSoup import BeautifulSoup
import urllib2
import sys
import re
import os

def get_top_search_result(game_name):
    url = "http://abgx360.net/verified.php?f=name&q=%s" % (game_name.replace(" ", "+"))
    try:
        html = urllib2.urlopen(url).read()
    except: return
    soup = BeautifulSoup(html)
    even = soup.find(attrs = { "class" : "even" })
    tds = even.findAll("td")
    game = tds[1].text
    last_td = tds[len(tds) - 1]
    a = last_td.find('a')
    href = a["href"]
    link = "http://abgx360.net" + href
    return (game, link)

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

def download_file(link, dest_dir):
    u = urllib2.urlopen(link)
    dest_dir = dest_dir.replace("\\", "/")
    if dest_dir != "" and dest_dir[len(dest_dir) - 1] != "/":
        dest_dir = dest_dir + "/"
    ensure_dir_exists(dest_dir)
    destname = dest_dir + get_filename_from_url(link)
    localFile = open(destname, "w")
    localFile.write(u.read())
    localFile.close()

def get_filename_from_url(url):
    tokens = url.replace("\\", "/").split("/")
    return tokens[len(tokens) - 1]

def ensure_dir_exists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    
def main():
    if len(sys.argv) == 2:
        (game, link) = get_top_search_result(sys.argv[1])
        print game + ": " + link
        (ss, dmi) = get_first_ssv2(link)
        print "SS: " + ss
        print "DMI: " + dmi
        download_file(ss, "Patches/" + game)
        download_file(dmi, "Patches/" + game)
    else:
        print "Usage: abgx360.py game_name"
    
if __name__ == "__main__":
    main()
    