#!/bin/sh

sudo apt install pandoc mupdf texlive-extra-utils texlive-fonts-recommended texlive-pictures texlive-generic-recommended texlive-latex-extra
sudo cp notetaking /usr/local/bin
sudo cp notetaking.latex /usr/share/pandoc/data/templates/notetaking.latex

