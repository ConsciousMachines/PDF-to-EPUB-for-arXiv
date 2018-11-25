# PDF-to-EPUB-for-arXiv

Tired of reading arXiv papers on the computer? Wishing there existed a way to convert them to EPUB format for your E-reader? Well today is your lucky day! 

Just organize all the pdf files you want to read into 2 folders, one with single-column documents (like textbooks) and one for two-column documents (like most arXiv papers). Then supply the names of the pdf directory, and the desired output directory to the respective script and you got an EPUB that you can read on the go without straining your eyes for hours. Also, provide your E-reader resolution for better image scale ratios (mine was 1.333)

How it's done: 
this method takes the PDF and converts it to an image using the pdf2image wrapper (requires to install Popper ((Windows binaries are available online))), and then the images to an EPUB file. This top-down approach takes care of all the problems of decrypting PDF files and reconverting images, fonts, etc. 



Tested with Kobo Aura One e-reader, and on Windows 10

Known issues: 
- epub doesn't open on Microsoft Edge explorer (still works on your E-reader though)
