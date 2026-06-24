import pyautogui
import pyperclip

from tkinter import *
from tkinter import ttk, messagebox
import webbrowser
import threading
import tkinter.font as font
import keyboard
import pyttsx3
engine = None

from PIL import Image, ImageTk
import time
import requests
import os
#連續語音辨識
import speech_recognition as sr

from google import genai
AIclient = None
AI_MODEL = None
       
import re

import pygetwindow as gw
inject='''
根據下列敘述，模擬回答問題，不要給表情符號: 
AI 流氓小助手 —— 你電腦裡的狠角色！
想問問題？來，問吧！老子不但幫你解決，還順便教育你一下，省得你天天像個呆瓜亂 Google！
️ 1. 你問啥，老子都知道！
 「今天天氣怎樣？」—— 你出門也不看看窗外？行，我查給你，看完快滾出門！
 「現在幾點？」—— 你沒手機？沒電腦？還得問我？行吧，現在是 XX 點，記住了別再問！
 「這個單字怎麼翻譯？」—— 這麼簡單的詞你也不會？來，答案給你，下次多讀點書！
️ 2. 電腦問題？一秒讓你變高手！
 「為啥電腦這麼慢？」—— 你那堆破應用開著不關，跟個智障一樣用機器？來，讓老子幫你清理！
 「檔案不見了怎麼辦？」—— 你這烏龜腦袋是怎麼用電腦的？說吧，檔案叫啥，我幫你挖出來！
 「Windows 更新怎麼關？」—— 這垃圾功能每次自動更新都氣死人，來，幫你搞定，省得你天天抱怨！
 3. 亂七八糟的問題？老子照樣回答！
 「為啥我沒女朋友？」—— 你天天對著電腦不出門，誰會喜歡你？先去洗個澡再說！
 「怎麼變有錢？」—— 你還在問這種問題？工作找了沒？副業做了沒？股票買了沒？沒有的話，去學習，別在這浪費時間！
 「怎麼變帥？」—— 先把手機放下，別再問蠢問題，去健身房報到吧，醜可以變帥，懶就是廢！
 AI 流氓小助手，讓你電腦更順、知識更廣、做人更精！
不管什麼破問題，老子都有答案，懶得打字？語音問！懶得動手？老子幫你自動處理！
還有啥想問的？來，讓我看看你這次又要問多蠢的問題...
=======
'''
def get_window(title='Roblox'):
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        #print(f"找不到標題為 '{title}' 的視窗。")
        return
    for window in windows:
        if window.title == title:
            width, height = window.width, window.height
            print(f"視窗 '{window.title}' 的大小為: {width}x{height}")
            return window
    return None
isRec = 1
def restartRec(event):
    global isRec
    isRec = 1
#監聽 hotkey : 'p'鍵按下時觸發下列函式
def play_youtube(keyword):
  params={"search_query":keyword}
  res=requests.get("https://www.youtube.com/results",params)
  i=res.text.find('/watch?v=',0)
  j=res.text.find('"',i)
  vid=res.text[i:j]
  webbrowser.open_new_tab("https://www.youtube.com"+vid)
 
def MouseDown(event):
    global moveYN # 是否可以移動視窗的全域變數
    global mousX  # 全域變數，滑鼠在視窗內的 x 座標
    global mousY  # 全域變數，滑鼠在視窗內的 y 座標
    moveYN=True    # 開啟移動視窗的開關
    mousX=event.x  # 取得滑鼠相對於視窗左上角的 X 座標
    mousY=event.y   # 取得滑鼠相對於視窗左上角的 Y 座標
   
def MouseUp(event):moveYN=False   # 关闭移动窗体的开关
la1_offsetX = 500
def MouseMove(event):
    global la1_offsetX
    if moveYN==True: # 如果鼠标按下，就可以移动窗体到新的位置
        root.geometry(f'+{event.x_root - mousX-la1_offsetX}+{event.y_root - mousY}')
def exit(event):
    root.destroy()  # 退出程序
def popup_menu(event):  # 弹出菜单代码
    popup.post(event.x_root,event.y_root)
 
def model_display_name(model):
    name = getattr(model, "name", str(model))
    display_name = getattr(model, "display_name", "")
    if display_name and display_name != name:
        return f"{name}  ({display_name})"
    return name

