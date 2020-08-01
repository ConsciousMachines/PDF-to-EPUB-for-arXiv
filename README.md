# PDF-to-EPUB

Have you always wished that you could read PDFs just like they appear on your computer screen, but on your e-reader? Well, if you have a KOBO e-reader, today is your lucky day!



*Installation*

- follow instructions [here](https://github.com/Belval/pdf2image) to install pdf2image and Poppler


*Directions*
- set "pdf_dir" in the python script to the folder with the PDFs you want to convert
- set "out_dir" to the directory where you want the output
- run!


![alt text](https://github.com/ConsciousMachines/PDF-to-EPUB-for-arXiv/blob/master/example.jpg)

How it's done: 
this method takes the PDF and converts it to an image using the pdf2image wrapper (requires to install Poppler ((Windows binaries are available online))), and then the images to an EPUB file. This top-down approach takes care of all the problems of decrypting PDF files and reconverting images, fonts, etc. while maintaining all the desired formatting eyecandy embedded in PDFs. 



Tested with Kobo Aura One e-reader, and on Windows 10

Known issues: 
- None. This is an ideal program. 

special thanks to KCC (Kindle Comic Converter) which shows how to implement borderless epubs. 
