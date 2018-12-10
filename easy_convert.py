import pdf2image as p2i
from PIL import Image as im
import numpy as np
import shutil
import zipfile
import os
from tqdm import tqdm

out_dir = 'C:\\Users\\name\\Desktop\\test\\out\\'
pdf_dir = 'C:\\Users\\name\\Desktop\\test\\some_book.pdf'


def convert(pdf_dir, out_dir):
    an_instance = general_pdf(pdf_dir, out_dir)
    del an_instance 
    print("EPUB ready at " + out_dir)

class general_pdf():
    def __init__(self, pdf_dir, out_dir):
        self.pdf_dir = pdf_dir 
        self.out_dir = out_dir 
        assert os.path.exists(pdf_dir)
        assert os.path.exists(out_dir)
        self.pdf_title = pdf_dir.split('\\')[-1].split('.pdf')[0]
        self.create_temp_dir()
        self.data = p2i.convert_from_path(self.pdf_dir, fmt='png', thread_count=os.cpu_count())
        self.slice_pages()
        self.save_images()
        self.convert_to_epub()


    def convert_to_epub(self):
        images = [self.temp_dir_name + i for i in os.listdir(self.temp_dir_name)]
        self.make_general_epub(images, title = self.pdf_title, output_dir = self.out_dir)
        shutil.rmtree(self.temp_dir_name)


    def save_images(self):
        digits = len(str(len(self.all_slices)))
        file_names = [str(i).rjust(digits, '0') + '.jpg' for i in range(len(self.all_slices))]
        for index, slice in enumerate(self.all_slices):
            im.fromarray(255-slice).save(self.temp_dir_name + file_names[index])
        

    def create_temp_dir(self):
        if self.out_dir[-1] != '\\':
            self.out_dir += '\\'
        self.temp_dir_name = self.out_dir + 'temp'
        while os.path.exists(self.temp_dir_name):
            self.temp_dir_name += '0'
        self.temp_dir_name += '\\'
        os.mkdir(self.temp_dir_name)
        

    def slice_pages(self):
        self.all_slices = []    
        for i in tqdm(range(len(self.data))):
            tpage = 255 - np.asarray(self.data[i])[:,:,0]
            tpage = self.general_crop(tpage)
            self.all_slices += self.general_split(tpage)
            

    def general_split(self, tpage, leniance = 20):
        v_split = tpage.shape[0]//2
        one_slice = np.transpose(tpage[:v_split + leniance,:])[::-1,:]
        two_slice = np.transpose(tpage[v_split-leniance:,:])[::-1,:]
        return [one_slice, two_slice]
        

    def general_crop(self, tpage, step = 5, leniance = 10):
        side_crop_left = 0
        side_crop_right = tpage.shape[1]-1
        top_crop = 0 
        bot_crop = tpage.shape[0]-1 
        while np.mean(tpage[:,side_crop_left]) == 0:
            side_crop_left += step
        while np.mean(tpage[:,side_crop_right]) == 0:
            side_crop_right -= step 
        while np.mean(tpage[top_crop,:]) == 0:
            top_crop += step 
        while np.mean(tpage[bot_crop,:]) == 0:
            bot_crop -= step 
        side_crop_left = max(0,side_crop_left - leniance)
        side_crop_right = min(tpage.shape[1]-1, side_crop_right + leniance)
        top_crop = max(0, top_crop - leniance)
        bot_crop = min(tpage.shape[0]-1, bot_crop + leniance)
        return tpage[top_crop:bot_crop, side_crop_left:side_crop_right]


    def make_general_epub(self, images, output_dir, title=None, author=None):
        if True:

            container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
            <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
              <rootfiles>
                <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
              </rootfiles>
            </container>
            '''

            page_xml_1 = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?><html xmlns="http://www.w3.org/1999/xhtml">
            <head>
            <title>Strength</title>

            <meta content="http://www.w3.org/1999/xhtml; charset=utf-8" http-equiv="Content-Type"/>

                    <style title="override_css" type="text/css">
                        body { text-align: center; padding:0pt; margin: 0pt; }
                    </style>
                </head>
                <body>
                    <div>
                        <svg xmlns="http://www.w3.org/2000/svg" height="100%" version="1.1" width="100%" xmlns:xlink="http://www.w3.org/1999/xlink">
                            <image xlink:href="../Images/'''

            page_xml_2 = '''.jpg"/>
                        </svg>
                    </div>
                </body>
            </html>
            '''
            page_xml_1 + '0000' + page_xml_2

            content1 = '''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
            <package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uuid_id" version="2.0">
                <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:opf="http://www.idpf.org/2007/opf" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

                    <dc:title>{title}</dc:title>

                    <dc:language>en</dc:language>

                    <dc:identifier id="uuid_id" opf:scheme="uuid">isbn-000-0-000-00000-0</dc:identifier>
                    <dc:creator>{author}</dc:creator>
                    <dc:publisher>Swagu Booksu</dc:publisher>
                    <dc:date>2099-09-09</dc:date>

                    <meta name="cover" content="my-cover-image"/>

                </metadata>
                <manifest>
            '''

            add_manifest = '''
                    <item href="Text/{xhtml_file}.xhtml" id="{xhtml_id}" media-type="application/xhtml+xml"/>
                    <item href="Images/{image_file}.jpg" id="{image_id}" media-type="image/jpeg"/>
            '''

            content2 = '''
                </manifest>
                <spine toc="tableofcontents">
            '''


            add_spine = '''
                    <itemref idref="{0}"/>
            '''

            content3 = '''
                </spine>
                <guide>
                    <reference href="Text/bookcover.xhtml" title="Cover Image" type="cover"/>
                </guide>
            </package>
            '''

        epub = zipfile.ZipFile(output_dir + title + '.epub', 'w')
        epub.writestr("mimetype", "application/epub+zip")
        epub.writestr("META-INF/container.xml", container_xml)

        manifest, spine = '', ''

        names = [format(i, '04d')  for i in range(len(images))]

        # Write first image due to some exceptions
        im_content = open(images[0], 'rb').read()
        epub.writestr("OEBPS/Images/" + 'cover.jpg', im_content)

        manifest += content1.format(title=title, author=author)
        manifest += add_manifest.format(xhtml_file = 'bookcover',
                                        image_file = 'cover.jpg',
                                        xhtml_id = 'bookcover',
                                        image_id = 'my-cover-image')
        spine += '        <itemref idref="bookcover" linear="no"/>'
        im_content2 = page_xml_1 + 'cover' + page_xml_2
        epub.writestr("OEBPS/Text/bookcover.xhtml", im_content2)

        for index in range(1, len(images[1:])):
            image = images[index]
            image_name = names[index]
            im_content = open(image, 'rb').read()

            epub.writestr("OEBPS/Images/" + image_name + '.jpg', im_content)
            xhtml_id = 'idk' + image_name
            manifest += add_manifest.format(xhtml_file = xhtml_id,
                                            image_file = image_name,
                                            xhtml_id = xhtml_id,
                                            image_id = image_name)
            spine += add_spine.format(xhtml_id)
            im_content2 = page_xml_1 + image_name + page_xml_2
            epub.writestr("OEBPS/Text/{0}.xhtml".format(xhtml_id), im_content2)

        manifest += content2
        manifest += spine
        manifest += content3
        epub.writestr("OEBPS/content.opf", manifest)
        epub.close()


convert(pdf_dir, out_dir)


