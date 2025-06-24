import nebulatk as ntk


window = ntk.Window(width = 300, height = 600).place()


left_btn = ntk.Button(window, text = "<", height =50, width = 50).place(75,100)
right_btn = ntk.Button(window, text = ">", height =50, width = 50).place(175,100)

up_btn = ntk.Button(window, text = "^", height =50, width = 50).place(125,50)
down_btn = ntk.Button(window, text = "v", height =50, width = 50).place(125,150)


