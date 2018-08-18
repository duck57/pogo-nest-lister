#!/usr/bin/env python3
# coding=UTF-8
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import os
import importlib
import datetime
import click
from sortedcontainers import SortedList
from collections import defaultdict
import csv
import sqlite3
from sqlite3 import Error
import pyperclip
import rotate as dateparse
import importoldlists as dbutils

nested_dict = lambda: defaultdict(nested_dict)
global private_reminder, ghost_icon, giraffe_icon, smallwhale, largewhale, rat_icon, hoothoot
private_reminder = '☝'  # maybe this should be in a config file in the future
ghost_icon = '👻'
giraffe_icon = '🦒'
smallwhale = '🐳'
largewhale = '🐋'
rat_icon = '🐀'
hoothoot = '🦉'

'''
Takes the city and date and outputs the FB-formatted nest post
If no date given, pulls from the most-recent nest list prior to today
If a date is given, pulls from the most recent nest list prior to that date
If no lists are older than the specified date, output error and use oldest available list
'''


# check that you're running a valid city
def city_folder_check(city, prefix):
    cfolder = prefix + city + "/"
    if os.path.exists(cfolder) is False:
        print("There is no folder for " + city +
              " in the " + prefix + " directory")
        return False

    # ignore .hidden files and folders
    files = 0
    for f in os.listdir(cfolder):
        if not f.startswith('.') and os.path.isfile(cfolder + f):
            files += 1

    if files == 0:
        print("There are no nest records in " + city + "'s folder")
        return False
    return True


# ensures you have a valid city folder
def choose_folder(city=None):
    prefix = dateparse.outpath
    while True:
        if city is not None and city_folder_check(city, prefix) is True:
            return city, prefix + city + "/"
        city = input("Which city's nests do you want to list? ")


# decorates a string of text by inserting it halfway between the decoration string
def decorate_text(text, decor):
    stl = len(decor)//2
    return decor[:stl] + text + decor[stl:]


# finds the closest matching nest list to the given date
def find_nest_list(path, date):
    searchlist = SortedList()
    for file in os.listdir(path):
        if not file.startswith('.') and os.path.isfile(path + file):
            searchlist.add(file)

    # ZZZ to ensure it goes after other files
    loc = searchlist.bisect_right(str(date) + "ZZZ ") - 1
    if loc < 0:
        print("Date " + str(date) +
            " is prior to any stored rotations.  Using oldest available data instead.")
        loc = 0
    recentrotation = searchlist[loc].split(".")[0]
    return dateparse.getdate(recentrotation), path + searchlist[loc]


# checks a nest's status: 0 for no info, 1 for unconfirmed, 2 for confirmed
def assign_status(species, confirmation):
    if species.strip() == "":
        return 0
    if true_if_Y(confirmation):
        return 2
    return 1


# returns True if it's a Y
def true_if_Y(str):
    if str.strip() == "":
        return False
    if str[0].upper() == 'Y':
        return True
    return False


# loads the nests from a file into memory and separates them by city and status
def load_nests(nestfile):
    nestlist = nested_dict()
    empties = nested_dict()
    f = open(nestfile, 'r')
    nests = csv.DictReader(f, delimiter="\t")
    for nest in nests:
        loc = nest["Location"].strip()
        if loc == "":
            loc = "ZZZZZZNo location information"  # sort at the end
        stat = assign_status(nest["Species"], nest["Confirm?"])
        name = nest["Primary Name"].strip()
        if stat == 0:
            list = empties
        else:
            list = nestlist
        list[loc][name]["Private"] = true_if_Y(nest["Private Property?"])
        list[loc][name]["Alt"] = nest["Alternate Name"].strip()
        list[loc][name]["Note"] = nest["Notes"].strip()
        list[loc][name]["Species"] = nest["Species"].strip()
        list[loc][name]["Status"] = stat
    f.close()
    return nestlist, empties


# converts the status into text
def disp_status(statnum):
    if statnum == 0:
        return "No information"
    if statnum == 1:
        return "Unconfirmed"
    if statnum == 2:
        return "Confirmed"
    return "Invalid data"


