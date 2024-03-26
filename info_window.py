from tkinter import *

selected_filter = 0

def change_filter(filter):
	selected_filter = filter


if __name__ == '__main__':
	root = Tk()
	frame = Frame(root)
	frame.pack()

	redbutton = Button(frame, text = 'rainbow', fg ='red', command=change_filter(0))
	redbutton.pack( side = LEFT)

	greenbutton = Button(frame, text = 'sun', fg='brown')
	greenbutton.pack( side = LEFT )

	bluebutton = Button(frame, text ='purple', fg ='blue')
	bluebutton.pack( side = LEFT )

	blackbutton = Button(frame, text ='inverted', fg ='black')
	blackbutton.pack( side = LEFT)

	root.mainloop()
