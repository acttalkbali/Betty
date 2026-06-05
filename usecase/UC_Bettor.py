"""
UC Bettor creation:
A wannabe-bettor registers to the Betty application, setting its email address, password and pseudo.
"""

"""
UC bettor login:
A registered bettor logs-in to Betty using its pseudo or email address and password.
The tournaments to which he is registered are listed.
POST bettor logged-in
"""

"""
UC tournament selection:
PRE bettor logged-in
The bettor selects a tournament from those to which he has registered.
POST Tournament selected
"""

"""
UC Tournament registration:
PRE bettor logged-in
Betty selects the open tournaments
The bettor selects the open tournament into which he wants to participate (automatic selection if only one tournament opened)
The bettor wallet is credited with the Tournament's setup wallet.
"""

"""
UC BTeam setup:
The admin creates a BTeam and assigns some registered bettors to it
"""

"""
UC The Bettor sets up its sheep livestock
PRE bettor logged in, OPEN tournament T selected,
The Bettor buys sheep. Its wallet is debited accordingly
"""

"""
UC Bet:
PRE bettor logged-in, OPEN tournament T selected
The bettor enters its bet for any of the OPEN available T bettable
"""

"""
UC Tournament status:
PRE bettor logged-in, OPEN tournament T selected
The bettor choose 'tournament status' from the available actions.
The tournament's bettable are listed in accordance with their status
"""

"""
UC Tournament ranking:
PRE bettor logged-in, OPEN tournament T selected
The bettor choose 'tournament ranking' from the available actions.
The tournament's current bettor ranking is listed. 
"""
