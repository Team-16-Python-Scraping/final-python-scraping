from ast import arg
from concurrent.futures import thread
from tkinter import Toplevel, messagebox
import tkinter
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request
import requests
import os
from tqdm import tqdm #thư viện hiện tiến trình tải
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
from tkinter import ttk
from tkinter import Tk
import threading
from shopeeFunctions import getPosition


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
            soup = bs(page, 'lxml')
            for item in soup.findAll('a'):
                if item['href'].endswith('jpg'):
                    urls.append(item['href'])

            for item in soup.findAll('img'):
                if item is not None:
                    if item['src'].startswith('http'):
                        urls.append(item['src'])
            return urls     
    return None
        
    

def download(url, pathname):    #tải file ảnh với url vừa lấy được và đặt vào thư mục tự đặt tên
    if not os.path.isdir(pathname): # nếu không có directory của folder thì tạo
        os.makedirs(pathname)
    response = requests.get(url, stream=True)   # tải lần lượt theo từng url
    file_size = int(response.headers.get("Content-Length", 0))  # lấy dung lượng ảnh
    filename = os.path.join(pathname, url.split("/")[-1])   # lấy tên file ảnh
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024) # thanh tiến độ tải, chuyển về bytes thay vì iteration (mặc định trong thư viện tqdm)
    path = r'C:\team16\Images'
    files = os.listdir(path)
    with open(f'{path}\image{len(files)}.jpg', "wb") as f:
        for data in progress.iterable:
            f.write(data)   # chuyền dữ liệu đọc được vào file
            progress.update(len(data))  # cập nhật tiến độ tải

def showProgressBar(root):
    global win
    win = Toplevel()
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
    global win
    win.destroy()
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
        for img in imgs:
            try:
                cnt += 1
                if cnt > limit:
                    break
                download(img, path) # tải ảnh với mỗi url
            except:
                pass
        threading.Thread(target=endProgress, args=(tab2,)).start()
        messagebox.showinfo('Successfully', 'Đã download tất cả ảnh vào trong\n thư mục C:\\team16\\images')

