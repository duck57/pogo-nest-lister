# PoGo Nest Lister

##### A system for tracking PoGo nest migrations for your city's parks

CURRENTLY UNDERGOING A MAJOR REWRITE.  The migration to the SQLite database has
been successful, but the unified terminal UI is not yet implemented, so there
are still common functions that still require external software to complete.

Update 04 October 2018: limitations of SQLite before a full TUI solution is
implemented have proven too aggrivating and I'm moving to Maria+Django (or
maybe moving from Python to Elixir/Phoenix) before working more on the TUI
stuff or other major improvements.  This will probably be in a new repository.
The code in its current state works, but isn't elegant to use.


##### [Link to example nest post](https://www.facebook.com/groups/pokemongocolumbus/permalink/554505388295779/)

## Instructions

TODO: complete me once the rewrite is finished and stable enough to be worth
writing detailed docs.  However, there is currently the choice to format the
output for either Facebook or Discord.  

14 Dec 2018: This update may change the model from being a locally-run app to a
server-hosted app and future instructions may be more focused on notes to self
and end user workflows instead of technical install details.

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
