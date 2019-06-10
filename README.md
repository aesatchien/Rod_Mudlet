# Rod_Mudlet
6/09/2019 CJH

This is a set of mudlet maps, scripts, triggers and aliases for Mudlet and Realms of Despair.

--To use this repository, download it, extract the parent zip and 
1) use Mudlet's package installer to import the CJH_Rod_Mudlet.zip file.  To get rid of it, use the package installer to uninstall it. You can enable and disable individual items.
2) use Mudlet's Options -> Preferences -> Mapper -> Load Map and load the map (.dat) file.  Note - you need
  a) Jor'Mox's generic mapper package installed, and need to do a "map update".  
  b) And a "find prompt" may also be necessary after that.  
  c) You need a "map ignore %s%s.* to keep the map from pulling in the RoD compass on your room names.   It should use my map then.


--The triggers are a bit harder - to get the fight trackers to work, you will have to edit the regular expressions that are watching to see your prompt and recognize the difference between the regular prompt and in-fight prompts.  It's specifically set up for my guys at the moment with "<>" in my fight prompt but not in my regular one. The disarm trigger should work fine.
--The aliases are all self-explanatory in how they work - just type the string the alias is waiting for.
  For instance: togconsole, togfight, and togquaff toggle the consoles, fight trackers, and quaffing features. "det x" casts one of many    detect spells, and "weal xy <target>" and "harm xy <enemy>" will cast helpful or harmful spells on your current target or enemy, where what xy maps to varies and is in the scripts section.  
--The scripts are basically initialization and helper functions for the triggers and aliases.  Instructive to read.

TODO: See if we can just use an xml file because that would be a lot easier to git diff.

Raise issues and bugs please and I'll look into them.

Note to self: in case I forget, this is stored on my laptop at \CJH\Misc\Games\CJH_Mudlet_Git
