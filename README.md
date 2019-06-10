# Rod_Mudlet
6/09/2019 CJH

This is a set of mudlet scripts, triggers and aliases for Mudlet and Realms of Despair.

To use this repository, download it, extract the parent zip and 
1) use Mudlet's package installer to import the CJH_Rod_Mudlet.zip file.  To get rid of it, use the package installer to uninstall it. 
2) use Mudlet's Options -> Preferences -> Mapper -> Load Map and load the map (.dat) file.  Note - you need
  a) Jor'Mox's generic mapper package installed, and need to do a "map update".  
  b) And a "find prompt" may also be necessary after that.  
  c) You need a "map ignore %s%s.* to keep the map from pulling in the RoD compass on your room names.   It should use my map then.


The triggers are a bit harder - to get the fight trackers to work, you may have to edit the regular expressions they are watching for to see your prompt and recognize the difference between the regular prompt and in-fight prompts.  It's specifically set up for my guys at the moment. 
The aliases are all self-explanatory in how they work - just type the string the alias is waiting for.
The scripts are initialization and helper functions for the triggers and aliases.  Instructive to read.

TODO: See if we can just use an xml file because that would be a lot easier to git diff.

Raise issues and bugs please and I'll look into them.

Note to self: in case I forget, this is at \CJH\Misc\Games\CJH_Mudlet_Git
