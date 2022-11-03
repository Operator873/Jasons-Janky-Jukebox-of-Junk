#!/usr/bin/env bash

######## Prompt editing ##########
# Format should be \e[<face>;<color>;<bgcolor>m<Following text...>
# Use ${DF} to return to terminal default (clear prior formating)
# Use ${RC} for standard white on black
# if statement changes prompt if user is root
# To apply to all users (including root) drop into /etc/profile.d/

# Colors used for the prompt.
## Text colors
BLACK='30'
RED='31'
GREEN='32'
YELLOW='33'
BLUE='34'
AGENTA='35'
CYAN='36'
WHITE='37'

## Background colors
BGBLACK='40'
BGRED='41'
BGGREEN='42'
BGYELLOW='43'
BGBLUE='44'
BGAGENTA='45'
BGCYAN='46'
BGWHITE='47'

## Font face
## Normal
NORM='0'
## Bold
BOLD='1'
## Dim
DIM='2'
## Underline
UL='4'
## Blink
BLINK='5'

# Remove formatting, return to Default
DF='\[\e[0m\]'

# Regular color
RC="\[\e[${BOLD};${WHITE}m\]"

# Current user color (modify if root)
if [ $UID -eq 0 ]
then
  # Build special prompt for root
  # If you comment out any portion (ex the DT config) make sure to
  # remove the variable from the PS1 line
  ## This will add a gray date/time line above the prompt
  DT="\[\e[${DIM};${WHITE}m\]\D{%x %X}${DF}\n"

  ## Configure the username part of the prompt
  UC="\[\e[${BOLD};${YELLOW};${BGRED}m\]\u"

  ## Configure the @hostname portion of prompt
  HC="\[\e[${BOLD};${WHITE};${BGRED}m\]@\h:"

  ## Configure the path information
  FQP="\[\e[${BOLD};${CYAN};${BGRED}m\]\w"

  ## Build the actual prompt.
  PS1="${DT}${RC}[${UC}${HC}${DF}${FQP}${DF}]# "
else
  # Prompt for everyone else
  # If you comment out any portion (ex the DT config) make sure to
  # remove the variable from the PS1 line
  ## This will add a gray date/time line above the prompt
  DT="\[\e[${DIM};${WHITE}m\]\D{%x %X}${DF}\n"

  ## Configure the username part of the prompt
  UC="\[\e[${BOLD};${GREEN}m\]\u"

  ## Configure the @hostname portion of prompt
  HC="\[\e[${BOLD};${BLUE}m\]\h"

  ## Configure the path information
  FQP="\[\e[${CYAN}m\]\w"

  ## Build the actual prompt.
  PS1="${DT}${RC}[${UC}@${HC}${RC}:${FQP}${DF}]$ "
fi
