# Pokénests

##### A system for tracking PoGo nest migrations for your city's parks

Note: the clipboard output is formatted to be used as a big Facebook tracking
post, as it was originally intended to make the [PoGoCo](https://www.facebook.com/groups/PokemonGoColumbus) nest list more
managable.

## Instructions

1. Make a file in the `Cities` folder for your area (PRs with new cities welcome, see `Columbus.tsv` for the reference implementation).
2. TK alphabetize your nests for easier reference (your city must have its list alphabetized for your PR to be accepted)
3. Every migration, run the new migration script, which will generate an output file in the `hist-nest/\<CITY\>/YYYY-MM-DD.tsv` format
4. Edit the file for the rotation as new nests come in
5. To generate the text formatted to share with Facebook, run the generate script with your city's name 

## Possible future features

* Group parks by suburb
* Analyse old nest lists to find inactive and neglected nests
* Other output formats (Reddit markdown tables, etc…): only if other folks make the PR to support this

##### P.S.

I'd rather use Textile than Markdown to make this, but I'm not in charge of how GitHub displays its repos.