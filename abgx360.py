from BeautifulSoup import BeautifulSoup
import urllib2

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
    
def main():
    print get_top_search_result("dirt")

if __name__ == "__main__":
    main()
    