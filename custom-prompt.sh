#!/usr/bin/env bash

######## Prompt editing

# Colors used for the prompt.
## Regular text color

# BLACK
BLACK='30'
## Background color
BGBLACK='40'
# RED
RED='31'
BGRED='41'
# GREEN
GREEN='32'
BGGREEN='42'
# YELLOW
YELLOW='33'
BGYELLOW='43'
# BLUE
BLUE='34'
BGBLUE='44'
# AGENTA
AGENTA='35'
BGAGENTA='45'
# CYAN
CYAN='36'
BGCYAN='46'
# WHITE
WHITE='37'
BGWHITE='47'

# Other formatting
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
  # root
  UC="\[\e[${BOLD};${YELLOW};${BGRED}m\]\u"
  DT="\[\e[${DIM};${WHITE}m\D{%x %X}${DF}\]\n"
  HC="\[\e[${BOLD};${WHITE};${BGRED}m\]@\h:"
  FQP="\[\e[${BOLD};${CYAN};${BGRED}m\]\w"
  PS1="[${UC}${HC}${DF}${FQP}${DF}]# "
else
  # user
  DT="\[\e[${DIM};${WHITE}m\]\D{%x %X}${DF}\n"
  FQP="\[\e[${CYAN}m\]\w"
  HC="\[\e[${BOLD};${BLUE}m\]\h"
  UC="\[\e[${BOLD};${GREEN}m\]\u"
  PS1="[${UC}@${HC}${RC}:${FQP}${DF}]$ "
fi
