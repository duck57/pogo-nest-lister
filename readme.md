# PoGo Nest Lister

##### A system for tracking PoGo nest migrations for your city's parks

Note: the clipboard output is formatted to be used as a big Facebook tracking
post, as it was originally intended to make the
[PoGoCo](https://www.facebook.com/groups/PokemonGoColumbus) nest list more
managable.

[(Link to example nest post)](https://www.facebook.com/groups/pokemongocolumbus/permalink/426082914471361/)

## Instructions

1. Make a file in the `Cities` folder for your area (PRs with new cities
   welcome, see `Columbus.tsv` for the reference implementation).
2. Alphabetize your nests for easier reference with `./sort <CITY>` (your city
   must have its list alphabetized for your add city PR to be accepted)
3. Every migration, run `./rotate -c <CITY>`, which will generate an output
   file in the `hist-nest/\<CITY\>/YYYY-MM-DD.tsv` format
4. Edit the file in the `hist-nest` folder for the rotation as new nests come
   in
5. To generate the text formatted to share with Facebook, run ` ./update -c
   <CITY>`

### Notes

1. I'd rather use Textile than Markdown to make this, but I'm not in charge of
   how GitHub displays its repos.
2. `rotate.py` can also accept a `-d` paramater which will accept a date, skip
   the prompt, and directly create the new file
3. `update.py` also accept a similar `-d` parameter in case you want to copy
   the text for a prior nest rotation
4. I've only tested this on my Mac so far and I have no idea how a Windows
   Python setup would work.  I can also test under FreeBSD if you ask nicely.
5. Requires the `dateutil`, `sortedcontainers`, and `click` packages to be
   installed.  They are listed as `python-dateutil`, `sortedcontainers`, and
   `click` in `pip3`.  (The difference in names for dateutil tripped me up)
6. Feature requests are tracked in the issues tab with the `enhancement` label.
