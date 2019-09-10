# PDF-to-EPUB

Have you always wished that you could read PDFs just like they appear on your computer screen, but on your e-reader? Well today is the day that it finally happens. All you need is a KOBO e-reader. 

Update: New borderless version available, for extra dense PDFs

TL;DR: for ANY pdf, use easy_convert.py: call the convert(pdf_path, output_directory) and you're done.

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
this method takes the PDF and converts it to an image using the pdf2image wrapper (requires to install Poppler ((Windows binaries are available online))), and then the images to an EPUB file. This top-down approach takes care of all the problems of decrypting PDF files and reconverting images, fonts, etc. while maintaining all the desired formatting eyecandy embedded in PDFs. 



Tested with Kobo Aura One e-reader, and on Windows 10

Known issues: 
- None
- for some reason Microsoft Edge renders the results differently from the e-reader, so don't bother using it for debugging

special thanks to KCC (Kindle Comic Converter) which shows how to implement borderless epubs. 
