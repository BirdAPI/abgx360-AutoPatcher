from BeautifulSoup import BeautifulSoup
import urllib
import urllib2
import platform
import sys
import re
import os

def get_top_search_result(game_name):
    url = "http://abgx360.net/verified.php?f=name&q=%s" % (game_name.replace(" ", "+"))
    try:
        html = urllib2.urlopen(url).read()
        soup = BeautifulSoup(html)
        even = soup.find(attrs = { "class" : "even" })
        tds = even.findAll("td")
        game = tds[1].text
        last_td = tds[len(tds) - 1]
        a = last_td.find('a')
        href = a["href"]
        link = "http://abgx360.net" + href
        return (game, link)
    except: 
        return (None, None)

def get_first_ssv2(ss_link):
    try:
        html = urllib2.urlopen(ss_link).read()
        soup = BeautifulSoup(html)
        evens = soup.findAll(attrs = { "class" : "even" })
        for even in evens:
            tds = even.findAll("td");
            if tds[0]["class"] == "rf" and tds[0].text == "2":
                ss = "http://abgx360.net" + tds[1].find("a")["href"]
                dmi = "http://abgx360.net" + tds[2].find("a")["href"]
                return (ss, dmi)
    except: 
        return (None, None)

def download_file(link, dest_dir):
    dest_dir = dest_dir.replace("\\", "/")
    if dest_dir != "" and dest_dir[len(dest_dir) - 1] != "/":
        dest_dir = dest_dir + "/"
    ensure_dir_exists(dest_dir)
    destname = dest_dir + get_filename_from_url(link)
    urllib.urlretrieve(link, destname)
    return destname

def get_filename_from_url(url):
    tokens = url.replace("\\", "/").split("/")
    return tokens[len(tokens) - 1]

def ensure_dir_exists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def get_first_game_patches(search):
    (game, link) = get_top_search_result(search)
    if game is not None:
        print game + ": " + link
        (ss, dmi) = get_first_ssv2(link)
        if ss is not None and dmi is not None:
            print "SS: " + ss
            print "DMI: " + dmi
            patch_path = "C:/Dirt 3/Patches"
            ss_filename = download_file(ss, patch_path)
            print "Downloaded: " + ss_filename
            dmi_filename = download_file(dmi, patch_path)
            print "Downloaded: " + dmi_filename
            return (ss_filename, dmi_filename)
        else:
            print "No SSv2 Patches Found!"
            return (None, None)
    else:
        print "No Results: " + search
        return (None, None)

def get_abgx360_exe():
    return "C:/Windows/SysWOW64/abgx360.exe" if is_64bit() else "C:/Windows/System32/abgx360.exe"
        
def is_64bit():
    return platform.architecture()[0] == "64bit"

def verify_stealth(iso):
    exe = get_abgx360_exe()
    args = '-vthi -- "%s"' % iso
    output = os.popen(exe + " " + args).read()
    write_to_file(output, os.path.dirname(iso) + "/abgx360_verify.html")   
    
def stealth_patch_ssv2(iso, ss, dmi):
    exe = get_abgx360_exe()
    args = '-vthi --noverify --patchitanyway --p-dmi "%s" --p-ss "%s" -- "%s"' % (dmi, ss, iso)
    output = os.popen(exe + " " + args).read()
    write_to_file(output, os.path.dirname(iso) + "/abgx360_patch.html")

def write_to_file(text, filename):
    localFile = open(filename, "w")
    localFile.write(text)
    localFile.close()
    
def main():
    if len(sys.argv) == 3:
        print "64 bit" if is_64bit() else "32 bit"
        iso = sys.argv[2]
        if os.path.exists(iso):
            (ss_filename, dmi_filename) = get_first_game_patches(sys.argv[1])
            if ss_filename is not None and dmi_filename is not None:
                print "Patching: %s to SSv2..." % iso
                stealth_patch_ssv2(iso, ss_filename, dmi_filename)
                print "Done patching to SSv2."
                print "Verifying: %s..." % iso
                verify_stealth(iso)
                print "Done verifying iso."
        else:
            print "ISO file does not exist!"
    else:
        print 'Usage: python abgx360.py "Game Name" "Game.iso"'
    
if __name__ == "__main__":
    main()
    