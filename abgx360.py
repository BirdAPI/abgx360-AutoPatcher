#!/usr/bin/python

from bs4 import BeautifulSoup
import platform
import sys
import re
import os
import urllib.request


def get_xex_crc(iso):
    exe = get_abgx360_executable()
    args = '-rg --noverify -- "%s"' % iso
    output = os.popen(exe + " " + args).read()
    match = re.search("XEX CRC = (?P<xex>[^  \n]+)", output)
    if match:
        return match.group("xex").strip()
    else:
        return None


def get_game_from_xex(xex):
    return xex, "http://abgx360.net/verified.php?f=pressings&q=" + xex


def search_by_xex(iso):
    xex = get_xex_crc(iso)
    if xex:
        print("Found XEX CRC: " + xex)
        return get_game_from_xex(xex)
    else:
        print("ERROR: No XEX CRC found for ISO!")
        return None, None


def get_first_ssv2(ss_link):
    html = urllib.request.urlopen(ss_link).read()
    soup = BeautifulSoup(html)
    evens = soup.findAll(attrs={"class": "even"})
    for even in evens:
        tds = even.findAll("td")
        if tds[0]["class"] == ['rf'] and tds[0].text == '2':
            ss = "http://abgx360.net" + tds[1].find("a")["href"]
            dmi = "http://abgx360.net" + tds[2].find("a")["href"]
            return ss, dmi
    return None, None


def download_file(link, dest_dir):
    ensure_dir_exists(dest_dir)
    dest_name = os.path.join(dest_dir, get_filename_from_url(link))
    urllib.request.urlretrieve(link, dest_name)
    return dest_name


def get_filename_from_url(url):
    tokens = url.replace("\\", "/").split("/")
    return tokens[len(tokens) - 1]


def ensure_dir_exists(dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)


def get_xex_game_patches(iso):
    xex, link = search_by_xex(iso)
    if link is not None:
        print("Verified: " + link)
        ss, dmi = get_first_ssv2(link)
        if ss is not None and dmi is not None:
            print("SS: " + ss)
            print("DMI: " + dmi)
            patch_path = os.path.join(os.path.dirname(iso), xex + "_SSv2")
            ss_filename = download_file(ss, patch_path)
            print("Downloaded: " + ss_filename)
            dmi_filename = download_file(dmi, patch_path)
            print("Downloaded: " + dmi_filename)
            return xex, ss_filename, dmi_filename
        else:
            print("No SSv2 Patches Found!")
            return None, None, None
    else:
        print("No Results: " + iso)
        return None, None, None


def get_abgx360_executable():
    if sys.platform == "linux" or sys.platform == "linux2":
        # Linux
        return "/usr/local/bin/abgx360"
    elif sys.platform == "darwin":
        # OS X
        return "/usr/bin/abgx360"
    elif sys.platform == "win32":
        # Windows
        if os_bits() == 64:
            return "C:/Windows/SysWOW64/abgx360.exe"
        else:
            return "C:/Windows/System32/abgx360.exe"


def os_bits():
    machine2bits = {'AMD64': 64, 'x86_64': 64, 'i386': 32, 'x86': 32}
    return machine2bits.get(platform.machine(), None)


def verify_stealth(iso, xex):
    exe = get_abgx360_executable()
    args = '-vchi --embed --aa --ach -- "%s"' % iso
    output = os.popen(exe + " " + args).read()
    log_name = os.path.join(os.path.dirname(iso), xex + "_verify.html")
    write_to_file(output, log_name)
    return log_name


def stealth_patch_ssv2(iso, ss, dmi, xex):
    exe = get_abgx360_executable()
    args = '-vhi --noverify --patchitanyway --embed --p-dmi "%s" --p-ss "%s" -- "%s"' % (dmi, ss, iso)
    output = os.popen(exe + " " + args).read()
    log_name = os.path.join(os.path.dirname(iso), xex + "_patch.html")
    write_to_file(output, log_name)
    return log_name


def was_patch_successful(patch_html_log):
    ss_success = False
    dmi_success = False
    html = open(patch_html_log, "r").read()
    soup = BeautifulSoup(html)
    greens = soup.findAll(attrs={"class": "green"})
    for green in greens:
        msg = green.text.strip()
        if msg == "Patching SS was successful":
            print("Patching SS was successful")
            ss_success = True
            if dmi_success:
                return True, True, True
        elif msg == "Patching DMI was successful":
            print("Patching DMI was successful")
            dmi_success = True
            if ss_success:
                return True, True, True
    return False, ss_success, dmi_success


def is_stealth_verified(verify_html_log, verify_ss2):
    ss2 = False
    crc_match = False
    verification = False
    splitvid = False
    html = open(verify_html_log, "r").read()
    soup = BeautifulSoup(html)
    normals = soup.findAll(attrs={"class": "normal"})
    for normal in normals:
        msg = normal.text.strip()
        if msg.find("SS Version: 2 (trusted)") != -1:
            print("SS Version: 2 (trusted)")
            ss2 = True
            break
    greens = soup.findAll(attrs={"class": "green"})
    for green in greens:
        msg = green.text.strip()
        if msg == "All CRCs match":
            print("All CRCs match")
            crc_match = True
        elif msg == "Verification was successful!":
            print("Verification was successful!")
            verification = True
        elif msg == "SplitVid is valid":
            print("SplitVid is valid")
            splitvid = True
    return (ss2 or not verify_ss2) and crc_match and verification and splitvid, ss2, crc_match, verification, splitvid


def is_ap25_game(verify_html_log):
    # TODO
    return False


def write_to_file(text, filename):
    local_file = open(filename, "w")
    local_file.write(text)
    local_file.close()


def automate_search(iso):
    if os.path.exists(iso):
        xex, ss_filename, dmi_filename = get_xex_game_patches(iso)
        if ss_filename is not None and dmi_filename is not None:
            print("Patching: %s to SSv2..." % iso)
            patch_html_log = stealth_patch_ssv2(iso, ss_filename, dmi_filename, xex)
            print("Done patching to SSv2.")
            patch_success = was_patch_successful(patch_html_log)
            if patch_success:
                print("Patching was successful!")
                print("Verifying: %s..." % iso)
                verify_html_log = verify_stealth(iso, xex)
                print("Done verifying iso.")
                stealth_success = is_stealth_verified(verify_html_log, True)
                if stealth_success:
                    print("Stealth check passed!")
                else:
                    print("ERROR: Stealth check failed!")
            else:
                print("ERROR: Patching Failed!")
    else:
        print("ISO file does not exist!")


def main():
    if len(sys.argv) == 2:
        exe = get_abgx360_executable()
        print("%s bit - %s" % (os_bits(), exe))
        if os.path.exists(exe):
            iso = sys.argv[1]
            automate_search(iso)
        else:
            print('ERROR: abgx360 could not be found on your system.')
    else:
        print('Usage: python abgx360.py "Game.iso"')


if __name__ == "__main__":
    main()