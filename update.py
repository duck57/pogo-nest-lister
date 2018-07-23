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
import pyperclip
import rotate as dateparse

nested_dict = lambda: defaultdict(nested_dict)

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
def FB_format_nests(nnl, empties):
    list = ""
    for location in sorted(nnl.keys()):
        # use "ZZZ" instead of just "Z" to accommodate Zanesville
        # and any city that two consecutive Z in its name
        list += decorate_text(location.split("ZZZ")[-1], "{~()~}") + '\n'
        for nestname in nnl[location]:
            status = nnl[location][nestname]["Status"]
            nest = nnl[location][nestname]
            list += nestname  # nest name
            if nest["Alt"] != "":
                list += "/" + nest["Alt"]
            if nest["Note"] != "" or nest["Private"]:
                list += " " + gen_parenthetical(nest["Note"], nest["Private"])
            list += ": " + nest["Species"]
            if status == 1:
                list += "*"
            list += '\n'  # prepare for next item
        list += '\n'
    if len(empties) == 0:
        return list
    list += decorate_text("No Reports", "[--  --]") + '\n'
    for location in sorted(empties.keys()):
        list += "• " + location + ": "
        first = True
        for park in sorted(empties[location].keys()):
            if first is False:
                list += ","
            list += " " + park
            first = False
        list += '\n'
    return list


def make_summary(nnl):
    summary = nested_dict()
    for location in nnl.keys():
        for park in nnl[location].keys():
            status = nnl[location][park]["Status"]
            #if status == 0:  # remove empty nests
            #    continue  # there shuold no longer be empty nests in the main list
            summary[nnl[location][park]["Species"]][park] = status
    return summary

def FB_summary(nnl):
    summary = make_summary(nnl)
    out = decorate_text("Summary", "[--  --]")
    for species in sorted(summary.keys()):
        out += "\n" + species + ":"
        first = True
        for park in sorted(summary[species].keys()):
            if first is False:
                out += ","
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
    out += "* = Unconfirmed\n"
    out += rotationday + " nest shift\n"
    out += "Last updated: " + updated8 + "\n\n"
    return out


# Preamble for Discord
def disc_preamble(updated8, rotationday):
    out = decorate_text(rotationday, "``") + " nest shift\n"
    out += "Last updated: " + updated8 + "\n\n"
    out += "**Bold** species are confirmed; _italic_ are single-reported\n\n"
    return out


# generate and copy a Discord post to the clipboard
# assumes all lines are roughly the same length and you don't troll
# with a 2000+ chars line for a single region
def disc_posts(listfile, rundate, shiftdate):
    nnl2, _ = load_nests(listfile)  # 2 to match other naming conventions
    list = []
    olen = 0
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
    num = olen//2000 + 1
    pts = len(list)//num
    for pos in range(num):
        start = pos*pts + 1
        end = start + pts
        pyperclip.copy(''.join(list[start:end]))
        if pos+1 < num:
            input("Copied part " + str(pos+1) + " of " + str(num) + " to the clipboard. Press enter or return to continue.")
        else:
            print("Copied part " + str(num) + " of " + str(num) + " to the clipboard.")


# generate and copy a FB post to the clipboard
def FB_post(listfile, rundate, shiftdate):
    nnl, nulls = load_nests(listfile)
    output = FB_format_nests(nnl, nulls)
    summary = FB_summary(nnl)
    pyperclip.copy(FB_preamble(rundate, shiftdate) + summary + decorate_text(" • ", "---==<>==---") + "\n\n" + output)
    print("Nest list copied to clipboard")


@click.command()
@click.option(
        '-d',
        '--date',
        default=str(datetime.datetime.today().date()),
        prompt="Generate list of nests as of this date",
        help="Generate list of nests as of this date"
        )
@click.option(
        '-c',
        '--city',
        '-f',
        prompt="Generate nest list of this city",
        help="Specify city for list generation"
        )
@click.option(
    '-o',
    '--format',
    type=click.Choice(['FB', 'Facebook', 'f', 'd', 'Discord', 'disc']),
    prompt="Output format",
    help="Specify the output formatting for the nest list")
# main method
def main(city=None, date=None, format=None):
    city, path = choose_folder(city)
    date = dateparse.getdate(date)
    rundate = date.strftime('%d %b %Y')
    print("Gathering nests for " + city + " as of " + rundate)
    rot8d8, listfile = find_nest_list(path, date)
    shiftdate = str(rot8d8)
    print("Using the nest list from the " + shiftdate + " nest rotation")
    if format[0].lower() == 'f':
        FB_post(listfile, rundate, shiftdate)
    if format[0].lower() == 'd':
        disc_posts(listfile, rundate, shiftdate)
    return

if __name__ == "__main__":
    main()
