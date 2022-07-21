# PDF to EPUB
Convert a PDF to images so it renders quickly and nicely on your e-reader. Also provides options to crop it so the font size is to your liking. 

![alt text](https://github.com/ConsciousMachines/PDF-to-EPUB-for-arXiv/blob/master/example.jpg)

# Installation
follow instructions [here](https://github.com/Belval/pdf2image) to install pdf2image and Poppler 

# Usage
- set the path to where your PDF is.
- manually set & preview the crop border sizes. this allows you to crop out annoying and large parts of pages. 
- run the rest of the script.

# Changelog
## July 21, 2022
- removed numpy dependency for the cropping process (making it faster)
- the process was getting killed for large books (>900 pages) and large dpi (>300) so even though the data[] array is "ready", there must be lazy evaluation going on somewhere otherwise it wouldn't run out of memory in the loop. deleting old data[] elements fixed the issue. 


