import pdf2image as p2i
from PIL import Image as im
import numpy as np
import shutil
import zipfile
import os
from tqdm import tqdm

# TODO:
# https://stackoverflow.com/questions/2431426/extract-toc-of-pdf


out_dir = 'C:\\Users\\pwnag\\Desktop\\'
pdf_dir = 'C:\\Users\\pwnag\\Desktop\\'
SERIOUSLY_PACKED = False

pdfs = [pdf_dir + i for i in os.listdir(pdf_dir) if i[-4:] == '.pdf']


def general_split(tpage, leniance = 20):
    v_split = tpage.shape[0]//2
    one_slice = np.transpose(tpage[:v_split + leniance,:])[::-1,:]
    two_slice = np.transpose(tpage[v_split-leniance:,:])[::-1,:]
    return [one_slice, two_slice]


def general_crop(tpage, step = 5, leniance = 5):
    try:
        side_crop_left = 0
        side_crop_right = tpage.shape[1]-1
        top_crop = 0
        bot_crop = tpage.shape[0]-1
        if SERIOUSLY_PACKED:
            while np.mean(tpage[:,side_crop_left]) <= 5: # for seriously cramped books
                side_crop_left += step
            while np.mean(tpage[:,side_crop_right]) <= 5:
                side_crop_right -= step
            while np.mean(tpage[top_crop,:]) <= 5:
                top_crop += step
            while np.mean(tpage[bot_crop,:]) <= 5:
                bot_crop -= step
        else: # this branch is untested, glitches redirect here
            while np.mean(tpage[:,side_crop_left]) == 0: # <= 5: for seriously cramped books
                side_crop_left += step
            while np.mean(tpage[:,side_crop_right]) == 0: # <= 5:
                side_crop_right -= step
            while np.mean(tpage[top_crop,:]) == 0: # <= 5:
                top_crop += step
            while np.mean(tpage[bot_crop,:]) == 0: # <= 5:
                bot_crop -= step
        side_crop_left = max(0,side_crop_left - leniance)
        side_crop_right = min(tpage.shape[1]-1, side_crop_right + leniance)
        top_crop = max(0, top_crop - leniance)
        bot_crop = min(tpage.shape[0]-1, bot_crop + leniance)
        return tpage[top_crop:bot_crop, side_crop_left:side_crop_right]
    except: # this is the case for blank pages
        return tpage


def save_images(slices_to_save, temp_dir_name):
    '''
    def save_images_old():
        digits = len(str(len(all_slices)))
        file_names = [str(i).rjust(digits, '0') + '.jpg' for i in range(len(all_slices))]
        for index, slice in enumerate(all_slices):
            im.fromarray(255-slice).save(temp_dir_name + file_names[index])
    '''

    '''saves the images to the temporary directory.'''
    digits = len(str(len(slices_to_save)))
    file_names = [str(i).rjust(digits, '0') + '.jpg' for i in range(len(slices_to_save))]
    for index, slice in enumerate(slices_to_save):
        im.fromarray(255-slice).save(temp_dir_name + file_names[index])


def custom_crop(tpage, params):
    '''
    params in the format: X_LEFT, X_RIGHT, Y_UP, Y_DOWN
    x_left = params[0]
    x_right = params[1]
    y_up = params[2]
    y_down = params[3]
    '''
    return tpage[params[2]:-params[3]:,params[0]:-params[1]]


