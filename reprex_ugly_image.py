import tkinter as tk
from PIL import Image, ImageTk

def main():
    root = tk.Tk()
    image_file_100 = Image.open('test images/100w/btn_render_flatter.png')
    image = ImageTk.PhotoImage(image_file_100)

    label = tk.Label(root,image=image)
    label.pack()

    image_file_400 = Image.open('test images/400h/btn_render_flatter.png').resize((200,52), Image.ANTIALIAS)
    image400 = ImageTk.PhotoImage(image_file_400)

    label400 = tk.Label(root,image=image400)
    label400.pack()


    root.mainloop()

if __name__ == '__main__':
    main()