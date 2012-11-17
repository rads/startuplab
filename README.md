startuplab
==========

Monday Deadline
---------------

- question page
* /questions/<questionID> for logged in user (see all interactions)
* /questions/<questionID> for all other users (jump straight to interaction
* /questions/<questionID>/<responderID> goes straight to an interaction

- UI shit (mostly steph):
* fix fonts for tags
* credits icon
* fix feed bid css


TODO (high priority)
----
* andrey: save new tags from profile view 
* andrey: design and implement bid interaction API
* nikolai: superuser deploy hooks & backdoors
* nikolai: credit transaction system
* nikolai: static files bullshit
* nikolai: general select2 helper functions (init/auto-populate)
* steph: title block in navbar, cross-browser testing

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
* nikolai: cool thing http://tommoor.github.com/crumble/
* nikolai: configure Postgres locally so we don't have to test the credit lock stuff on heroku
* both: think about different cases for when people don't have enough credits for stuff.
* for example, if you respond to a help request, the person making the request should see
* if the responder doesn't actually have enough credits to pay.
* both: write tests LOL yeah right
* clean up fonts folder
