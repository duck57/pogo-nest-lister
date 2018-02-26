# Pokénests

##### A system for tracking PoGo nest migrations for your city's parks

Note: the clipboard output is formatted to be used as a big Facebook tracking
post, as it was originally intended to make the
[PoGoCo](https://www.facebook.com/groups/PokemonGoColumbus) nest list more
managable.

## Instructions

1. Make a file in the `Cities` folder for your area (PRs with new cities
   welcome, see `Columbus.tsv` for the reference implementation).
2. Alphabetize your nests for easier reference with `sort.py` (your city must
   have its list alphabetized for your PR to be accepted)
3. Every migration, run `python3 rotate.py -c <CITY>`, which will generate an
   output file in the `hist-nest/\<CITY\>/YYYY-MM-DD.tsv` format
4. Edit the file in the `hist-nest` folder for the rotation as new nests come
   in
5. To generate the text formatted to share with Facebook, run `python3
   update.py -c <CITY>`

## Possible future features

* Group parks by suburb
* Analyse old nest lists to find inactive and neglected nests
* Other output formats (Reddit markdown tables, etc…): only if other folks make
  the PR to support this

##### P.S.

1. I'd rather use Textile than Markdown to make this, but I'm not in charge of
   how GitHub displays its repos.
2. `rotate.py` can also accept a `-d` paramater which will accept a date, skip
   the prompt, and directly create the new file
3. `update.py` also accept a similar `-d` parameter in case you want to copy
   the text for a prior nest rotation
