from tkinter import Toplevel, messagebox
import tkinter
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request
import requests
import os
from selenium import webdriver
from tqdm import tqdm #thư viện hiện tiến trình tải
from bs4 import BeautifulSoup as bs
from tkinter import ttk
import threading
from tkinter import filedialog
from shopeeFunctions import getPosition
import time
PATH = r'C:\Program Files (x86)\Chromedriver\chromedriver.exe' #link to chromedriver app in your pc

def get_url(url):   # get link ảnh vào urls = []
    urls = []
    if len(url) == 0:
        messagebox.showerror('Error', 'Bạn chưa nhập URL!')
    else:
        try:
            hdr = {'User-Agent': 'Mozilla/5.0'}
            req = Request(url,headers=hdr)
            page = urlopen(req)
        except TimeoutError as e:
            messagebox.showerror('Error', 'Time out')
        except HTTPError as e:
            messagebox.showerror('Error', 'Không tồn tại trang web')
        except URLError as e:
            messagebox.showerror('Error', 'URL không hợp lệ')   
        except:
            messagebox.showerror('Error', 'Đã có lỗi xảy ra\nVui lòng thử lại')
        else:
            try:
                driver = webdriver.Chrome(executable_path=PATH)
                driver.get(url)
                time.sleep(2)
                for i in range(70):
                    totalScrolledHeight = driver.execute_script("return window.pageYOffset + window.innerHeight")
                    height = int(driver.execute_script("return document.documentElement.scrollHeight"))
                    if totalScrolledHeight == height:
                        break
                    driver.execute_script('window.scrollBy(0, 600)')
                    time.sleep(0.1)
                # the script above for auto scroll in order to display all items which are written by js
                html = driver.page_source
                driver.close()
                soup = bs(html, 'lxml')

                for item in soup.findAll('img', {'src' : True}):
                    if item is not None:
                        if item['src'].startswith('http'):
                            urls.append(item['src'])
                return urls     
            except:
                messagebox.showerror('Error', 'Có lỗi xảy ra\nVui lòng thử lại')
                return None
    return None
        
def showProgressBar(root):
    global win, pb
    win = Toplevel()
    win.title('Đang xử lý...')
    win.attributes("-topmost", True)
    win.geometry(getPosition(root, 300, 120))
    win.resizable(False, False)
    pb = ttk.Progressbar(
            win,
            orient='horizontal',
            mode='indeterminate',
            length=280
        )
    pb.grid(row=0, column=0, columnspan=2, padx=10, pady=20)
    cancel_button = ttk.Button(
        win,
        text='Cancel',
        command=win.destroy
    )
    cancel_button.grid(column=0, row=1, padx=10, pady=10, sticky=tkinter.E)
    pb.start()
def endProgress(root):
    global win, pb
    pb.destroy()
    win.destroy() 

def download(url, pathname):    #tải file ảnh với url vừa lấy được và đặt vào thư mục tự đặt tên
    if not os.path.isdir(pathname): # nếu không có directory của folder thì tạo
        os.makedirs(pathname)
    response = requests.get(url, stream=True)   # tải lần lượt theo từng url
    file_size = int(response.headers.get("Content-Length", 0))  # lấy dung lượng ảnh
    filename = os.path.join(pathname, url.split("/")[-1])   # lấy tên file ảnh
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024) # thanh tiến độ tải, chuyển về bytes thay vì iteration (mặc định trong thư viện tqdm)
    files = os.listdir(pathname)
    ext = url[url.rindex('.'):]
    if ext.startswith('.png'):
        ext = '.png'
    elif ext.startswith('.jpg'):
        ext = '.jpg'
    elif ext.startswith('.jfif'):
        ext = '.jfif'
    elif ext.startswith('.com'):
        ext = '.jpg'
    elif ext.startswith('.svg'):
        ext = '.svg'
    with open(f'{pathname}\image{len(files)}{ext}', "wb") as f:
        for data in progress.iterable:
            f.write(data)   # chuyền dữ liệu đọc được vào file
            progress.update(len(data))  # cập nhật tiến độ tải

def getImage_run(tab2, url, path, limit):
    if limit == '':
        limit = 10 ** 6
    else:
        try:
            limit = int(limit)
        except:
            messagebox.showerror('Error', 'Mời bạn nhập đúng định dạng')
            return
    imgs = get_url(url)  # lấy url ảnh
    if imgs == None:
        return
    else:
        threading.Thread(target=showProgressBar, args=(tab2,)).start()
        cnt = 0
        thread = []
        for img in imgs:
            try:
                cnt += 1
                if cnt > limit:
                    break
                p = threading.Thread(target=download, args=(img, path))
                p.start()
                thread.append(p)
                # download(img, path) # tải ảnh với mỗi url
            except:
                pass
        for th in thread:
            th.join()
        threading.Thread(target=endProgress, args=(tab2,)).start()
        response = messagebox.askokcancel("Successfully","Bạn có muốn mở thư mục không?")
        if response == 1 : showFolder()
def showFolder():
    filedialog.askopenfile(initialdir=r"C:/team16/images",title="Select a File",filetypes=(("jpg files","*.jpg"),
                                                                                            ('jfif files', '*.jfif'),
                                                                                            ("png files", "*.png"), 
                                                                                            ('svg files', '*.svg'), 
                                                                                            ("all files","*.*")))
       
