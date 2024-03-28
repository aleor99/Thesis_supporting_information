import tkinter as tk
from tkinter import filedialog
from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import serial
from serial.tools.list_ports import comports
import numpy as np
from statistics import mode
import pandas as pd


'''This function is used to convert the hexadecimal string in input to the capacitance string'''
def converti_valore(input):
    return ((input - 0x800000) / 0x800000) * 4.09


'''Converts the capacitance into force'''
def force(capacitance):
    return (((capacitance-0.43321)/3.1))


'''Save frequency and PW into .csv file'''
def save_csv(list):

    df=pd.DataFrame(list)  
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    df.to_csv(file_path, index=False, decimal=',')
    return 

'''Lists used to save instant pw and f'''
pw_list=[]
freq_list=[]

class SerialPlotter:
    def __init__(self, parent, serial_port, baud_rate):

        '''The function sends the string for the stimulation'''
        def send_parameter():
            pacing_text="<R,9,{:.2f},{:.2f}>".format(self.pw_selected.get(), self.freq_selected.get())
            pacing_text = pacing_text.ljust(19, ' ')
            self.serial_connection.write(pacing_text.encode())
            print(pacing_text)
            print(len(pacing_text))
            return
        
        def reset():
            pw_list.clear()
            freq_list.clear()
            return
        
        ''''///General parameters///'''
        self.parent = parent
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.count_freq=0
        self.prev_value=0
        self.raw_value=0
        self.freq_selected = DoubleVar()
        self.pw_selected = DoubleVar()
        self.force_value=0
        self.time_inc=0
        self.freqsum=0
        self.flag_down=0
        self.raw_value_volt=0
        self.y_tresh_high=10000000
        self.y_max_median=0
        self.y_min_median=0
        self.y_down=0
        self.y_up=0
        self.time_marked=0
        self.time_marked_new=0
        self.last=0
        self.timedown=0
        self.timeup=0
        self.pw_calc=0
        self.flag_pw=0
        self.flag_val=0
        self.pw_mean=0
        self.avg_freq=0
        self.prev_time_time=0
        self.time=0


        ''''///Labels and entries///'''
        self.csv_button = tk.Button(self.parent, text="Reset lists", command=reset)
        self.csv_button.pack(side=TOP,pady=20)
        self.avgfreqlbl=tk.Label(self.parent, text="average frequency=", bg="white", font=("Helvetica", 20, "bold"))
        self.avgfreqlbl.pack(side=BOTTOM, pady=10)
        self.freqlbl=tk.Label(self.parent, text="frequency=", bg="white", font=("Helvetica", 20, "bold"))
        self.freqlbl.pack(side=BOTTOM) 
        self.avgpwlbl=tk.Label(self.parent, text="average PW=", bg="white", font=("Helvetica", 20, "bold"))
        self.avgpwlbl.pack(side=BOTTOM, pady=30)
        self.pwlbl=tk.Label(self.parent, text="PW=", bg="white", font=("Helvetica", 20, "bold"))
        self.pwlbl.pack(side=BOTTOM)
        self.entrypw=tk.Entry(self.parent, textvariable=self.pw_selected, justify=RIGHT, bg="light grey", bd=2, selectborderwidth=2, selectforeground="grey", width=4)
        self.entrypw.pack(side=RIGHT, pady=50, padx=(0, 23))
        self.pw_label=tk.Label(self.parent, text="PW:", bg="white", font=("Helvetica", 12))
        self.pw_label.pack(side=RIGHT, pady=50)
        self.button_parameters = tk.Button(self.parent, text="Set parameters", command=send_parameter)
        self.button_parameters.pack(side=RIGHT, pady=(150,0))
        self.entryf=tk.Entry(self.parent, textvariable=self.freq_selected, justify=RIGHT, bg="light grey", bd=2, selectborderwidth=2, selectforeground="grey", width=4)
        self.entryf.pack(side=RIGHT, pady=50)
        self.f_label=tk.Label(self.parent, text="f:", bg="white", font=("Helvetica", 12))
        self.f_label.pack(side=RIGHT, pady=50)


        ''''///Plot parameters///'''
        self.fig = Figure(dpi=100)#dpi is the resolution
        self.fig.set_size_inches(14, 5)
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot([], [], label="Converted Value", color="blue" )
        self.linetrdown, = self.ax.plot([], [], label="trashold", color="red", linestyle="--" )
        self.linetrup, = self.ax.plot([], [], color="orange", linestyle="--" )
        self.ax.legend(loc='upper right')
        self.ax.set_xlabel('Time (s)')

        if conv_mod==1:
            self.ax.set_ylabel('Force of contraction') 
        else:
            self.ax.set_ylabel('Voltage')
        
        self.ax.set_title('Values plot on the serial port', fontsize= 10)
        self.ax.grid()

        # Set initial y-axis limits
        if conv_mod==1:
            self.ax.set_ylim(0.0004, 0.0009) #just arbitrary set of the y limits 
        else:
            self.ax.set_ylim(8399621, 8600000000) 


        def format_newton(value, _):
            return f"{value:.5f} N"

        if conv_mod==1:
            self.ax.yaxis.set_major_formatter(plt.FuncFormatter(format_newton))
        

        ''''///Initialization lists///'''
        self.serial_data = []
        self.x_data = []
        self.x_datatr = []
        self.frame_index = 0
        self.y_min_list=[]
        self.y_max_list=[]
        self.trdown_list=[]
        self.trup_list=[]
        self.y_min_dac=[]
        self.y_max_dac=[]
        

        ''''///Serial connection///'''
        self.serial_connection = None
        try:
            self.serial_connection = serial.Serial(self.serial_port, self.baud_rate)
            print(f"Serial connection on {self.serial_port}.")
        except serial.SerialException as se:
            print(f"Error on the serial connection: {se}")
    

    def update_plot(self, _):
        
        dato = self.serial_connection.readline().decode('utf-8').strip()

        ''''///String conversion///'''
        if len(dato) >= 6:
            dato_hex = dato[:6]   
            self.raw_value = int(dato_hex, 16)
            self.prev_time_time=self.time   #the previous time is saved in order to measure the PW with the previous time istant (sharp peak problem)
            self.time=self.frame_index*conv_time
            self.x_data.append(self.time) 

            ''''///Actions specific for the conversion mode///'''
            if conv_mod==1:
                converted_value = converti_valore(self.raw_value)
                self.prev_value=self.force_value
                self.force_value=force(converted_value)
                self.serial_data.append(self.force_value)
                if (self.prev_value>self.y_down and self.force_value<self.y_down): 
                        self.flag_pw=0
                        if(self.time>4):
                            self.pw_calc=round(self.time-self.timeup,4)
                            pw_list.append(self.pw_calc)
                            self.pw_mean=np.mean(pw_list)
                            avgpw_text = "average PW={:.2f}s".format(self.pw_mean)
                            pw_text = "PW={:.2f}s".format(self.pw_calc)
                            self.pwlbl.config( text=pw_text, bg="white", font=("Helvetica", 20, "bold"))
                            self.avgpwlbl.config( text=avgpw_text, bg="white", font=("Helvetica", 20, "bold"))
                else:
                    self.flag_down=0
                if (self.prev_value<self.y_down and self.force_value>self.y_down):
                    self.timeup=self.prev_time_time #made for the sharp peak generated, otherways can be:
                    #self.timeup=self.time
                    self.flag_pw=1

            else:
                self.prev_value=self.raw_value_volt
                self.raw_value_volt = self.raw_value
                self.serial_data.append(self.raw_value_volt)
                if (self.prev_value>self.y_down and self.raw_value<self.y_down):
                    self.flag_down=1
                    if(self.flag_pw==1):
                        self.flag_pw=0
                        if(self.time>4): #it waits 4 seconds before the tresholds are set
                            self.pw_calc=round(self.time-self.timeup,4)
                            pw_list.append(self.pw_calc)
                            self.pw_mean=np.mean(pw_list)
                            avgpw_text = "average PW={:.3f}s".format(self.pw_mean)
                            pw_text = "PW={:.3f}s".format(self.pw_calc)
                            self.pwlbl.config( text=pw_text, bg="white", font=("Helvetica", 20, "bold"))
                            self.avgpwlbl.config( text=avgpw_text, bg="white", font=("Helvetica", 20, "bold"))
                else:
                    self.flag_down=0
                if (self.prev_value<self.y_down and self.raw_value>self.y_down): 
                    self.timeup=self.prev_time_time #made for the sharp peak generated, otherways can be:
                    #self.timeup=self.time
                    self.flag_pw=1


            ''''///Frequency calculation///'''
            if ((self.flag_down==1) and (self.time>4)):
                self.prev_time=self.time_inc
                self.time_inc=self.time
                freq=1/(self.time_inc-self.prev_time)
                freq_list.append(freq)
                self.avg_freq=np.mean(freq_list)
                if freq<self.avg_freq/2 or freq>self.avg_freq*2 : #related to the printing of * in strange values
                    self.time_marked=self.time
                    self.time_marked_new=1
                freq_text = "frequency={:.2f}Hz".format(freq)
                avgfreq_text = "average frequency={:.2f}Hz".format(self.avg_freq)
                self.freqlbl.config( text=freq_text, bg="white", font=("Helvetica", 20, "bold"))
                self.avgfreqlbl.config( text=avgfreq_text, bg="white", font=("Helvetica", 20, "bold"))        
            
            ''''///Set treshold///'''
            self.y_down=(self.y_min_median +(self.y_max_median-self.y_min_median)*0.06) #arbitrary treshold, change it in order to set the y _down (to distinguish the low values to noise)         
            self.treshold=(self.y_up-self.y_down)
            self.trdown_list.append(self.y_down) #added into the lists to be plotted as red dashed lines
            if conv_mod ==1:
                if(self.force_value>self.y_tresh_high):
                    self.trup_list.append(self.force_value)# to plot the highs 
                    self.last=self.force_value
                else:
                    self.trup_list.append(self.last)
            else:
                if(self.raw_value_volt>self.y_tresh_high):
                    self.trup_list.append(self.raw_value_volt)
                    self.last=self.raw_value_volt
                else:
                    self.trup_list.append(self.last)
            self.y_up=self.trup_list[-1] 
                

            ''''///Update plots///'''
            self.line.set_data(self.x_data, self.serial_data)
            self.line.axes.set_xlim(left=max(0, (self.frame_index - 100)*conv_time), right=self.time)

            ''' //used to highlight strange values, it overloads the code 
            if self.time_marked_new==1:
                if conv_mod==1:
                    self.ax.scatter(self.time_marked, self.force_value, color='green', marker='*')
                else:
                    self.ax.scatter(self.time_marked, self.raw_value_volt, color='green', marker='*')
                self.time_marked_new=0
            '''
            self.linetrdown.set_data(self.x_data, self.trdown_list)
            self.linetrdown.axes.set_xlim(left=max(0, (self.frame_index - 100)*conv_time), right=self.time)
            self.linetrup.set_data(self.x_data, self.trup_list)
            self.linetrup.axes.set_xlim(left=max(0, (self.frame_index - 100)*conv_time), right=self.time)

            ''''///Update y range///'''
            if self.serial_data:
                y_min, y_max = min(self.serial_data[-70:]), max(self.serial_data[-70:])
                self.line.axes.set_ylim(y_min/1.001, y_max*1.001)
                self.y_max_list.append(y_max)
                self.y_min_list.append(y_min)
                self.y_min_dac.append(max(self.y_min_list[-20:]))
                self.y_max_dac.append(min(self.y_max_list[-20:]))
                self.y_min_median=mode(self.y_min_dac)
                self.y_max_median=mode(self.y_max_dac)
                self.y_tresh_high=(((self.y_max_median-self.y_min_median)/2)+self.y_min_median)
                self.line.axes.set_xlim(left=max(0, (self.frame_index - 100)*conv_time), right=self.time)
            self.frame_index += 1

            # Update the canvas
            self.canvas.draw()


        # Schedule the next update
        self.after_id = self.parent.after(10, self.update_plot, None)#aggiorna

    '''///Polt management function///'''

    def embed_plot(self):
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent) #funzione che mette la fihuar nel widget in pratica
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.NONE, expand=FALSE)#questo lo posiziona dopo averlo creato 
        self.canvas.draw()#dovrebbe disegnarlo aggiornando qualche valore tipo

        # Start animation loop
        self.update_plot(None)
    
    def clear_plot(self):
        self.serial_data = []
        self.x_data = []
        self.frame_index = 0

        self.line.set_data([], [])
        self.line.axes.set_xlim(0, 1)
        self.line.axes.set_ylim(0, 1)

        self.canvas.draw()

    def stop_animation(self):
        if hasattr(self, 'after_id'):
            self.parent.after_cancel(self.after_id)
            self.clear_plot()
    
    def destroy_plot(self):
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
    #funzione che stoppa l'animazione, legata ad after
    def close_serial_connection(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Serial connection closed.")

BAUD_rate=""
porta_COM=""
conv_time=""
conv_mod=""

def MainWindow():

    def connection():
        global serial_plotter
        serial_plotter = SerialPlotter(panel1, serial_port=porta_COM, baud_rate=BAUD_rate)
        serial_plotter.embed_plot()
        my_button.config(text="Disconnect", command =lambda: disconnection())
        return
    
    def disconnection():        
        global serial_plotter
        root.after(100, serial_plotter.stop_animation())
        my_menu.entryconfig("COM ports", state="normal")
        my_menu.entryconfig("Baudrate", state="normal")
        my_menu.entryconfig("Conversion frequency", state="normal")
        serial_plotter.destroy_plot()
        serial_plotter.close_serial_connection()
        my_button.config(text="Connection", command=lambda: (root.after(100, connection())))
        return
        

    def enable_button():
        if BAUD_rate and porta_COM and conv_time:
            my_button.config(state="normal")
        return

    def COM_sel(porta):
        global porta_COM
        my_menu.entryconfig("COM ports",state="disabled")
        porta_COM=f"{porta}"[:4]
        enable_button()
        return
    
    def baud_0():
        global BAUD_rate
        BAUD_rate="9600"
        enable_button()
        return


    def baud_1():
        global BAUD_rate
        BAUD_rate="115200"
        enable_button()
        return
    
    def baud_2():
        global BAUD_rate
        BAUD_rate="230400"
        enable_button()
        return

    def baud_3():
        global BAUD_rate
        BAUD_rate="250000"
        enable_button()
        return
    
    def COM_ports():
        for port in comports():
            COM_menu.add_command(label=f"{port}", command=lambda p=port: COM_sel(p))

    def freq_1():
        global conv_time
        if conv_mod==1:
            conv_time=(110.79*0.062+0.2332)/78
        else:
            conv_time=(149.07*0.1221+0.0752)/59

        #conv_time=(7.11)/78
        enable_button()
        return

    def freq_2():
        global conv_time
        if conv_mod==1:
            conv_time=(110.79*0.038+0.2332)/92
        else:
            conv_time=(149.07*0.0621+0.0752)/62
        #conv_time=(7.11)/80
        enable_button()
        return
    
    def freq_3():
        global conv_time
        if conv_mod==1:
            conv_time=((110.79*0.02+0.2332)/86)*1.98
        else:
            conv_time=((149.07*0.0312+0.0752)/78)*1.068
        #conv_time=(4.57)/80
        enable_button()
        return

    def freq_4():
        global conv_time
        if conv_mod==1:
            conv_time=((110.79*0.0119+0.2332)/78)*0.9375
        else:
            conv_time=((149.07*0.0201+0.0752)/86)*1.07
        #conv_time=(2.50)/80
        enable_button()
        return

    def freq_5():
        global conv_time
        conv_time=((110.79*0.011+0.2332)/84)*0.909091
        #conv_time=(1.87)/80
        enable_button()
        return
    
    def Capacitance():
        global conv_mod
        conv_mod=1
        my_menu.entryconfig("Conversion frequency", state="normal")
        convfreq_menu.add_command(label="16.1Hz",command= lambda:[freq_1(), my_menu.entryconfig("Conversion frequency", state="disabled")])
        convfreq_menu.add_command(label="26.3Hz",command= lambda:[freq_2(), my_menu.entryconfig("Conversion frequency", state="disabled")])
        convfreq_menu.add_command(label="50.0Hz",command= lambda:[freq_3(), my_menu.entryconfig("Conversion frequency", state="disabled")])
        convfreq_menu.add_command(label="83.8Hz",command= lambda:[freq_4(), my_menu.entryconfig("Conversion frequency", state="disabled")])
        convfreq_menu.add_command(label="90.9Hz",command= lambda:[freq_5(), my_menu.entryconfig("Conversion frequency", state="disabled")])
        enable_button()
        return
    
    def Voltage():
        global conv_mod
        conv_mod=0
        my_menu.entryconfig("Conversion frequency", state="normal")
        convfreq_menu.add_command(label="8.2Hz", state="normal",command= lambda:[freq_1(), my_menu.entryconfig("Conversion frequency", state="disabled")])
        convfreq_menu.add_command(label="16.1Hz", state="normal",command= lambda:[freq_2(), my_menu.entryconfig("Conversion frequency", state="disabled")])
        convfreq_menu.add_command(label="31.2Hz", state="normal",command= lambda:[freq_3(), my_menu.entryconfig("Conversion frequency", state="disabled")])
        convfreq_menu.add_command(label="49.8Hz", state="normal",command= lambda:[freq_4(), my_menu.entryconfig("Conversion frequency", state="disabled")])
        enable_button()
        return


    root = Tk()
    root.title('PACING GUI')
    #root.iconbitmap("tudelft_fire.ico") here you should put the pathway for the icon 
    #root.iconbitmap("C:/Users/39345/Desktop/Università Milano/Polimi/Tesi/Theis_project_third/immagini_gui/tudelft_fire.ico")
    root.geometry("1200x900")

    paned_window1 = tk.PanedWindow(bd=4, relief="raised", orient=VERTICAL)
    paned_window1.pack(expand=True, fill=tk.BOTH)

    panel1 = tk.Frame(paned_window1, height=200, bg="white")
    paned_window1.add(panel1)


    my_menu = Menu(root)
    file_menu = Menu(my_menu, tearoff=0)
    root.config(menu=my_menu)
    
    file_menu.add_command(label="Save frequency", command=lambda: save_csv(freq_list))
    file_menu.add_command(label="Save pulse width", command=lambda: save_csv(pw_list))      
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=lambda: root.quit())
    my_menu.add_cascade(label="File", menu=file_menu)

    
    
    baud_menu = Menu(file_menu, tearoff=0)
  
    baud_menu.add_command(label="9600", command= lambda:[baud_0( ), my_menu.entryconfig("Baudrate", state="disabled")])
    baud_menu.add_command(label="115200", command= lambda:[baud_1( ), my_menu.entryconfig("Baudrate", state="disabled")])
    baud_menu.add_command(label="230400", command=lambda:[baud_2( ), my_menu.entryconfig("Baudrate", state="disabled")])
    baud_menu.add_command(label="250000", command=lambda:[baud_3( ), my_menu.entryconfig("Baudrate", state="disabled")])
    my_menu.add_cascade(label="Baudrate", menu=baud_menu)

    COM_menu = Menu(file_menu, tearoff=0)
    COM_ports()
    my_menu.add_cascade(label="COM ports", menu=COM_menu)

    mod_menu = Menu(file_menu, tearoff=0)

    mod_menu.add_command(label="Capacitance", command= lambda:[Capacitance(), my_menu.entryconfig("Conversion modality", state="disabled")])
    mod_menu.add_command(label="Voltage", command= lambda:[Voltage(), my_menu.entryconfig("Conversion modality", state="disabled")])
    my_menu.add_cascade(label="Conversion modality", menu=mod_menu)

    convfreq_menu = Menu(file_menu, tearoff=0)
    my_menu.add_cascade(label="Conversion frequency", menu=convfreq_menu)
    my_menu.entryconfig("Conversion frequency", state="disabled")

    


    my_button = tk.Button(panel1, text="Connect", command=connection, state="disabled")
    my_button.pack(pady=10)

    #https://ultrapythonic.com/tkinter-panedwindow/                c'e' tantissimo qui, guardare bene  


    root.mainloop()

if __name__ == "__main__":
    MainWindow()
