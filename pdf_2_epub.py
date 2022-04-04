import pdf2image as p2i
from PIL import Image as im
from PIL import ImageEnhance
import numpy as np
import zipfile, os, io


out_dir = r'C:\Users\i_hat\Desktop'
POPPLER_PATH = r'C:\Users\i_hat\Desktop\bastl\py\4path\poppler\bin'


def make_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def general_split(p, leniance = 20):
    v_split                                 = p.shape[0]//2
    one_slice                               = p[:v_split + leniance,:].T[::-1,:]
    two_slice                               = p[v_split-leniance:,:].T[::-1,:]
    return [one_slice, two_slice]


def general_crop(p, leniance = 20, step = 5):
    try:
        side_crop_left                      = 0
        side_crop_right                     = p.shape[1]-1
        top_crop                            = 0
        bot_crop                            = p.shape[0]-1
        while np.mean(p[:,side_crop_left])  == 0: 
            side_crop_left                 += step
        while np.mean(p[:,side_crop_right]) == 0: 
            side_crop_right                -= step
        while np.mean(p[top_crop,:])        == 0: 
            top_crop                       += step
        while np.mean(p[bot_crop,:])        == 0: 
            bot_crop                       -= step
        side_crop_left                      = max(0,side_crop_left - leniance)
        side_crop_right                     = min(p.shape[1]-1, side_crop_right + leniance)
        top_crop                            = max(0, top_crop - leniance)
        bot_crop                            = min(p.shape[0]-1, bot_crop + leniance)
        return p[top_crop:bot_crop, side_crop_left:side_crop_right]
    except: # this is the case for blank pages
        return p


pdfs                                        = [os.path.join(out_dir, i) for i in os.listdir(out_dir) if i[-4:] == '.pdf']
one_pdf                                     = pdfs[0]    

for one_pdf in pdfs:
        
    pdf_title                                   = os.path.basename(one_pdf).split('.')[0]
    print(f"Starting:\n{pdf_title}")


    # convert_from_path(pdf_path, dpi=200, output_folder=None, 
    # first_page=None, last_page=None, fmt='ppm', jpegopt=None, 
    # thread_count=1, userpw=None, use_cropbox=False, strict=False, 
    # transparent=False, single_file=False, output_file=str(uuid.uuid4()), 
    # poppler_path=None, grayscale=False, size=None, paths_only=False)
    data = p2i.convert_from_path(one_pdf, fmt='png', thread_count=os.cpu_count(), poppler_path = POPPLER_PATH,
        dpi = 300)#, first_page = 69, last_page=96)


    # turn rendered image into Black & White numpy array 
    imgs = [(np.sum(255.0 - np.array(i), 2) / 3.0).astype(np.uint8) for i in data]
    for i in range(len(imgs)): 
        imgs[i][np.where(imgs[i]==1)] = 0 # correct white pixels 


    # perform general crop and split
    all_slices = [imgs[0]] # copy the original cover
    for i in imgs: 
        all_slices += general_split(general_crop(i)) 


    # c o n t r a s t   &   s a v e
    with zipfile.ZipFile(os.path.join(out_dir, f'{pdf_title}.cbz'), 'w') as zf:
        for i in range(1, len(all_slices)):
            file_object = io.BytesIO()
            e = ImageEnhance.Contrast(im.fromarray(255 - all_slices[i]))
            e.enhance(4.).save(file_object, "PNG")
            zf.writestr(f"{str(i).rjust(4, '0')}.png", file_object.getvalue())









'''

# custom crop 
    
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


'''