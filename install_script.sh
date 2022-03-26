#!/bin/bash

system=$(uname)

echo $tester
echo -e "Installing chromedriver and \033[32mpython\033[0m libraries needed 🐍..."

sleep 2

python3=$(which python3)
if [ -z $python3 ]; then
	echo "Please install Python3 🐍 before launching this script."
	exit 1
fi

if [ $system = "Darwin" ]; then
	brew=$(which brew)
	if [ ! -z $brew ]; then
		brew install --cask chromedriver
	else
		echo -e "\033[31mPlease install brew or install chromedriver directly.\033[0m"
		exit 1
	fi
elif [ $system = "Linux" ]; then
	pacman=$(which pacman)
	dpkg=$(which pkg)
	apt=$(which apt)
	yum=$(which yum)
	if [ ! -z $apt ]; then
		sudo apt install chromium-chromedriver
	elif [ ! -z $dpkg ]; then
		sudo pkg install chromium-chromedriver
	elif [ ! -z $pacman ]; then
		sudo pacman install chromium-chromedriver
	elif [ ! -z $yum ]; then
		sudo yum install chromium-chromedriver
	else
		echo "Unable to install chromium-chromedriver. Is any package manager installed ?"
		exit 1
	fi
fi

pip3 install notify-py selenium
exit 0
