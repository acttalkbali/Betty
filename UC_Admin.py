"""
Admin Use Cases implementation
"""

"""
UC Tournament Creation:
The admin creates the tournament, setting its name, start and end date
"""

"""
UC Team Creation:
The admin creates a bettable team, setting its name
"""

"""
UC Team Tournament assignment;
PRE tournament is selected
The admin assigns a bettable team to a tournament, setting its sheep price for the tournament
"""

"""
UC Phase Creation:
PRE tournament is selected
The admin creates a tournament phase, setting its type, name, number, wallet
"""

"""
UC Bettable Creation:
PRE tournament T is selected, T phase is selected
The admin creates a bettable event for the selected phase, setting the teams involved and its start date & time. 
If the start date and time is in the future, the bettable state is set to OPEN 
"""

"""
UC Tournament Publishing:
PRE tournament is selected
The admin opens the tournament to bettors. The tournament's web-site is created, an invitation e-mail wih the link is sent
to the registered bettors (+ filtering +), and possibly to additional bettor candidates
"""

"""
UC The admin registers a bettable score after its completion:
PRE RUNNING tournament T selected, RUNNING bettable selected
The admin registers the final score of the bettable. The bettable is set to CLOSED. 
The bettor ranking is re-computed. 
"""

"""
UC The admin corrects a bettable score after its completion:
PRE RUNNING tournament T selected, CLOSED bettable selected
The admin corrects the final score of the bettable.
"""
