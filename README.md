startuplab
==========

TODO (high priority)
----
* andrey: save new tags from profile view (line ~245 of views.py in this commit)
* andrey: design and implement bid interaction API
* nikolai: superuser deploy hooks & backdoors
* nikolai: credit transaction system

pages:
- full feed page
- post UI
- generic background block
- money exchange page
- home page / concept splash
- error pages !!! (with feedback entry thing)
- generic pages (about, "what's next", etc)

BACKLOG (low priority)
-------
* andrey: search around for efficient ways to search for strings of text in active bids
* andrey: figure out logging shit
* nikolai: figure out static file bullshit on heroku
* nikolai: cool thing http://tommoor.github.com/crumble/
* nikolai: configure Postgres locally so we don't have to test the credit lock stuff on heroku
* both: think about different cases for when people don't have enough credits for stuff.
* for example, if you respond to a help request, the person making the request should see
* if the responder doesn't actually have enough credits to pay.
* both: write tests LOL yeah right
