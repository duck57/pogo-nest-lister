# PoGo Nest Lister

##### A system for tracking PoGo nest migrations for your city's parks

* [New developments have moved to this new repo!](https://github.com/duck57/poke-db)
* [Link to example nest post](https://www.facebook.com/groups/pokemongocolumbus/permalink/554505388295779/)

### Notes

2. `rotate.py` can also accept a `-d` paramater which will accept a date, skip
   the prompt, and directly create the new file
3. `update.py` also accept a similar `-d` parameter in case you want to copy
   the text for a prior nest rotation
4. I've only tested this on my Mac so far and I have no idea how a Windows
   Python setup would work.  I can also test under FreeBSD if you ask nicely.
5. Requires the `dateutil`, `sortedcontainers`, and `click` packages to be
   installed.  They are listed as `python-dateutil`, `sortedcontainers`, and
`click` in `pip3`.  (The difference in names for dateutil tripped me up)
6. This is a closed project.  [poke-db](https://github.com/duck57/poke-db) is the new hotness.