# generates a parenthetical containing notes and a private property notice when needed
# assumes at least one of these is true or populated
def gen_parenthetical(notes, private):
    privatenotice = "Private property—please be respectful"
    if notes == "":
        return decorate_text(privatenotice, "()")
    if not private:
        return decorate_text(notes, "()")
    combined = notes + "; " + privatenotice.lower()
    return decorate_text(combined, "()")


# outputs the formatted nest list for the FB post
# nnl stands for Nested Nest List
def FB_format_nests(nnl):
    list = ""
    for location in sorted(nnl.keys()):
        # use "ZZZ" instead of just "Z" to accommodate Zanesville
        # and any city that two consecutive Z in its name
        list += decorate_text(location.split("ZZZ")[-1], "{~()~}") + '\n'
        for nestname in nnl[location]:
            status = nnl[location][nestname]["Status"]
            nest = nnl[location][nestname]
            if nest["Ghost"]:
                list += ghost_icon
            if nest["Private"]:
                list += private_reminder  # private property reminder
            list += nestname  # nest name
            if nest["Alt"] != "":
                list += "/" + nest["Alt"]
            if nest["Note"] is not None and nest["Note"] != "":
                list += " " + gen_parenthetical(nest["Note"], '')
            list += ": " + nest["Species"]
            if status == 1:
                list += "*"
            list += '\n'  # prepare for next item
        list += '\n'
    return list


def FB_empty(empties):
    list = decorate_text("No Reports", "[--  --]") + '\n'
    for location in sorted(empties.keys()):
        list += "• " + location + ": "
        first = True
        for park in sorted(empties[location].keys()):
            if first is False:
                list += ","
            list += " " + (private_reminder if empties[location][park]["Private"] else '') + park
            first = False
        list += '\n'
    return list


def make_summary(nnl):
    summary = nested_dict()
    for location in nnl.keys():
        for park in nnl[location].keys():
            summary[nnl[location][park]["Species"]][park] = nnl[location][park]["Status"]
    return summary


def FB_summary(summary):
    out = decorate_text("Summary", "[--  --]")
    for species in sorted(summary.keys()):
        spico = ''
        if summary[species]["-Spooked"] is True:
            spico = ghost_icon
        elif species == "Walimer":
            spico = smallwhale
        elif species == "Girafarig":
            spico = giraffe_icon
        elif species == "Hoothoot":
            spico = hoothoot
        elif species == "Rattata":
            spico = rat_icon
        out += "\n" + spico + species + ":"
        first = True
        for park in sorted(summary[species].keys()):
            if park == "-Spooked":
                continue
            if first is False:
                out += ","
            if summary[species][park]["Private"]:
                out += private_reminder
            out += " " + park
            if summary[species][park] == 1:
                out += "*"
            first = False
    out += "\n\n"
    return out

# Preamble for FB post
# dates here should be previously-formatted as strings
def FB_preamble(updated8, rotationday):
    out = "#Nests #Tracking #Migration\n"
    out += "* = Unconfirmed, "
    out += private_reminder + "️ = Private property, please be respectful\n"
    out += rotationday + " nest shift\n"
    out += "Last updated: " + updated8 + "\n\n"
    return out


# Preamble for Discord
def disc_preamble(updated8, rotationday):
    out = decorate_text(rotationday, "``") + " nest shift\n"
    out += "Last updated: " + updated8 + "\n\n"
    out += "**Bold** species are confirmed; _italic_ are single-reported\n\n"
    return out


# discord post of top/important species & parks
# maybe this should be from a config file?
def disc_important_species(slist):
    important_species = ["Magikarp","Walimer","Water Biome"]
    out = decorate_text("Popular Species", "__****__")
    count = 0
    for species in sorted(slist.keys()):
        if species not in important_species and slist[species]["-Spooked"] is not True:
           continue
        count += 1
        out += '\n• ' + species + ": "
        first = True
        for park in slist[species]:
            if park == "-Spooked":
                continue
            if first is False:
                out += ', '
            out += decorate_text(park, '****' if slist[species][park]["Status"] == 2 else '__')
            first = False
    if count == 0:
        return ''
    return out



