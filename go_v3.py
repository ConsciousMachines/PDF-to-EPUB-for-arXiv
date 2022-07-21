import pdf2image as p2i
from PIL import Image, ImageEnhance, ImageOps
import numpy as np
import zipfile, os, io


out_dir = r'/home/chad/Desktop'


def pil_2_np(i): # convert PIL image to numpy
    return (255.0 - np.array(i)).astype(np.uint8)


pdfs                                        = [os.path.join(out_dir, i) for i in os.listdir(out_dir) if i[-4:] == '.pdf']
one_pdf                                     = pdfs[0]
pdf_title                                   = os.path.basename(one_pdf).split('.')[0]
print(f"Starting:\n{pdf_title}")


# convert_from_path(pdf_path, dpi=200, output_folder=None, 
# first_page=None, last_page=None, fmt='ppm', jpegopt=None, 
# thread_count=1, userpw=None, use_cropbox=False, strict=False, 
# transparent=False, single_file=False, output_file=str(uuid.uuid4()), 
# poppler_path=None, grayscale=False, size=None, paths_only=False)
data = p2i.convert_from_path(one_pdf, fmt='jpg', thread_count=os.cpu_count(), grayscale=True,
    dpi = 300)#, first_page = 69, last_page=96)


# custom crop 
CUSTOM_CROP = True    
# P R E - C R O P
# dark mode cropping master page - R U N  O N C E 
BRUH = 20 # skip BRUH front / back pages 
test_page_ = pil_2_np(data[BRUH]) 
for i in range(BRUH, len(data)-BRUH, 20):
    test_page_ = np.maximum(test_page_, pil_2_np(data[i]))    
# C R O P   D I M S   E X P E R I M E N T A T I O N 
x_left = 250
x_right = 250
y_up = 150
y_down = 170
total_page = test_page_.copy()
total_page[y_up,:] = 255
total_page[:,x_left] = 255
total_page[-y_down,:] = 255
total_page[:,-x_right] = 255 
Image.fromarray(total_page).show()




with zipfile.ZipFile(os.path.join(out_dir, f'{pdf_title}.cbz'), 'w') as zf:

    # write the original cover
    file_object = io.BytesIO() # https://stackoverflow.com/questions/63439403/how-to-create-a-zip-file-in-memory-with-a-list-of-pil-image-objects
    data[0].save(file_object, 'jpeg')
    zf.writestr('0000.jpg', file_object.getvalue())

    for i in range(1, len(data)):
        
        # memory management, otherwise process gets killed
        data[i-1] = None 

        # crop
        width, height = data[i].size
        _cropped = data[i].crop((x_left + 1, y_up + 1, width - x_right, height - y_down))

        # enhance contrast
        _enhanced = ImageEnhance.Contrast(_cropped).enhance(4.)

        # rotate 90 deg 
        _rot = _enhanced.transpose(Image.ROTATE_90)

        # split 
        leniance = 20
        width, height = _rot.size
        _one_slice = _rot.crop((0,0,width // 2 + leniance + 1,height))
        _two_slice = _rot.crop((width // 2 - leniance,0,width,height))

        # write
        _ = file_object.seek(0)
        _ = file_object.truncate(0)
        _one_slice.save(file_object, 'jpeg')
        zf.writestr(f"{str(i*2-1).rjust(4, '0')}.jpg", file_object.getvalue())
        _ = file_object.seek(0)
        _ = file_object.truncate(0)
        _two_slice.save(file_object, 'jpeg')
        zf.writestr(f"{str(i * 2).rjust(4, '0')}.jpg", file_object.getvalue())