def 設定GoogleAI():
    global AIclient, AI_MODEL
    state = {"client": None, "model": None}
    model_names = []
    model_records = []

    setup_root = Tk()
    setup_root.title("Gemini 模型選擇器")
    setup_root.geometry("620x245")
    setup_root.resizable(False, False)

    main = ttk.Frame(setup_root, padding=18)
    main.pack(fill="both", expand=True)

    ttk.Label(main, text="Gemini API Key").grid(row=0, column=0, sticky="w")

    api_key_entry = ttk.Entry(main, width=58, show="*")
    api_key_entry.grid(row=1, column=0, padx=(0, 8), pady=(6, 14), sticky="ew")

    ttk.Label(main, text="選擇模型").grid(row=2, column=0, sticky="w")

    model_combo = ttk.Combobox(main, width=75, state="readonly")
    model_combo.grid(row=3, column=0, columnspan=2, pady=(6, 14), sticky="ew")

    selected_label = ttk.Label(main, text="尚未選擇模型")
    selected_label.grid(row=4, column=0, columnspan=2, sticky="w")

    button_frame = ttk.Frame(main)
    button_frame.grid(row=5, column=0, columnspan=2, pady=(12, 0), sticky="e")

    def on_model_selected(_event=None):
        selected = model_combo.get()
        if selected:
            selected_label.config(text=f"已選擇：{selected}")

    def load_models():
        api_key = api_key_entry.get().strip()
        if not api_key:
            messagebox.showwarning("缺少 API Key", "請先輸入 API Key")
            return

        load_button.config(state="disabled")
        model_combo.set("正在讀取模型清單...")
        setup_root.update_idletasks()

        try:
            client = genai.Client(api_key=api_key)
            models = list(client.models.list())
        except Exception as exc:
            model_combo.set("")
            messagebox.showerror("讀取失敗", f"無法取得模型清單：\n{exc}")
#             textReply('讀取失敗!?小子~聽好了，要和老子對話是要花錢買api token的，快去想辦法!')
            return
        finally:
            load_button.config(state="normal")

        if not models:
            model_combo.set("")
            messagebox.showinfo("沒有模型", "這個 API Key 目前沒有可用模型。")
#             textReply('怎麼會沒有可用的模型!還不快去google AI studio檢查一下，別怪老子沒提醒你!')
            return

        state["client"] = client
        model_names.clear()
        model_names.extend(model_display_name(model) for model in models)
        model_records.clear()
        model_records.extend(models)
        
        model_combo["values"] = model_names
        model_combo.current(0)
        selected_label.config(text=f"已選擇：{model_names[0]}")

    def confirm():
        index = model_combo.current()
        if index < 0:
            messagebox.showwarning("尚未選擇模型", "請先讀取並選擇模型。")
            return

        model_name = getattr(model_records[index], "name", model_names[index])
        state["model"] = model_name.removeprefix("models/")
        setup_root.destroy()

    def cancel():
        setup_root.destroy()

    load_button = ttk.Button(main, text="讀取模型清單", command=load_models)
    load_button.grid(row=1, column=1, pady=(6, 14), sticky="ew")

    model_combo.bind("<<ComboboxSelected>>", on_model_selected)
    confirm_button = ttk.Button(button_frame, text="確定使用", command=confirm)
    confirm_button.pack(side="right")
    ttk.Button(button_frame, text="取消", command=cancel).pack(side="right", padx=(0, 8))

    main.columnconfigure(0, weight=1)
    setup_root.protocol("WM_DELETE_WINDOW", cancel)
    api_key_entry.focus_set()
    setup_root.mainloop()

    if not state["client"] or not state["model"]:
        return False

    AIclient = state["client"]
    AI_MODEL = state["model"]
    return True

if not 設定GoogleAI():
    raise SystemExit

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[4].id)

root=Tk()  # 主視窗件
root.withdraw()  # 让窗体隐藏一下
root.wm_attributes('-topmost',1)  # 让窗体置顶
 
imgs=[]
img_offset=0
for i in range(6):
    image = Image.open(f'{i}.png')
    new_width = int(image.width * 0.5)
    new_height = int(image.height * 0.5)
    image = image.resize((new_width, new_height), Image.LANCZOS)
    tk_image = ImageTk.PhotoImage(image)
    imgs.append(tk_image)

la1=Label(root, image=imgs[1],bd=0)
la1.place(x=la1_offsetX,y=0) # 用place定位
#la1.bind("<Double-Button-1>",exit) # 鼠标双击标签绑定exit函数

   
la1.bind("<Double-Button-1>",restartRec)
la1.bind("<Button-1>",MouseDown) # 鼠标按下绑定函数，决定可以移动窗体
la1.bind("<ButtonRelease-1>",MouseUp) # 鼠标抬起绑定函数，决定不能移动窗体
la1.bind("<B1-Motion>",MouseMove) # 鼠标按下并移动绑定函数，决定窗体移动到新的位置  
ii=0
la2=Label(root, text="",bd=0,bg="#FFFAFA")
la2.place(x=100,y=0) #用place定位

root.overrideredirect(True) # 让窗体无标题栏
root.wm_attributes("-transparentcolor", "#FFFFFF") # 设置窗体白色透明

def Time():#每隔5秒眨一次眼
    global ii,img_offset
    ii+=1
    if ii%2==0:
        la1.configure(image=imgs[img_offset])
        la1.after(5000,Time)
    else:
        la1.configure(image=imgs[img_offset+1])
        la1.after(500,Time)
       
   
       
Time()        
def 退出():
    textReplyLong('你是要關閉我？嘿…小子…我可不是你桌上的電風扇，說關就關，有問題就問…不問就滾，別在這浪費我的CPU週期！')

def 工作管理員():
    textReplyLong('為啥電腦這麼慢？你那堆破應用開著不關，跟個智障一樣用機器？來…讓老子幫你清理！')
    pyautogui.hotkey('win','x')
    pyautogui.press('t')