# generate and copy a Discord post to the clipboard
# assumes all lines are roughly the same length and you don't troll
# with a 2000+ chars line for a single region
def disc_posts(nnl2, rundate, shiftdate, slist=None):
    list = []
    olen = 0
    max = 2000  # Discord post length limit
    pre = disc_preamble(rundate, shiftdate)
    olen += len(pre)
    list.append('')  # this is required for things to split up right later
    list.append(pre)

    for loc in sorted(nnl2.keys()):
        loclst = decorate_text(loc, '__****__') + '\n'
        for nestname in sorted(nnl2[loc].keys()):
            loclst += nestname
            nest = nnl2[loc][nestname]
            if nest["Alt"] != '':
                loclst += '/' + str(nest["Alt"])
            loclst += ": " + decorate_text(nest["Species"], '****' if nest["Status"] == 2 else '__') + '\n'
        if len(loclst) > 2000:
            raise Exception("Nest list for sub-region " + loc + """ exceeds 2000 characters,
            which causes Discord problems.  Consider breaking into smaller areas.""")
        olen += len(loclst)
        list.append(loclst)

    start = 0
    end = 0
    num = olen//max + 1
    trg = olen//num
    outparts = []
    pts = len(list)//num
    ix = 0
    count = 0
    tmpstr = ""
    for nbh in list:
        if len(nbh) + count < max and count <= trg:
            tmpstr += nbh
            count += len(nbh)
        else:
            outparts.append(tmpstr)
            tmpstr = nbh
            count = 0
            ix += 1
    outparts.append(tmpstr)

    outparts.append(disc_important_species(slist))

    pos = 0
    num = len(outparts)
    for part in outparts:
        pyperclip.copy(part)
        pos += 1
        if pos < num:
            input("Copied part " + str(pos) + " of " + str(num) + " to the clipboard. Press enter or return to continue.")
        else:
            print("Copied part " + str(num) + " of " + str(num) + " to the clipboard.")


# generate and copy a FB post to the clipboard
def FB_post(nnl, rundate, shiftdate, mt=None, slist=None):
    post = FB_preamble(rundate, shiftdate)
    if slist is not None:
        post += FB_summary(slist)
        post += decorate_text(" • ", "---==<>==---") + "\n\n"
    post += FB_format_nests(nnl)
    if mt is not None:
        # post += decorate_text(" • ", "---==<>==---") + "\n\n"
        post += FB_empty(mt)
    pyperclip.copy(post)
    print("Nest list copied to clipboard")


# select the most recent date on or before the supplied date from the database
# returns the rotation number and the corresponding YYYY-MM-DD date
def get_rot8d8(today, dbc):
    sql = "SELECT * FROM rotation_dates WHERE date <= ? ORDER BY date DESC LIMIT 1"
    cur = dbc.cursor()
    cur.execute(sql, [today])
    res = cur.fetchall()
    if len(res) > 0:
        return res[0][0], res[0][1]
    print("Date " + today + " is older than anything in the database.  Using oldest data instead.")
    sql = "SELECT * FROM rotation_dates LIMIT 1"
    cur.execute(sql)
    res = cur.fetchall()
    return res[0][0], res[0][1]


# returns the nest's location from the SQL data
# assumes neighborhood & region data are names (not IDs) in positions 7 & 8
def get_sortloc(nestrow):
    if nestrow[7] is None:
        return "ZZZZZZNo location information"
    elif nestrow[8] is None:
        return nestrow[7]
    else:
        return nestrow[8]


# turns a SQL result nest row into an NNL entry
# the dbc is only necessary if you want to look up and include alternate names
def nstrw2nnl(nestrow, dbc=None):
    nst = nested_dict()
    nst["Official Name"] = nestrow[3]
    nst["Short Name"] = nestrow[4]
    nst["Neighborhood"] = nestrow[7]
    nst["Region"] = nestrow[8]
    nst["Species"] = nestrow[0]
    nst["Private"] = nestrow[6]
    nst["Note"] = nestrow[5]
    nst["Status"] = 2 if nestrow[1] == 1 else 1
    nst["Ghost"] = True if (nestrow[10] == 'Ghost' or nestrow[11] == 'Ghost') else False
    nst["SpNum"] = nestrow[9]
    if dbc is None:
        nst["Alt"] = ''
        return nst
    slalts = "SELECT name FROM alt_names WHERE main_entry = ?"
    cur = dbc.cursor()
    cur.execute(slalts, [nestrow[2]])
    rawalt = cur.fetchall()
    altlst = []
    for alt in rawalt:
        altlst.append(alt[0])
    nst["Alt"] = '/'.join(altlst)
    return nst


