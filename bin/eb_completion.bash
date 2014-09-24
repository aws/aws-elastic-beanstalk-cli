_eb_complete() {
 COMPREPLY=()
 local words=( "${COMP_WORDS[@]}" )
 local word="${COMP_WORDS[COMP_CWORD]}"
 words=("${words[@]:1}")
 local completions="$(eb completer --cmplt=\""${words[*]}"\")"
 COMPREPLY=( $(compgen -W "$completions" -- "$word") )
}

complete -F _eb_complete eb