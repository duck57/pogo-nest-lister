#!/usr/bin/env python3
# coding=UTF-8
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import sys
import os
import sqlite3
import urwid
from collections import OrderedDict
from sortedcontainers import SortedList
from collections import defaultdict
import update as output
import importoldlists as dbutils
import rotate as dateparse
import readline


nested_dict = lambda: defaultdict(nested_dict)


class NestDisplay:
    palette = [
        ('body','default', 'default'),
        ('foot','dark cyan', 'dark blue', 'bold'),
        ('key','light cyan', 'dark blue', 'underline'),
        ]

    footer_text = ('foot', [
        "Text Editor    ",
        ('key', "F5"), " copy list  ",
        ('key', "F9"), " quit",
        ])

    def __init__(self, db):
        self.dbc = dbutils.create_connection(db)
        self.listbox = urwid.ListBox('self.walker')
        self.footer = urwid.AttrWrap(urwid.Text(self.footer_text),
            "foot")
        self.view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'),
            footer=self.footer)

    def main(self):
        self.loop = urwid.MainLoop(self.view, self.palette,
            unhandled_input=self.unhandled_keypress)
        self.loop.run()

    def unhandled_keypress(self, k):
        """Last resort for keypresses."""

        if k == "f5":
            self.save_file()
        elif k == "f9":
            raise urwid.ExitMainLoop()
        elif k == "delete":
            # delete at end of line
            self.walker.combine_focus_with_next()
        elif k == "backspace":
            # backspace at beginning of line
            self.walker.combine_focus_with_prev()
        elif k == "enter":
            # start new line
            self.walker.split_focus()
            # move the cursor to the new line and reset pref_col
            self.loop.process_input(["down", "home"])
        elif k == "right":
            w, pos = self.walker.get_focus()
            w, pos = self.walker.get_next(pos)
            if w:
                self.listbox.set_focus(pos, 'above')
                self.loop.process_input(["home"])
        elif k == "left":
            w, pos = self.walker.get_focus()
            w, pos = self.walker.get_prev(pos)
            if w:
                self.listbox.set_focus(pos, 'below')
                self.loop.process_input(["end"])
        else:
            return
        return True


def selectlist(prompt, size):
    while True:
        try:
            selection = int(input(prompt))
        except (ValueError):
            print("Enter an integer")
            continue
        if selection in range(1,size+1):
            return selection
        else:
            print("Selection outside range")
            continue


def input_with_prefill(prompt, text):
    def hook():
        readline.insert_text(text)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    result = input(prompt)
    readline.set_pre_input_hook()
    return result


def update_park(dbc, rotnum):
    print("q to quit without saving, empty to quit & commit changes")
    search = input("Which park do you want to search? ").strip()
    if search == '':
        return 1
    if search.lower() == 'q':
        return -5
    results1, _ = dbutils.query_nest(search, dbc)
    if results1 is None:
        print("No nests found")
        return False
    count = 0
    results2 = nested_dict()
    choices = {}
    for nest in results1:
        nid = nest[0]
        if nid in choices.values():
            continue
        else:
            count += 1  # it goes here or else later logic is wrong
        choices[count] = nid
        results2[nid]["Name"] = nest[1]
        results2[nid]["Short"] = nest[2]
        results2[nid]["LocID"] = nest[3]
        results2[nid]["Count"] = count
    for choice in sorted(choices.keys()):
        print(str(choice) + ". " + results2[choices[choice]]["Name"])
    selected = -1
    if count==1:
        selected = 1
    else:
        selected = selectlist("Enter the number of the park you would like to display: ", count)
    selected = choices[selected]
    sq1 = "SELECT * FROM nest_locations WHERE nest_id=?"
    sq2 = "SELECT * FROM alt_names WHERE main_entry=?"
    sq3 = "SELECT * FROM neighborhoods WHERE id=?"
    sq4 = "SELECT * FROM regions WHERE id=?"
    nest_info = """
        SELECT
            nest_locations.*,
            neighborhoods.name AS 'Subdivision',
            regions.*
        FROM nest_locations
            LEFT OUTER JOIN neighborhoods ON nest_locations.location = neighborhoods.id
            LEFT OUTER JOIN regions ON neighborhoods.region = regions.id
        WHERE nest_id = ?"""

    inforow = dbc.execute(nest_info, [selected]).fetchall()[0]
    alts = dbc.execute(sq2, [selected])
    sinforow = []
    for i in inforow:
        sinforow.append(str(i))

    """print("Nest id: " + sinforow[0])
    print("Name: " + sinforow[1])
    print("Short: " + sinforow[2])
    print("Neighborhood id: " + sinforow[3])
    print("Address: " + sinforow[4])
    print("Notes: " + sinforow[5])
    print("Private? " + sinforow[6])
    print("Fixed nest? " + sinforow[7])
    print("Latitude: " + sinforow[8])
    print("Longitude: " + sinforow[9])
    print("Nest size: " + sinforow[10])
    print("Neighborhood: " + sinforow[11])
    print("Region ID: " + sinforow[12])
    print("Region: " + sinforow[13])
    print(output.decorate_text("Alternate Names", "[--  --]"))
    for alt in alts:
        print(str(alt))"""


    print("\nSelected Nest: " + sinforow[0] + " " + sinforow[1])
    rwnst = dbc.execute("SELECT species_txt, confirmation FROM species_list WHERE rotation_num = ? AND nestid = ?", (rotnum, inforow[0])).fetchall()
    current, confirm = None, None
    if len(rwnst)>0:
        current = rwnst[0][0]
        confirm = rwnst[0][1]
    upd8nest = "UPDATE species_list SET species_txt = ?, confirmation = ? WHERE rotation_num = ? AND nestid = ?"
    svnstsql = "INSERT INTO species_list(species_txt, confirmation, rotation_num, nestid) VALUES (?,?,?,?)"
    delnest  = "DELETE FROM species_list WHERE rotation_num = ? AND nestid = ?"
    if current is None:
        current = ''
        upd8nest = svnstsql  # adds a new nest if it's currently empty
    elif confirm is not None:
        current += "|" + str(confirm)
    species = input_with_prefill("Species|confirm? ", current)
    print("")

    conf = 1 if len(species.split('|'))>1 else None
    species = species.split('|')[0].strip()
    if species == '':
        species = None
        dbc.execute(delnest, (rotnum, inforow[0]))
        return False
    savenest = (species, conf, rotnum, inforow[0])
    dbc.execute(upd8nest, savenest)

    return False


def main():
    dbc = dbutils.create_connection("nests.db")
    rotnum, d8 = output.get_rot8d8(dateparse.getdate("t"), dbc)
    print("Editing rotation " + str(rotnum) + " from " + d8)
    stop = False
    while stop is False:
        stop = update_park(dbc, rotnum)
    if stop == 1:
        dbc.commit()
        print("Nests saved!")
    else:
        dbc.rollback()
        print("Nests reverted")
    dbc.close()


if __name__ == "__main__":
    main()
