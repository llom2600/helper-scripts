#!/bin/bash
#work on a specific virtual environment

set_venv(){
	local d=" /home/llom2600/virtual-env/$1/bin/activate"
	echo $d
}

export venv_path=$(set_venv $1)

#echo "Switching  environment to: $venv_path"