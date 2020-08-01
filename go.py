# press CTRL + K + 0    to collapse all functions
import pdf2image as p2i
from PIL import Image as im
from PIL import ImageEnhance
import numpy as np
import shutil, zipfile, os


work_dir = 'C:\\Users\\pwnag\\Desktop\\'

create_dir = lambda dir : os.mkdir(dir) if not os.path.exists(dir) else print("folder exists!")

def general_split(tpage, leniance = 20):
    v_split = tpage.shape[0]//2
    one_slice = np.transpose(tpage[:v_split + leniance,:])[::-1,:]
    two_slice = np.transpose(tpage[v_split-leniance:,:])[::-1,:]
    return [one_slice, two_slice]


def general_crop(tpage, leniance = 5, step = 5):
    try:
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
    except: # this is the case for blank pages
        return tpage


def convert_to_epub(temp_dir, output_dir, title, img_shapes):
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

    epub = zipfile.ZipFile(os.path.join(output_dir, title) + '.kepub.epub', 'w')
    epub.writestr("mimetype", "application/epub+zip")
    epub.writestr("META-INF/container.xml", container_xml)
    epub.writestr("OEBPS/nav.xhtml", nav_xhtml.format(title))
    epub.writestr("OEBPS/toc.ncx", toc_ncx)
    epub.writestr("OEBPS/Text/style/css", style_css)

    manifest, spine = '', ''

    images = [os.path.join(temp_dir, i) for i in os.listdir(temp_dir)]

    names = [format(i, '04d') for i in range(len(images))]

    # write cover (just duplicate images[0])
    im_content = open(images[0], 'rb').read()
    epub.writestr("OEBPS/Images/" + 'cover.jpg', im_content)

    # write the rest of the images
    index = 0
    for i in names:
        manifest += content_opf_manifest_template.format(i)
        spine += content_opf_spine_template.format(i)

        im_content = open(images[index], 'rb').read()

        image_width = img_shapes[index][0]
        image_height = img_shapes[index][1]

        index += 1
        epub.writestr("OEBPS/Images/" + i + '.jpg', im_content)

        xhtml_content = xhtml_template.format(i, image_width, image_height)
        epub.writestr("OEBPS/Text/{0}.xhtml".format(i), xhtml_content)

    # write content
    content_opf_final = content_opf_upper.format(title) + manifest + content_opf_middle + spine + content_opf_lower
    epub.writestr("OEBPS/content.opf", content_opf_final)
    epub.close()


''' TEST ZONE '''
LENIANCE = 5 # 5 normal, 20 for a smol border (for converting light novels)
pdfs = [work_dir + i for i in os.listdir(work_dir) if i[-4:] == '.pdf']

one_pdf = pdfs[0]    
pdf_title = one_pdf.split('\\')[-1].split('.')[0]
print("Starting:\n" + pdf_title)


'''
convert_from_path(pdf_path, dpi=200, output_folder=None, 
first_page=None, last_page=None, fmt='ppm', jpegopt=None, 
thread_count=1, userpw=None, use_cropbox=False, strict=False, 
transparent=False, single_file=False, output_file=str(uuid.uuid4()), 
poppler_path=None, grayscale=False, size=None, paths_only=False)
'''
data = p2i.convert_from_path(one_pdf, fmt='png', thread_count=os.cpu_count(), first_page = 69, last_page=96)



# make temporary directory
temp_dir = os.path.join(work_dir, 'temp')
create_dir(temp_dir)

# turn rendered image into Black & White numpy array 
imgs = [(np.sum(255 - np.asarray(i), axis=2)//3).astype(np.uint8) for i in data]
for i in range(len(imgs)): 
    imgs[i][np.where(imgs[i]==1)] = 0 # correct white pixels 
front_cover = imgs[0] # copy the original cover

# correct double covers 
fc_height, fc_width = front_cover.shape
if fc_height / fc_width < 1:
    front_cover = front_cover[:,fc_width//2:]




# custom crop 
if False:
        
    # P R E - C R O P
    # dark mode cropping master page - R U N  O N C E 
    BRUH = 50 # skip BRUH front / back pages 
    test_page_ = imgs[BRUH].copy() 
    for i in range(BRUH, len(imgs)-BRUH):
        test_page_ = np.maximum(test_page_, imgs[i])    

    # C R O P   D I M S   E X P E R I M E N T A T I O N 
    x_left = 480
    x_right = 220
    y_up = 200
    y_down = 200
    total_page = test_page_.copy()
    total_page[y_up,:] = 255
    total_page[:,x_left] = 255
    total_page[-y_down,:] = 255
    total_page[:,-x_right] = 255 
    im.fromarray(total_page).show()

    imgs = [i[y_up:-y_down:,x_left:-x_right] for i in imgs[1:]] # custom crop




# perform general crop and split
all_slices = [front_cover] 
for i in imgs: 
    all_slices += general_split(general_crop(i,LENIANCE)) 
img_shapes = [[i.shape[1], i.shape[0]] for i in all_slices] # width, height


# save imgs to temp dir
file_names = [str(i).rjust(4, '0') + '.jpg' for i in range(len(all_slices))]
for i, slice in enumerate(all_slices):
    im.fromarray(255-slice).save(os.path.join(temp_dir, file_names[i]))

#convert_to_epub(temp_dir, work_dir, pdf_title, img_shapes) # original without contrast
del all_slices, imgs 


# c o n t r a s t 
create_dir(temp_dir + '2')
images = [os.path.join(temp_dir, i) for i in os.listdir(temp_dir)]
file_names = [str(i).rjust(4, '0') + '.jpg' for i in range(len(images))]
shutil.copyfile(images[0], os.path.join(temp_dir+'2', file_names[0])) # dont modify cover
for i, imag in enumerate(images[1:],1):
    enhancer = ImageEnhance.Contrast(im.open(imag))
    enhancer.enhance(4.).save(os.path.join(temp_dir+'2', file_names[i]))

convert_to_epub(temp_dir + '2', work_dir, pdf_title, img_shapes)
shutil.rmtree(temp_dir)
shutil.rmtree(temp_dir + '2')