def make_numpy_arrays(the_data):
    ''' Turns the rendered image into a numpy array, which will be an average over
    the 3 color channels.   '''
    new_data = []
    for i in range(len(the_data)):
        tpage = (np.sum(255 - np.asarray(the_data[i]), axis=2)//3).astype(np.uint8)
        new_data.append(tpage)
    return new_data


def slice_pages(the_imgs):
    '''performs the general crop and the general split.'''
    all_slices = []
    # dont preprocess cover page
    all_slices.append(the_imgs[0])
    # rest of the pages
    for i in tqdm(range(1,len(the_imgs))):
        tpage = the_imgs[i]
        tpage = general_crop(tpage)
        all_slices += general_split(tpage)
    return all_slices


def convert_to_epub_NO_BORDER(temp_dir_name, one_pdf_dir, title, all_slices):

    # ALL NEW KEPUB

    if True:
        container_xml = '''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
        <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
        </rootfiles>
        </container>
        '''
        nav_xhtml = '''<?xml version="1.0" encoding="utf-8"?>
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
        <head>
        <title>{0}</title>
        <meta charset="utf-8"/>
        </head>
        <body>
        <nav xmlns:epub="http://www.idpf.org/2007/ops" epub:type="toc" id="toc">
        <ol>
        <li><a href="Text/0002-kcc.xhtml">soy</a></li>
        </ol>
        </nav>
        <nav epub:type="page-list">
        <ol>
        <li><a href="Text/0002-kcc.xhtml">soy</a></li>
        </ol>
        </nav>
        </body>
        </html>
        '''
        toc_ncx = '''<?xml version="1.0" encoding="UTF-8"?>
        <ncx version="2005-1" xml:lang="en-US" xmlns="http://www.daisy.org/z3986/2005/ncx/">
        <head>
        <meta name="dtb:uid" content="urn:uuid:3b6462a2-2cf2-4b2e-8779-4d9bb6e5f2c3"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
        <meta name="generated" content="true"/>
        </head>
        <docTitle><text>soy</text></docTitle>
        <navMap>
        <navPoint id="Text"><navLabel><text>soy</text></navLabel><content src="Text/0002-kcc.xhtml"/></navPoint>
        </navMap>
        </ncx>
        '''
        style_css = '''@page {
        margin: 0;
        }
        body {
        display: block;
        margin: 0;
        padding: 0;
        }
        '''
        content_opf_upper = '''<?xml version="1.0" encoding="UTF-8"?>
        <package version="3.0" unique-identifier="BookID" xmlns="http://www.idpf.org/2007/opf">
        <metadata xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{0}</dc:title>
        <dc:language>en-US</dc:language>
        <dc:identifier id="BookID">urn:uuid:3b6462a2-2cf2-4b2e-8779-4d9bb6e5f2c3</dc:identifier>
        <dc:contributor id="contributor">KindleComicConverter-5.5.1</dc:contributor>
        <dc:creator></dc:creator>
        <meta property="dcterms:modified">2019-09-05T18:06:13Z</meta>
        <meta name="cover" content="cover"/>
        <meta property="rendition:orientation">portrait</meta>
        <meta property="rendition:spread">portrait</meta>
        <meta property="rendition:layout">pre-paginated</meta>
        </metadata>
        <manifest>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        <item id="nav" href="nav.xhtml" properties="nav" media-type="application/xhtml+xml"/>
        <item id="cover" href="Images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>
        '''
        content_opf_middle = '''<item id="css" href="Text/style.css" media-type="text/css"/>
        </manifest>
        <spine page-progression-direction="ltr" toc="ncx">
        '''
        content_opf_lower = '''</spine>
        </package>
        '''
        content_opf_manifest_template = '''
        <item id="page_Images_{0}" href="Text/{0}.xhtml" media-type="application/xhtml+xml"/>
        <item id="img_Images_{0}" href="Images/{0}.jpg" media-type="image/jpeg"/>
        '''
        content_opf_spine_template = '''<itemref idref="page_Images_{0}"/>'''

        xhtml_template = '''<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
        <head>
        <title>{0}</title>
        <link href="style.css" type="text/css" rel="stylesheet"/>
        <meta name="viewport" content="width={1}, height={2}"/>
        </head>
        <body style="">
        <div style="text-align:center;top:1.7%;">
        <img width="{1}" height="{2}" src="../Images/{0}.jpg"/>
        </div>
        </body>
        </html>
        '''



    # Initialize

    WIDTH = 1250
    HEIGHT = 1807

    output_dir = one_pdf_dir[:-4]
    epub = zipfile.ZipFile(output_dir + '.kepub.epub', 'w')
    epub.writestr("mimetype", "application/epub+zip")
    epub.writestr("META-INF/container.xml", container_xml)
    epub.writestr("OEBPS/nav.xhtml", nav_xhtml.format(title))
    epub.writestr("OEBPS/toc.ncx", toc_ncx)
    epub.writestr("OEBPS/Text/style/css", style_css)



    manifest, spine = '', ''

    images = [os.path.join(temp_dir_name, i) for i in os.listdir(temp_dir_name)]

    names = [format(i, '04d') + '-kcc' for i in range(len(images))]

    # write cover (just duplicate images[0])
    im_content = open(images[0], 'rb').read()
    epub.writestr("OEBPS/Images/" + 'cover.jpg', im_content)


    # write the rest of the images
    index = 0
    for i in names:
        manifest += content_opf_manifest_template.format(i)
        spine += content_opf_spine_template.format(i)

        im_content = open(images[index], 'rb').read()

        image_width = all_slices[index].shape[1] # done here before the index is incremented.
        image_height = all_slices[index].shape[0]
        #image_height = 1200#int(image_height*1.1)

        index += 1
        epub.writestr("OEBPS/Images/" + i + '.jpg', im_content)


        xhtml_content = xhtml_template.format(i, image_width, image_height)
        epub.writestr("OEBPS/Text/{0}.xhtml".format(i), xhtml_content)



    # write content
    content_opf_final = content_opf_upper.format(title) + manifest + content_opf_middle + spine + content_opf_lower
    epub.writestr("OEBPS/content.opf", content_opf_final)
    epub.close()






for one_pdf_dir in pdfs:

    pdf_title = one_pdf_dir.split('\\')[-1].split('.')[0]
    pdf_title
    print("Starting:\n" + one_pdf_dir)
    data = p2i.convert_from_path(one_pdf_dir, fmt='png', thread_count=os.cpu_count())#, last_page=20)

    data2 = [data[0]] + data[:] # copy first page to be the cover, then cropped
    imgs = make_numpy_arrays(data2)
    #imgs = [custom_crop(i, custom_crop_params) for i in imgs] # custom crop
    all_slices = slice_pages(imgs)

    # make temporary directory
    temp_dir_name = out_dir + 'temp'
    temp_dir_name += '\\'
    os.mkdir(temp_dir_name)
    # do the rest
    save_images(all_slices, temp_dir_name)
    #convert_to_epub(temp_dir_name, out_dir, pdf_title)

    convert_to_epub_NO_BORDER(temp_dir_name, one_pdf_dir, pdf_title, all_slices)

    shutil.rmtree(temp_dir_name)
