import pdf2image as p2i
from PIL import Image as im
import numpy as np
import shutil
import zipfile
import os
from tqdm import tqdm

# TODO:
# https://stackoverflow.com/questions/2431426/extract-toc-of-pdf

global out_dir
out_dir = 'C:\\Users\\pwnag\\Desktop\\'
pdf_dir = 'C:\\Users\\pwnag\\Desktop\\'

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
        while np.mean(tpage[:,side_crop_left]) == 0: # <= 5 for seriously cramped books
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
    except: # this is the case for blank pages
        return tpage


def make_general_epub(images, output_dir, title=None, author=None):
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


def convert_to_epub(temp_dir_name, out_dir, pdf_title):
    images = [temp_dir_name + i for i in os.listdir(temp_dir_name)]
    make_general_epub(images, title = pdf_title, output_dir = out_dir)
    shutil.rmtree(temp_dir_name)


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
        tpage = (np.sum(255 - np.asarray(data[i]), axis=2)//3).astype(np.uint8)
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


def convert_to_epub_NO_BORDER(temp_dir_name, pdf_dir, title, all_slices):

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

    output_dir = pdf_dir[:-4]
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




''' TEST ZONE: FIND THE PARAMETERS '''

''' LAST EXPERIMENTATION WITH ALGORITHMS BY SEDGEWICK. lots of new sugoi solutions!
pdf_dir = pdfs[0]
pdf_title = pdf_dir.split('\\')[-1].split('.pdf')[0]
pdf_title

first_page = 0
last_page = 100
data = p2i.convert_from_path(pdf_dir, fmt='png', thread_count=os.cpu_count(),\
    first_page=first_page, last_page = last_page)

data = p2i.convert_from_path(pdf_dir, fmt='png', thread_count=os.cpu_count())

tpages = [ (np.sum(255 - np.asarray(data[i]), axis=2)//3).astype(np.uint8) for i in range(len(data))]


# remove all pixels of a certain color
tpages3 = [i.astype(np.int32) for i in tpages[1:]]# remove first page which has wack dimensions
for i in range(len(tpages3)):
    tpages3[i][np.where(((tpages3[i] == 68) | (tpages3[i] == 47) | (tpages3[i] == 170) | (tpages3[i] == 114)))] = 0

tpages3[-5].shape

# B E T T E R  I D E A - check the max because we dont want to crop images
index = 1 # start at 1 to miss the first page w wack dims
the_max = tpages3[index]
while index != len(tpages3)-5:
    next_page = tpages3[index + 1]
    the_max = np.maximum(the_max, next_page)
    index += 1
im.fromarray(the_max).show()

len(tpages3)

# F I N D I N G  P I X E L S
i = 74
tpage = tpages2[i].copy()
im.fromarray(tpage).show()
tpage[300,:] = 255
tpage[:,180] = 255
tpage[300,180]

# P R E - C R O P
tpage2 = the_max.copy()
x_left = 100
x_right = 100
y_up = 150
y_down = 170
tpage2[y_up,:] = 255
tpage2[:,x_left] = 255
tpage2[-y_down,:] = 255
tpage2[:,-x_right] = 255
im.fromarray(tpage2).show()


custom_crop_params = [x_left, x_right, y_up, y_down]

for i in range(len(tpages3)):
    tpages3[i] = custom_crop(tpages3[i], custom_crop_params)


# standard procedure
all_slices = slice_pages(tpages3)
temp_dir_name = out_dir + 'temp'
temp_dir_name += '\\'
os.mkdir(temp_dir_name)

im.fromarray(all_slices[2]).show()

digits = len(str(len(all_slices)))

file_names = [str(i).rjust(digits, '0') + '.jpg' for i in range(len(all_slices))]

for index, slice in enumerate(all_slices):
    try:
        im.fromarray(255-slice).save(temp_dir_name + file_names[index])
    except:
        im.fromarray(255-slice).convert('RGB').save(temp_dir_name + file_names[index])
convert_to_epub_NO_BORDER(temp_dir_name, pdf_dir, pdf_title, all_slices)
shutil.rmtree(temp_dir_name)
'''


'''================================== END EXPERIMENTATION ZONE
==============================================================='''






data = p2i.convert_from_path(pdf_dir, fmt='png', thread_count=os.cpu_count())

imgs = make_numpy_arrays(data)
#imgs = [custom_crop(i, custom_crop_params) for i in imgs] # custom crop
all_slices = slice_pages(imgs)

# make temporary directory
temp_dir_name = out_dir + 'temp'
temp_dir_name += '\\'
os.mkdir(temp_dir_name)
# do the rest
save_images(all_slices, temp_dir_name)
#convert_to_epub(temp_dir_name, out_dir, pdf_title)

convert_to_epub_NO_BORDER(temp_dir_name, pdf_dir, pdf_title, all_slices)


1






















# a previous experiment
if False:


    i = 40
    tpage = (np.sum(255 - np.asarray(data[i]), axis=2)//3).astype(np.uint8)
    tpage[168,:] = 255
    tpage[201,:] = 255
    tpage[:,52] = 255
    tpage[:,213] = 255

    maxx = 0.
    minn = 9999.
    for i in range(1701):
        suoy = np.mean(tpage[:,i]).astype(np.int)
        maxx = np.max([maxx, suoy])
        if suoy != 0:
            minn = np.min([minn, suoy])
    maxx
    minn

    tpage[:,1000] = 255
    np.mean(tpage[:,52]).astype(np.int)
    ''' the max vertical displacement is 33 pixels, which can be at most 8415
    but on average is 161, or for the whole page is 2
    8415/2201 = 3.83
    '''


    im.fromarray(tpage).show()


    while True:
        if np.mean(tpage[:,i]) == 0:
            i += 1
        else:
            break
    print(i)




    tpage = (np.sum(255 - np.asarray(data[i]), axis=2)//3).astype(np.uint8)
    tpage2 = general_crop2(tpage)
    im.fromarray(tpage2).show()
    im.fromarray(tpage).show()




    # ready to finish
    data = p2i.convert_from_path(pdf_dir, fmt='png', thread_count=os.cpu_count())
    manual_crop = True
    all_slices = slice_pages()
    save_images()
    convert_to_epub()



    def general_crop2(tpage, step = 5, leniance = 15):
        special_value = 3.83 # crop value used in Spivak
        try:
            side_crop_left = 0
            side_crop_right = tpage.shape[1]-1
            top_crop = 0
            bot_crop = tpage.shape[0]-1
            # do vertical first, because horizontal has wider range
            while np.mean(tpage[:,side_crop_left]) < special_value:
                side_crop_left += step
            while np.mean(tpage[:,side_crop_right]) < special_value:
                side_crop_right -= step

            # fix these values so we can already use them in determining
            # the horizontal crop
            side_crop_left = max(0,side_crop_left - leniance)
            side_crop_right = min(tpage.shape[1]-1, side_crop_right + leniance)

            while np.mean(tpage[top_crop,side_crop_left:side_crop_right]) == 0:
                top_crop += step
            while np.mean(tpage[bot_crop,side_crop_left:side_crop_right]) == 0:
                bot_crop -= step

            top_crop = max(0, top_crop - leniance)
            bot_crop = min(tpage.shape[0]-1, bot_crop + leniance)
            return tpage[top_crop:bot_crop, side_crop_left:side_crop_right]

        except: # this is the case for blank pages
            print("something went wrong")
            return tpage
