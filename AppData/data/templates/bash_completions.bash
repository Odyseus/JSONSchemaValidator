#!/bin/bash

# It would have been impossible to create this without the following post on Stack Exchange!!!
# https://unix.stackexchange.com/a/55622

type "{executable_name}" &> /dev/null &&
_decide_nospace_{current_date}(){
    # Decide if after the completion of a term should a space character be added or not.
    # It only works on Bash, not on Zsh. Not tested in any other shell.
    if [[ ${1} == "--"*"=" ]] ; then
        type "compopt" &> /dev/null && compopt -o nospace
    fi
} &&
_json_schema_validator_cli_{current_date}(){
    local cur prev cmd
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Handle --xxxxxx=
    if [[ ${prev} == "--"* && ${cur} == "=" ]] ; then
        compopt -o filenames
        COMPREPLY=(*)
        return 0
    fi

    # Handle --xxxxx=path
    case ${prev} in
        "="|"-d"|"-s")
        # Unescape space
        cur=${cur//\\ / }
        # Expand tilder to $HOME
        [[ ${cur} == "~/"* ]] && cur=${cur/\~/$HOME}
        # Show completion if path exist (and escape spaces)
        compopt -o filenames
        local files=("${cur}"*)
        [[ -e ${files[0]} ]] && COMPREPLY=( "${files[@]// /\ }" )
        return 0
        ;;
    esac

    # Completion of commands and "first level" options.
    if [[ $COMP_CWORD == 1 ]]; then
        COMPREPLY=( $(compgen -W "generate -h --help --manual --version \
validate" -- "${cur}") )
        return 0
    fi

    # Completion of options and sub-commands.
    cmd="${COMP_WORDS[1]}"

    case $cmd in
        "validate")
            COMPREPLY=( $(compgen -W "-d --data-file= -s --schema-file= \
--data-prop= --schema-prop= --data-is-json --schema-is-json" -- "${cur}") )
            _decide_nospace_{current_date} ${COMPREPLY[0]}
            ;;
        "generate")
            COMPREPLY=( $(compgen -W "system_executable" -- "${cur}") )
            ;;
    esac
} &&
complete -F _json_schema_validator_cli_{current_date} {executable_name}
