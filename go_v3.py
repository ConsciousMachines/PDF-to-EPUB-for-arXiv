import pdf2image as p2i
from PIL import Image, ImageEnhance, ImageOps, ImageDraw
import numpy as np
import zipfile, os, io
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


out_dir = r'/home/chad/Desktop'
pdfs                                        = [os.path.join(out_dir, i) for i in os.listdir(out_dir) if i[-4:] == '.pdf']
one_pdf                                     = pdfs[0]
pdf_title                                   = os.path.basename(one_pdf).split('.')[0]
print(f"Starting:\n{pdf_title}")


def render_average_page(data): # what the average page looks like 
    try:
        BRUH           = 20 # skip BRUH front / back pages (covers are diff sizes)
        _test_page     = 255 - np.array(data[BRUH]).astype(np.uint8)
        for i in range(BRUH, len(data)-BRUH, 20):
            _test_page = np.maximum(_test_page, 255 - np.array(data[i]).astype(np.uint8)) 
        return (True, _test_page)
    except: # if the pages are all different sizes then we cant do it
        return (False, None)


# convert_from_path(pdf_path, dpi=200, output_folder=None, 
# first_page=None, last_page=None, fmt='ppm', jpegopt=None, 
# thread_count=1, userpw=None, use_cropbox=False, strict=False, 
# transparent=False, single_file=False, output_file=str(uuid.uuid4()), 
# poppler_path=None, grayscale=False, size=None, paths_only=False)
data = p2i.convert_from_path(one_pdf, fmt='jpg', thread_count=os.cpu_count(), grayscale=True,
    dpi = 300)#, first_page = 69, last_page=96)
success, avg_page = render_average_page(data)




class Viewer():
    def refresh(self, e):
        img                    = self.page.copy()
        width, height          = img.size
        # draw 
        x_left                 = self.vals[0].get()
        x_right                = self.vals[2].get()
        y_up                   = self.vals[1].get()
        y_down                 = self.vals[3].get()
        line_left              = [(x_left, 0), (x_left, height)]
        line_right             = [(width - x_right, 0), (width - x_right, height)]
        line_up                = [(0, y_up), (width, y_up)]
        line_down              = [(0, height - y_down), (width, height - y_down)]
        img1                   = ImageDraw.Draw(img)  
        img1.line(line_left,  fill ="red", width = 10)
        img1.line(line_right, fill ="red", width = 10)
        img1.line(line_up,    fill ="red", width = 10)
        img1.line(line_down,  fill ="red", width = 10)
        #resize
        if height > self.window_size:
            img = img.resize((int(self.window_size * (width / height)),self.window_size))

        self.photo = ImageTk.PhotoImage(image = img) # https://stackoverflow.com/questions/58411250/photoimage-zoom
        self.canvas_area.create_image(0,0,image = self.photo, anchor=tk.NW)
        self.canvas_area.update()

    def key_press(self, e):
        if e.keysym == 'Escape': # quit 
            return self.root.destroy()
        elif e.keysym == 'd':
            self.page_num += 1
        elif e.keysym == 'a':
            self.page_num -= 1
        self.page = data[self.page_num]
        self.refresh(0)

    def start(self, avg_page = None):
        self.page_num = len(data) // 2
        self.window_size = 1000
        if type(avg_page) == type(None):
            self.page = data[self.page_num]
        else:
            self.page = Image.fromarray(avg_page)
        
        self.root                                        = tk.Tk()
        self.menu_left                                   = tk.Canvas(self.root, width=150, height = 400, bg = 'black')
        self.menu_left.grid(row                          = 0, column=0, sticky = 'nsew')
        sf                                               = ttk.Frame(self.menu_left)
        sf.bind("<Configure>",  lambda e: self.menu_left.configure(scrollregion = self.menu_left.bbox("all")))
        self.root.bind('<Key>', lambda x: self.key_press(x))
        self.menu_left.create_window((0, 0), window      =sf, anchor="nw")

        self.vals                                        = [tk.DoubleVar() for i in range(4)]
        _labels = ['W', 'N', 'E', 'S']
        labs                                             = [ttk.Label(sf, text=_labels[i]) for i in range(4)]
        slds                                             = [None for i in range(4)]
        for i in range(4):
            slds[i]                                      = ttk.Scale(sf, from_ = 0.0, to = 2000.0, orient = 'vertical', 
                                    variable = self.vals[i], command = self.refresh, length = int(0.9 * self.window_size))
            slds[i].grid(column                          = i, row = 1, columnspan = 1, sticky = 'nsew')
            labs[i].grid(column                          = i, row = 0, columnspan = 1, sticky = 'nsew')

        self.canvas_area                                 = tk.Canvas(self.root, width=self.window_size, height=self.window_size, bg = 'black')
        self.canvas_area.grid(row                        = 0, column=1, sticky = 'nsew') 
        self.root.grid_rowconfigure(1, weight            = 1)
        self.root.grid_columnconfigure(1, weight         = 1)
        self.refresh(0)
        self.root.mainloop()

v  = Viewer()
v.start(avg_page)






x_left                 = v.vals[0].get()
x_right                = v.vals[2].get()
y_up                   = v.vals[1].get()
y_down                 = v.vals[3].get()

# c o n t r a s t   &   s a v e
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