# prefers the short name over primary name currently
def nestname(nestrow):
    return nestrow[4] if nestrow[4] is not None else nestrow[3]


# returns the nested nest list and stack of empties
def get_nests(rotnum, dbc):
    nestout = nested_dict()
    nestmt  = nested_dict()
    ssumry  = nested_dict()
    sqnests = """SELECT
                    sl.species_txt AS Species --0
                    ,sl.confirmation AS 'Confirmed?' --1
                    ,nls.nest_id --2
                    ,nls.official_name AS 'Primary Name' --3
                    ,nls.short_name AS 'Short Name' --4
                    ,nls.notes AS 'Park Notes' --5
                    ,nls.private AS 'Private Property?' --6
                    ,nbz.name AS 'Neighborhood' --7
                    ,regions.name AS 'Location' --8
                    ,nsp.`#` AS Dex --9
                    ,nsp.Type --10
                    ,nsp.Subtype --11
                FROM species_list AS sl
                    LEFT OUTER JOIN nest_locations AS nls ON (sl.nestid = nls.nest_id)
                    LEFT OUTER JOIN neighborhoods AS nbz ON (nls.location = nbz.id)
                    LEFT OUTER JOIN regions ON (nbz.region = regions.id)
                    LEFT OUTER JOIN nesting_species AS nsp ON (sl.species_no = nsp.`#`)
                WHERE sl.rotation_num = ?"""
    sqmt = """SELECT
                NULL,NULL --fill in for 0 and 1
                ,nls.nest_id --2
                ,nls.official_name AS 'Primary Name' --3
                ,nls.short_name AS 'Short Name' --4
                ,nls.notes AS 'Park Notes' --5
                ,nls.private AS 'Private Property?' --6
                ,nbz.name AS 'Neighborhood' --7
                ,regions.name AS 'Location' --8
                ,NULL,NULL,NULL --filler for 9,10,11
            FROM nest_locations AS nls
                LEFT OUTER JOIN neighborhoods AS nbz ON (nls.location = nbz.id)
                LEFT OUTER JOIN regions ON (nbz.region = regions.id)
            WHERE nls.nest_id NOT IN (
                SELECT nestid FROM species_list
                WHERE rotation_num = ?
            )"""
    for nestrow in dbc.execute(sqnests, [rotnum]):
        nestdct = nstrw2nnl(nestrow, dbc)
        nestout[get_sortloc(nestrow)][nestname(nestrow)] = nestdct
        ssumry[nestrow[0]][nestname(nestrow)] = nestdct
        if nestdct["Ghost"]:
            ssumry[nestrow[0]]["-Spooked"] = True
    for nestrow in dbc.execute(sqmt, [rotnum]):
        nestmt[nestrow[7]][nestname(nestrow)] = nstrw2nnl(nestrow, dbc)
    return nestout, nestmt, ssumry


@click.command()
@click.option(
        '-d',
        '--date',
        default=str(datetime.datetime.today().date()),
        prompt="Generate list of nests as of this date",
        help="Generate list of nests as of this date"
        )
@click.option(
    '-o',
    '--format',
    type=click.Choice(['FB', 'Facebook', 'f', 'd', 'Discord', 'disc']),
    prompt="Output format",
    help="Specify the output formatting for the nest list")
# main method
def main(city=None, date=None, format=None):
    date = dateparse.getdate(date)
    rundate = date.strftime('%d %b %Y')
    print("Gathering nests as of " + rundate)
    dbfile = "nests.db"
    dbc = dbutils.create_connection(dbfile)
    if dbc is None:
        print("Error creating database")
        return None

    rotnum, shiftdate = get_rot8d8(date, dbc)
    nests, empties, species = get_nests(rotnum, dbc)
    print("Using the nest list from the " + shiftdate + " nest rotation")
    if format[0].lower() == 'f':
        format_name = "Facebook"
        FB_post(nests, rundate, shiftdate, slist=species, mt=empties)
    if format[0].lower() == 'd':
        format_name = "Discord"
        disc_posts(nests, rundate, shiftdate, slist=species)


if __name__ == "__main__":
    main()