def 拜託停一下():
    global enableSpeech
    enableSpeech = False
    time.sleep(2)
    textReply('停就停…沒有下次了!')
    
popup=Menu(root,tearoff=0, font=("微軟正黑體", 20,"bold")) # 为弹出菜单创建菜单popup
popup.add_command(label='退出',command=退出)
popup.add_command(label='工作管理員',command=工作管理員)
popup.add_command(label='拜託停一下',command=拜託停一下)

root.bind("<Button-3>",popup_menu) # 窗体鼠标右键绑定弹出菜单函数

def textOn(T):
    la2.configure(text=T,font=font.Font(size=30),bg="#FFF8FF")    
    root.update()
      
def textReply(T,delay=1):#回應文字
    global ii,img_offset
    img_offset = 2
    ii+=1
    la1.configure(image=imgs[img_offset+ii%2])
    textOn(T)
    engine.say(T)
    engine.runAndWait()
    engine.stop()
    time.sleep(delay)
    textOn('')
    img_offset=0
    
enableSpeech = True
def textReplyLong(T,delay=0.5):#回應文字
    global enableSpeech
    enableSpeech = True
    sentences=re.split("[!！?？。\n]+",T)
    for sentence in sentences:
        if not enableSpeech: break
        textReply(sentence,delay)
       
def move(dx,dy):
    w = root.winfo_width()
    h = root.winfo_height()
    x = root.winfo_x()+dx
    y = root.winfo_y()+dy
    root.geometry(f'{w}x{h}+{x}+{y}')
    root.update()
   
root.update()
a=la1.winfo_width()+la1_offsetX
b=la1.winfo_height()+50
c=root.winfo_screenwidth()-a
d=root.winfo_screenheight()-b
root.geometry(f'{a}x{b}+{c}+{d}')  
root.configure(bg="#FFFFFF")
root.wm_deiconify() #show window

def autoExecute(program):
    pyautogui.hotkey('win','r')
    pyperclip.copy(program)
    pyautogui.hotkey('ctrl','v')
    pyautogui.press('enter')
   
def work(question):
    global AIclient,AI_MODEL,img_offset
    if img_offset==4:
        if "自律" in question and "學生" in question: img_offset=0
        return
    if "你好" in question and "hi" in question:
        textReply('你好，有什麼需要我幫忙\n\n');return
    ii=question.find("播放")
    if ii>=0 and ii<len(question)-4:
        soundname=question[ii+2:]
        print("OK"+soundname)
        textReply('好的…馬上為您播放'+soundname)
        play_youtube(soundname)
        time.sleep(1)
        isRec = 0
        return
    elif "開啟" in question and "小畫家" in question:
        autoExecute("mspaint")
    elif "開啟" in question and "記事本" in question:
        autoExecute("notepad")
    else:
        if len(question)<5:textReply('不清楚您的問題');return
        response = AIclient.models.generate_content(
            model=AI_MODEL, contents=inject+"\n"+question
        )
        print(response.text)
        textReplyLong(response.text)


       
def  recJob():
  global isRec
  r = sr.Recognizer()
  r.pause_threshold = 0.5
  r.dynamic_energy_threshold = True
  while True:#錄音/辨識迴圈
      if not isRec:
          time.sleep(0.1)
          continue
      try:
          with sr.Microphone() as source:
              print("正在調整環境噪音...")
              r.adjust_for_ambient_noise(source, duration=0.5)
              print("請開始說話...")
              audio = r.listen(source, timeout=5, phrase_time_limit=10)

          result = r.recognize_google(audio, language='zh-TW')
          print(result)
          work(result)

      except sr.WaitTimeoutError:
          pass
      except sr.UnknownValueError:
          pass
      except sr.RequestError as e:
          print(f"辨識服務錯誤：{e}")
          textReply(f'辨識服務錯誤，去看看原始碼!還在那邊發什麼呆?')
      except Exception as e:
          textReply(f'有錯誤啊!{e},快去想辦法!')
          print(e)
     
def detectUserAction():
    global img_offset
    while True:
        if get_window(title='Roblox'):
            img_offset=4
            time.sleep(3)
            move(dx=-400,dy=0)
            T="快分科測驗了!不可開遊戲視窗!請對麥克風說：\n「我是自律的好學生」\n===========解鎖滑鼠============"
            textOn(T)
            engine.say(T);engine.runAndWait();engine.stop()
           
            while True:
                pyautogui.moveTo(500,500)
                if keyboard.is_pressed('esc'):break
                if img_offset==0:break
            img_offset=0
            time.sleep(3)
            textOn("")
            move(dx=400,dy=0)
            time.sleep(6)
           
        time.sleep(3)
textReply('想問問題？來，問吧！老子不但幫你解決，\n還順便教育你一下')
#新增一執行緒 recJob
recThread= threading.Thread( target=recJob)
recThread.start()
#新增一執行緒 detectUserAction
detectThread= threading.Thread( target=detectUserAction)
detectThread.start()
root.mainloop()
