# PDF-to-EPUB-for-arXiv

Tired of reading arXiv papers on the computer? Wishing there existed a way to convert them to EPUB format for your E-reader? Well today is your lucky day! 

TL;DR: for ANY pdf regardless of format, use easy_convert.py: call the convert(pdf_path, output_directory) and you're done.

*Installation*

- follow instructions [here](https://github.com/Belval/pdf2image) to install pdf2image and Poppler
- navigate to your installation directory and run:
$ pip install -r requirements.txt

*Directions*
- set "pdf_dir" in the python script to the folder with the PDFs you want to convert
- set "out_dir" to the directory where you want the output
- run!


![alt text](https://github.com/ConsciousMachines/PDF-to-EPUB-for-arXiv/blob/master/example.jpg)

How it's done: 
this method takes the PDF and converts it to an image using the pdf2image wrapper (requires to install Popper ((Windows binaries are available online))), and then the images to an EPUB file. This top-down approach takes care of all the problems of decrypting PDF files and reconverting images, fonts, etc. while maintaining all the desired formatting eyecandy embedded in PDFs. 



Tested with Kobo Aura One e-reader, and on Windows 10

Known issues: 
- epub doesn't open on Microsoft Edge explorer (still works on your E-reader though)
