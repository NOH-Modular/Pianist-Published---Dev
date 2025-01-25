### NOH-modular Pianist firmware v2.0 - licensed under a CC-BY-NC-SA 4.0 license - https://creativecommons.org/licenses/by-nc-sa/4.0/
#Library Imports
from machine import Pin, PWM, I2C, Timer
from oled import Write, GFX
from oled.fonts import ubuntu_12, ubuntu_20
import framebuf, ad5593_edited, rp2, ssd1306, gc, micropython

micropython.alloc_emergency_exception_buf(100)

################################################################################################################################################################
### Pin and object Definition
### Screen and Menu Set-up ###

W = 128
H = 64

i2c = I2C(1,scl=Pin(3),sda=Pin(2),freq=400000)
oled = ssd1306.SSD1306_I2C(128,64,i2c)
draw = GFX(128,64,oled.pixel)
WriteS = Write(oled, ubuntu_12)
WriteL = Write(oled, ubuntu_20)
WriteF = oled

### Pi Pico Pin Set-up ###

J_center = Pin(18, Pin.IN, Pin.PULL_UP)
J_up = Pin(0, Pin.IN, Pin.PULL_UP)
J_down = Pin(26, Pin.IN, Pin.PULL_UP)
J_left = Pin(19, Pin.IN, Pin.PULL_UP)
J_right = Pin(1, Pin.IN, Pin.PULL_UP)
RGB_r = Pin(21, Pin.OUT)
RGB_g = Pin(20, Pin.OUT)
RGB_b =  Pin(22, Pin.OUT)
PS_led = Pin(11, Pin.OUT)
Gate_input = Pin(17, Pin.IN, Pin.PULL_DOWN)
PS_input = Pin(16, Pin.IN, Pin.PULL_DOWN)
Clock = Pin(15, Pin.IN)

################################################################################################################################################################
### Widget Class and objects --> needs libraries --> WriteS, oled, 

def abstractmethod(f):
    return f

class Widget():
    @abstractmethod
    def print_w(self):
        #when the widget is printed on screen
        pass

    @abstractmethod
    def default_print_f(self):
        #the default function that widgets use to print themselves
        pass

    @abstractmethod
    def click_w(self):
        #when the widget is clicked on
        pass

    def set_surrounding_widgets(self, up=None, down=None, left=None, right=None):
        self.navigation = [up,down,left,right]

    def outline_w(self,mask=False):
        #when the widget is the current one selected
        oled.rect(self.outline_x,self.outline_y,self.outline_length,self.outline_height,not mask)
        oled.show()

### navigation Widgets ###

class Nav_widget(Widget):
    save_slots = []

    def __init__(self, label, size, position, outline, custom_print_f = None, click_f = None):
        #text to display and its size
        self.label = label
        self.size = size
        #x and y coordinates of the text
        self.x, self.y = position
        #the outline when the widget is selected
        self.outline_x, self.outline_y, self.outline_length, self.outline_height = outline
        #setting the printing fuction to default or a user-set custom one
        self.print_f = self.default_print_f
        if custom_print_f != None: self.print_f = custom_print_f
        #setting the click fuction if there is one other than navigating to the menu
        self.click_f = click_f
        #generates the navigation widgets to None for now --> forces user definition
        self.set_surrounding_widgets()

    def default_print_f(self,obj,label,size,x,y):
        oled.fill_rect(obj.outline_x,obj.outline_y,obj.outline_length,obj.outline_height,False)
        size.text(label,x,y)

    def print_w(self):
        self.print_f(self,self.label,self.size,self.x,self.y)

    def click_w(self):
        if self.click_f == None: pass
        else: self.click_f()
        self.destination.enter()

    def set_destination_menu(self,menu):
        self.destination = menu

### navigation objects in main menu ###

global_menu_widget = Nav_widget('-global-',WriteS,[85,0],[80,0,48,14])
chord_menu_widget = Nav_widget('-chord-',WriteS,[37,0],[31,0,46,14])
edit_menu_widget = Nav_widget('edit',WriteS,[3,0],[0,0,28,14])

edit_menu_back_widget = Nav_widget('back',WriteS,[52,10],[48,10,33,14])
copy_widget = Nav_widget('copy',WriteS,[30,24],[28,25,32,14])
paste_widget = Nav_widget('paste',WriteS,[29,38],[27,38,33,15])
clear_widget = Nav_widget('clear',WriteS,[72,24],[69,25,31,14])
clear_all_widget = Nav_widget('cl. all',WriteS,[72,38],[69,38,33,14])

### navigation objects in chord menu ###

chord_menu_back_widget = Nav_widget('- back -',WriteS,[4,0],[0,0,44,14])
chord_menu_clear_widget = Nav_widget('clear',WriteS,[95,0],[86,0,42,14])

### navigation objects in global menu page 1 ###

global_menu_back_widget = Nav_widget('- back -',WriteS,[47,0],[43,0,44,14])
for i in range(4):
    Nav_widget.save_slots.append(Nav_widget(str(i+1),WriteS,[53+(20*i),47],[46+(20*i),46,20,16]))
global_menu_to_2_widget = Nav_widget('>>>',WriteS,[98,0],[86,0,42,14])

### navigation objects in global menu page 2 ###

global_menu_2_back_widget = Nav_widget('- back -',WriteS,[47,0],[43,0,44,14])
global_menu_to_1_widget = Nav_widget('<<<',WriteS,[14,0],[0,0,44,14])
calibration_widget = Nav_widget('calibr.',WriteS,[91,47],[88,46,38,16])

### navigation objects in calibration menu ###

calibration_cancel_widget = Nav_widget('- cancel -',WriteS,[44,0],[39,0,53,14])
calibration_save_widget = Nav_widget('- save & exit -',WriteS,[29,47],[22,46,83,16])

################################################################################################################################################################
### browse Widgets ###

class Browse_widget(Widget):
    selection_timer = Timer()
    selection_blink_time = 300
    selection_blink_flag = False

    root_options = ['   A','Bb','   B','   C','Db','   D',' Eb','   E','   F','Gb','   G','Ab']
    root_condensed_options = ['A','Bb','B','C','Db','D','Eb','E','F','Gb ','G','Ab']
    third_options = [' _','M', '+','m','o','o']
    seventh_options = ['_','7']
    color_options = ['  _','sus2','sus4','b5','#5','b6','add6','min7','maj7','oct.','b9 ','add9','#9','b11','add11','#11']
    over_options = [' _','A','Bb','B','C','Db','D','Eb',' E',' F','Gb',' G','Ab']
    page_options = ['1','2','3','4']

    shift_options = ['   -',' + 1',' + 2',' + 3',' + 4',' + 5',' + 6',' + 7',' + 8',' + 9',' +10',
                     '  -10','  - 9','  - 8','  - 7','  - 6','  - 5','  - 4','  - 3','  - 2','  - 1']
    spread_options = ['   -',' + 1',' + 2',' + 3',' + 4',' + 5',' + 6',' + 7',' + 8',' + 9',' +10']
    repeat_options = ['  -','x 1','x 2','x 3','x 4','x 5','x 6','x 7','x 8','x 9','x10','x11','x12','x13','x14','x15']

    gate_options = [' reset','randm','  shift','spread','freeze',' jump']
    mode_options = ['normal',' chord',' plaits',' organ']
    scale_options  = ['free','maj','min','dor.','phr.','lyd.','myx','locr.']
    save_options = ['load   -','save   -']
    brightness_options = ['low','med',' full']

    offset_options = ['   _',' + 1',' + 2',' + 3',' + 4',' + 5',' + 6',' + 7',' + 8',' + 9','+10','+11','+12','+13','+14','+15',
                     ' -15',' -14',' -13',' -12',' -11',' -10','  - 9','  - 8','  - 7','  - 6','  - 5','  - 4','  - 3','  - 2','  - 1']

    def __init__(self, options, size, position, outline, custom_print_f = None):
        #whether the widget is being edited (e.g. changing the root of a chord)
        self.currently_edited = False
        #text or number to display
        self.options = options
        self.counter = 0
        #size of the text
        self.size = size
        #x and y coordinates of the text
        self.x, self.y = position
        #the outline when the widget is selected
        self.outline_x, self.outline_y, self.outline_length, self.outline_height = outline
        #setting the printing fuction to default or a user-set custom one
        self.print_f = self.default_print_f
        if custom_print_f != None: self.print_f = custom_print_f
        #generates the navigation widgets to None for now --> forces user definition
        self.set_surrounding_widgets()

    def default_print_f(self,obj,options,counter,size,x,y):
        oled.fill_rect(obj.outline_x,obj.outline_y,obj.outline_length,obj.outline_height,False)
        if type(options)==int: size.text(str(counter+1),x,y)
        else: size.text(options[counter],x,y)

    def print_w(self):
        self.print_f(self,self.options,self.counter,self.size,self.x,self.y)

    def click_w(self):
        self.currently_edited = not self.currently_edited
        if self.currently_edited: 
            Browse_widget.selection_timer.init(mode = Timer.PERIODIC, period = Browse_widget.selection_blink_time, callback = self.selection_blink)
        else: 
            Browse_widget.selection_timer.deinit()
            Browse_widget.selection_blink_flag = False
            self.outline_w()

    def update_w(self,direction):
        if direction>1: pass
        else:
            if type(self.options)==int: self.counter = (self.counter+(1-(2*direction)))%self.options
            else: self.counter = (self.counter+(1-(2*direction)))%len(self.options)
            self.print_w()
            oled.show()

    def selection_blink(self,source):
        Browse_widget.selection_blink_flag = not Browse_widget.selection_blink_flag
        self.outline_w(Browse_widget.selection_blink_flag)
    
################################################################################################################################################################
### Custom browse object functions ###

def print_number(obj,options,counter,size,x,y):
    oled.fill_rect(obj.outline_x,obj.outline_y,obj.outline_length,obj.outline_height,False)
    if counter > 8: size.text(str(counter+1),x,y)
    else: size.text(str(counter+1),x+3,y)

def print_number_w_zero(obj,options,counter,size,x,y):
    oled.fill_rect(obj.outline_x,obj.outline_y,obj.outline_length,obj.outline_height,False)
    if counter==0: size.text('  -',x-1,y)
    elif counter > 9: size.text(str(counter),x,y)
    else: size.text(str(counter),x+3,y)

def print_chord_navigation(obj,options,counter,size,x,y):
    oled.fill_rect(obj.outline_x,obj.outline_y,obj.outline_length,obj.outline_height,False)
    size.text(options[counter],x,y)
    if counter > 8: size.text(str(counter+1),x+24,y)
    else: size.text(str(counter+1),x+27,y)
    oled.vline(65,4,7,1)

def print_calib_vout(obj,options,counter,size,x,y):
    oled.fill_rect(obj.outline_x,obj.outline_y,obj.outline_length,obj.outline_height,False)
    if counter==0: WriteS.text('0.25',48,26)
    else: WriteL.text(str(counter),54,19)
    WriteL.text('V',71,19)

### browse objects for main menu ### --> NEED TO MAKE 32 COPIES OF EACH CHORD INFO, MAKE A CLASS TO MANAGE THAT

root_widget = Browse_widget(Browse_widget.root_options,WriteL,[3,21],[0,20,30,24])
third_widget = Browse_widget(Browse_widget.third_options,WriteL,[32,21],[30,20,20,24])
seventh_widget = Browse_widget(Browse_widget.seventh_options,WriteL,[52,21],[50,20,17,24])
color_1_widget = Browse_widget(Browse_widget.color_options,WriteS,[69,18],[67,17,35,16])
color_2_widget = Browse_widget(Browse_widget.color_options,WriteS,[69,32],[67,32,35,15])
over_widget = Browse_widget(Browse_widget.over_options,WriteS,[109,27],[106,20,22,24])
page_widget = Browse_widget(4,WriteS,[4,50],[0,50,14,14])

### browse objects for chord menu ###

chord_navigation_widget = Browse_widget(Browse_widget.root_condensed_options,WriteS,[47,0],[43,0,44,14],print_chord_navigation)

shift_widget = Browse_widget(Browse_widget.shift_options,WriteS,[54,29],[45,29,40,14])
spread_widget = Browse_widget(Browse_widget.spread_options,WriteS,[97,29],[88,29,38,14])

go_to_chord_widget = Browse_widget(33,WriteS,[39,47],[35,46,20,16],print_number_w_zero)
go_to_repeat_widget = Browse_widget(Browse_widget.repeat_options,WriteS,[58,47],[55,46,22,16])
go_to_then_widget = Browse_widget(32,WriteS,[110,47],[106,46,20,16],print_number)

### browse objects for global menu page 1 ###

gate_widget = Browse_widget(Browse_widget.gate_options,WriteS,[6,29],[2,29,40,14])
mode_widget = Browse_widget(Browse_widget.mode_options,WriteS,[47,29],[45,29,40,14])
scale_widget = Browse_widget(Browse_widget.scale_options,WriteS,[97,29],[88,29,38,14])
save_widget = Browse_widget(Browse_widget.save_options,WriteS,[8,47],[2,46,34,16])

### browse objects for global menu page 2 ###

jump_min_widget = Browse_widget(32,WriteS,[47,29],[45,29,16,14],print_number)
jump_max_widget = Browse_widget(32,WriteS,[71,29],[69,29,16,14],print_number)
brightness_widget = Browse_widget(Browse_widget.brightness_options,WriteS,[96,29],[88,29,38,14])
scale_root_widget = Browse_widget(Browse_widget.root_condensed_options,WriteS,[64,47],[60,46,25,16])

### browse objects for calibration menu ###

calibration_channel_widget = Browse_widget(8,WriteL,[16,19],[2,17,40,26])
calibration_vout_widget = Browse_widget(6,WriteL,[16,19],[45,17,40,26],print_calib_vout)
calibration_offset_widget = Browse_widget(Browse_widget.offset_options,WriteL,[89,19],[88,17,38,26])

################################################################################################################################################################
### toggle Widgets class ###

class Toggle_widget(Widget):
    on_off = ['on','off']
    sequence_view_options = ['normal','  none  ']

    def __init__(self, options, size, position, outline, custom_print_f = None):
        #text to display and its size
        self.options = options
        self.state = False
        self.size = size
        #x and y coordinates of the text
        self.x, self.y = position
        #the outline when the widget is selected
        self.outline_x, self.outline_y, self.outline_length, self.outline_height = outline
        #setting the printing fuction to default or a user-set custom one
        self.print_f = self.default_print_f
        if custom_print_f != None: self.print_f = custom_print_f
        #generates the navigation widgets to None for now --> forces user definition
        self.set_surrounding_widgets()

    def default_print_f(self,obj,options,state,size,x,y):
        oled.fill_rect(obj.outline_x,obj.outline_y,obj.outline_length,obj.outline_height,False)
        size.text(options[state],x,y)

    def print_w(self):
        self.print_f(self,self.options,self.state,self.size,self.x,self.y)

    def click_w(self):
        self.state = not self.state
        self.print_w()
        self.outline_w()

class Cell_widget(Toggle_widget):
    cells = []
    current_cell = None

    def __init__(self, position, outline, custom_print_f = None):
        #setting the state
        self.state = False
        Cell_widget.current_cell = self
        #x and y coordinates of the text
        self.x, self.y = position
        #the outline when the widget is selected
        self.outline_x, self.outline_y, self.outline_length, self.outline_height = outline
        #setting the printing fuction to default or a user-set custom one
        self.print_f = self.default_print_f
        if custom_print_f != None: self.print_f = custom_print_f
        #generates the navigation widgets to None for now --> forces user definition
        self.set_surrounding_widgets()

    def default_print_f(self,obj,state,x,y):
        oled.rect(x,y,7,8,state,False)
        oled.rect(x+1,y+1,5,6,state,False)

    def print_w(self):
        self.print_f(self,self.state,self.x,self.y)

    def click_w(self):
        if self == Cell_widget.current_cell: pass
        else:
            Cell_widget.current_cell.state = False
            Cell_widget.current_cell.print_w()
            Cell_widget.current_cell = self
            self.state = True
            self.print_w()
            oled.show()

### toggle objects in main menu ###

for i in range(8):
    Cell_widget.cells.append(Cell_widget([19+(14*i),52],[18+(14*i),51,9,10]))

### toggle objects in chord menu ###

voicing_widget = Toggle_widget(Toggle_widget.on_off,WriteS,[14,29],[2,29,40,14])

### toggle objects in global menu page 2 ###

sequence_view_widget = Toggle_widget(Toggle_widget.sequence_view_options,WriteS,[4,29],[2,29,40,14])

################################################################################################################################################################
### widget navigation settings ###
### main menu ###

global_menu_widget.set_surrounding_widgets(None,color_1_widget,chord_menu_widget,None)
chord_menu_widget.set_surrounding_widgets(None,third_widget,edit_menu_widget,global_menu_widget)
edit_menu_widget.set_surrounding_widgets(None,root_widget,None,chord_menu_widget)

root_widget.set_surrounding_widgets(edit_menu_widget,page_widget,None,third_widget)
third_widget.set_surrounding_widgets(chord_menu_widget,Cell_widget.cells[1],root_widget,seventh_widget)
seventh_widget.set_surrounding_widgets(chord_menu_widget,Cell_widget.cells[2],third_widget,color_1_widget)
color_1_widget.set_surrounding_widgets(global_menu_widget,color_2_widget,seventh_widget,over_widget)
color_2_widget.set_surrounding_widgets(color_1_widget,Cell_widget.cells[4],seventh_widget,over_widget)
over_widget.set_surrounding_widgets(global_menu_widget,Cell_widget.cells[6],color_1_widget,None)

page_widget.set_surrounding_widgets(root_widget,None,None,Cell_widget.cells[0])
Cell_widget.cells[0].set_surrounding_widgets(root_widget,None,page_widget,Cell_widget.cells[1])
Cell_widget.cells[1].set_surrounding_widgets(third_widget,None,Cell_widget.cells[0],Cell_widget.cells[2])
Cell_widget.cells[2].set_surrounding_widgets(seventh_widget,None,Cell_widget.cells[1],Cell_widget.cells[3])
Cell_widget.cells[3].set_surrounding_widgets(seventh_widget,None,Cell_widget.cells[2],Cell_widget.cells[4])
Cell_widget.cells[4].set_surrounding_widgets(color_2_widget,None,Cell_widget.cells[3],Cell_widget.cells[5])
Cell_widget.cells[5].set_surrounding_widgets(color_2_widget,None,Cell_widget.cells[4],Cell_widget.cells[6])
Cell_widget.cells[6].set_surrounding_widgets(over_widget,None,Cell_widget.cells[5],Cell_widget.cells[7])
Cell_widget.cells[7].set_surrounding_widgets(over_widget,None,Cell_widget.cells[6],None)

### edit menu ###

edit_menu_back_widget.set_surrounding_widgets(None,copy_widget,None,None)
copy_widget.set_surrounding_widgets(edit_menu_back_widget,paste_widget,None,clear_widget)
paste_widget.set_surrounding_widgets(copy_widget,None,None,clear_all_widget)
clear_widget.set_surrounding_widgets(edit_menu_back_widget,clear_all_widget,copy_widget,None)
clear_all_widget.set_surrounding_widgets(clear_widget,None,paste_widget,None)

### chord menu ###

chord_menu_back_widget.set_surrounding_widgets(None,voicing_widget,None,chord_navigation_widget)
chord_navigation_widget.set_surrounding_widgets(None,shift_widget,chord_menu_back_widget,chord_menu_clear_widget)
chord_menu_clear_widget.set_surrounding_widgets(None,spread_widget,chord_navigation_widget,None)

voicing_widget.set_surrounding_widgets(chord_menu_back_widget,go_to_chord_widget,None,shift_widget)
shift_widget.set_surrounding_widgets(chord_navigation_widget,go_to_repeat_widget,voicing_widget,spread_widget)
spread_widget.set_surrounding_widgets(chord_menu_clear_widget,go_to_then_widget,shift_widget,None)

go_to_chord_widget.set_surrounding_widgets(voicing_widget,None,None,go_to_repeat_widget)
go_to_repeat_widget.set_surrounding_widgets(shift_widget,None,go_to_chord_widget,go_to_then_widget)
go_to_then_widget.set_surrounding_widgets(spread_widget,None,go_to_repeat_widget,None)

### global menu page 1 ###

global_menu_back_widget.set_surrounding_widgets(None,mode_widget,None,global_menu_to_2_widget)
global_menu_to_2_widget.set_surrounding_widgets(None,scale_widget,global_menu_back_widget,None)

gate_widget.set_surrounding_widgets(global_menu_back_widget,save_widget,None,mode_widget)
mode_widget.set_surrounding_widgets(global_menu_back_widget,Nav_widget.save_slots[0],gate_widget,scale_widget)
scale_widget.set_surrounding_widgets(global_menu_to_2_widget,Nav_widget.save_slots[2],mode_widget,None)

save_widget.set_surrounding_widgets(gate_widget,None,None,Nav_widget.save_slots[0])
Nav_widget.save_slots[0].set_surrounding_widgets(mode_widget,None,save_widget,Nav_widget.save_slots[1])
Nav_widget.save_slots[1].set_surrounding_widgets(mode_widget,None,Nav_widget.save_slots[0],Nav_widget.save_slots[2])
Nav_widget.save_slots[2].set_surrounding_widgets(scale_widget,None,Nav_widget.save_slots[1],Nav_widget.save_slots[3])
Nav_widget.save_slots[3].set_surrounding_widgets(scale_widget,None,Nav_widget.save_slots[2],None)

### global menu page 2 ###

global_menu_2_back_widget.set_surrounding_widgets(None,jump_min_widget,global_menu_to_1_widget,None)
global_menu_to_1_widget.set_surrounding_widgets(None,sequence_view_widget,None,global_menu_2_back_widget)

sequence_view_widget.set_surrounding_widgets(global_menu_to_1_widget,scale_root_widget,None,jump_min_widget)
jump_min_widget.set_surrounding_widgets(global_menu_2_back_widget,scale_root_widget,sequence_view_widget,jump_max_widget)
jump_max_widget.set_surrounding_widgets(global_menu_2_back_widget,scale_root_widget,jump_min_widget,brightness_widget)
brightness_widget.set_surrounding_widgets(global_menu_2_back_widget,calibration_widget,jump_max_widget,None)

scale_root_widget.set_surrounding_widgets(jump_max_widget,None,None,calibration_widget)
calibration_widget.set_surrounding_widgets(brightness_widget,None,scale_root_widget,None)

### calibration menu ###

calibration_cancel_widget.set_surrounding_widgets(None,calibration_vout_widget,None,None)

calibration_channel_widget.set_surrounding_widgets(calibration_cancel_widget,calibration_save_widget,None,calibration_vout_widget)
calibration_vout_widget.set_surrounding_widgets(calibration_cancel_widget,calibration_save_widget,calibration_channel_widget,calibration_offset_widget)
calibration_offset_widget.set_surrounding_widgets(calibration_cancel_widget,calibration_save_widget,calibration_vout_widget,None)

calibration_save_widget.set_surrounding_widgets(calibration_vout_widget,None,None,None)

################################################################################################################################################################
### Joystick interrupt handlers

class Control_handler:
    handler_pins = []
    handlers = []
    timer = Timer()
    buffer_time = 150
    buffer_time_release = 20
    active_irq = None

    @classmethod
    def disable_all(cls):
        for obj in cls.handlers:
            obj.disable()

    @classmethod
    def enable_all(cls):
        for obj in cls.handlers:
            obj.enable()

    @classmethod
    def timer_callback(cls,source):
        cls.enable_all()
        if cls.active_irq.name.value() == cls.active_irq.detection and cls.active_irq.repeat_flag:
            cls.active_irq.handler_f(None)

    @classmethod
    def trigger_buffer(cls):
        cls.timer.init(mode = Timer.ONE_SHOT, period = cls.buffer_time, callback = cls.timer_callback)

    @classmethod
    def trigger_buffer_release(cls):
        cls.timer.init(mode = Timer.ONE_SHOT, period = cls.buffer_time_release, callback = cls.timer_callback)

    def __init__(self,pin_name,handler_f,detection,flag = True):
        #list of listeners
        self.delegates = []
        #used to call functions relating to the GPIO pin defined
        self.name = pin_name
        #registering the interrupt and the GPIO pin in the list
        Control_handler.handler_pins.append(self.name)
        Control_handler.handlers.append(self)
        #setting whether the interrupt repeats if the control is held (e.g. keeping the joystick up would indefinitely go up)
        self.repeat_flag = flag
        #passing the handler function
        self.handler_f = handler_f
        #setting whether the interrupt is on a rising edge or a falling edge
        self.detection = detection
        self.edge = Pin.IRQ_FALLING
        if detection: self.edge = Pin.IRQ_RISING
        self.enable()
        
    def enable(self):
        self.name.irq(handler=self.handler_f,trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)

    def disable(self):
        self.name.irq(handler=None,trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)

    def register(self,listeners):
        if type(listeners) == list:
            for obj in listeners:
                self.delegates.append(obj)
        else:
            self.delegates.append(listeners)


def J_center_handler(pin):
    Control_handler.disable_all()
    Control_handler.active_irq = J_center_irq

    if not pin.value():
        for delegate in Control_handler.active_irq.delegates:
            if delegate.button_event(4): break
        Control_handler.trigger_buffer()
    else: Control_handler.trigger_buffer_release()
J_center_irq = Control_handler(J_center,J_center_handler,False,False)

def J_up_handler(pin):
    Control_handler.disable_all()
    Control_handler.active_irq = J_up_irq

    for delegate in Control_handler.active_irq.delegates:
            if delegate.button_event(0): break
    
    Control_handler.trigger_buffer()
J_up_irq = Control_handler(J_up,J_up_handler,False)

def J_down_handler(pin):
    Control_handler.disable_all()
    Control_handler.active_irq = J_down_irq

    for delegate in Control_handler.active_irq.delegates:
            if delegate.button_event(1): break

    Control_handler.trigger_buffer()
J_down_irq = Control_handler(J_down,J_down_handler,False)

def J_left_handler(pin):
    Control_handler.disable_all()
    Control_handler.active_irq = J_left_irq

    for delegate in Control_handler.active_irq.delegates:
            if delegate.button_event(2): break

    Control_handler.trigger_buffer()
J_left_irq = Control_handler(J_left,J_left_handler,False)

def J_right_handler(pin):
    Control_handler.disable_all()
    Control_handler.active_irq = J_right_irq

    for delegate in Control_handler.active_irq.delegates:
            if delegate.button_event(3): break

    Control_handler.trigger_buffer()
J_right_irq = Control_handler(J_right,J_right_handler,False)

################################################################################################################################################################
### Menu and Event Listener Class and objects --> needs libraries --> widgets, oled, joystick

class Event_listener:

    @abstractmethod
    def button_event(self,data):
        #the function on a button press
        pass

class Menu(Event_listener):
    current_menu = None
    current_widget = None

    def __init__(self, widgets, skeleton, start_pos = 0):
        # a list of all the widget objects to be printed on that menu
        self.widgets = widgets
        # the function to be used to generate the background of the menu
        self.skeleton = skeleton
        # which widget in the widget list the menu defaults the selection to when entered
        self.start_pos = start_pos
        # flag that lets the menu know it is currently displayed (used for callbacks)
        self.is_current = False

    def enter(self):
        #make the old menu not current and make the new menu current
        if Menu.current_menu != None: Menu.current_menu.is_current = False
        Menu.current_menu = self
        self.is_current = True
        #print skeleton and widgets
        self.skeleton()
        for obj in self.widgets:
            obj.print_w()
        #set the outline of the starting widget
        Menu.current_widget = self.widgets[self.start_pos]
        Menu.current_widget.outline_w()

    def button_event(self,direction):
        #check if it is the active menu or not
        if not self.is_current: return False
        #check if it is a click from the joystick
        if direction == 4: 
            Menu.current_widget.click_w()
            return True
        #check if it is a brwose widget that needs to be updated
        if Menu.current_widget.__class__.__name__ == 'Browse_widget':
            if Menu.current_widget.currently_edited: 
                Menu.current_widget.update_w(direction)
                return True
        #move to the correct position
        if Menu.current_widget.navigation[direction] == None: pass
        else:
            Menu.current_widget.outline_w(True)
            Menu.current_widget = Menu.current_widget.navigation[direction]
            Menu.current_widget.outline_w()
        return True
        

### Menu skeletons Set-up ###

def main_menu_skeleton():
    oled.fill(0)
    oled.hline(0,15,128,1)
    oled.hline(0,48,128,1)
    oled.hline(15,63,112,1)
    oled.vline(29,0,15,1)
    oled.vline(78,0,15,1)
    for i in range(9):
        oled.vline(15+(i*14),49,15,1)
    for i in range(8):
        oled.rect(21+(i*14),54,3,4,1,True)
    oled.rect(103,21,2,23,1,True)

def edit_menu_skeleton():
    oled.rect(21,7,86,50,0,True)
    oled.rect(20,6,88,52,1)
    oled.rect(19,5,90,54,1)
    oled.vline(64,27,24,1)

def chord_menu_skeleton():
    oled.fill(0)
    oled.rect(0,15,128,30,1)
    oled.rect(0,44,128,20,1)
    oled.vline(43,16,29,1)
    oled.vline(86,16,29,1)
    
    WriteS.text('VOICE',4,16)
    WriteS.text('SHIFT',50,16)
    WriteS.text('SPRD.',92,16)
    WriteS.text('go to',4,47)
    WriteS.text('then',80,47)

def global_menu_skeleton():
    oled.fill(0)
    oled.rect(0,15,128,30,1)
    oled.rect(0,44,128,20,1)
    oled.vline(43,16,28,1)
    oled.vline(86,16,28,1)
    
    WriteS.text('GATE',7,16)
    WriteS.text('MODE',48,16)
    WriteS.text('SCALE',90,16)

def global_menu_2_skeleton():
    oled.fill(0)
    oled.rect(0,15,128,30,1)
    oled.rect(0,44,128,20,1)
    oled.vline(43,16,28,1)
    oled.vline(86,16,47,1)
    oled.hline(63,36,4,1)
    
    WriteS.text('VIEW',8,16)
    WriteS.text('JUMP',50,16)
    WriteS.text('BRITE.',91,16)
    WriteS.text('scale root-',4,47)

def calibration_menu_skeleton():
    oled.fill(0)
    oled.rect(0,15,128,30,1)
    oled.vline(43,16,28,1)
    oled.vline(86,16,28,1)
    
    oled.rect(0,0,26,16,1)
    oled.hline(3,15,3,0)
    oled.hline(9,15,3,0)
    oled.hline(15,15,3,0)
    oled.hline(21,15,3,0)

    WriteS.text('out',4,0)
    WriteS.text('v1.2',105,0)

### Menus ###

main_menu = Menu([edit_menu_widget,chord_menu_widget,global_menu_widget,
                  root_widget,third_widget,seventh_widget,color_1_widget,color_2_widget,over_widget,
                  page_widget,Cell_widget.cells[0],Cell_widget.cells[1],Cell_widget.cells[2],Cell_widget.cells[3],Cell_widget.cells[4],Cell_widget.cells[5],Cell_widget.cells[6],Cell_widget.cells[7]],
                 main_menu_skeleton,3)

edit_menu = Menu([edit_menu_back_widget,
                  copy_widget,clear_widget,
                  paste_widget,clear_all_widget],
                  edit_menu_skeleton)

chord_menu = Menu([chord_menu_back_widget,chord_navigation_widget,chord_menu_clear_widget,
                   voicing_widget,shift_widget,spread_widget,
                   go_to_chord_widget,go_to_repeat_widget,go_to_then_widget],
                  chord_menu_skeleton)

global_menu = Menu([global_menu_back_widget,global_menu_to_2_widget,
                    gate_widget,mode_widget,scale_widget,
                    save_widget,Nav_widget.save_slots[0],Nav_widget.save_slots[1],Nav_widget.save_slots[2],Nav_widget.save_slots[3]],
                   global_menu_skeleton)

global_menu_2 = Menu([global_menu_2_back_widget,global_menu_to_1_widget,
                      sequence_view_widget,jump_min_widget,jump_max_widget,brightness_widget,
                      scale_root_widget,calibration_widget],
                     global_menu_2_skeleton)

calibration_menu = Menu([calibration_cancel_widget,
                         calibration_channel_widget,calibration_vout_widget,calibration_offset_widget,
                         calibration_save_widget],
                        calibration_menu_skeleton)

### navigation widget menu allocation ###

edit_menu_widget.set_destination_menu(edit_menu)
global_menu_widget.set_destination_menu(global_menu)
chord_menu_widget.set_destination_menu(chord_menu)

for obj in edit_menu.widgets:
    obj.set_destination_menu(main_menu)

global_menu_back_widget.set_destination_menu(main_menu)
for obj in Nav_widget.save_slots:
    obj.set_destination_menu(main_menu)
global_menu_to_2_widget.set_destination_menu(global_menu_2)

global_menu_2_back_widget.set_destination_menu(main_menu)
global_menu_to_1_widget.set_destination_menu(global_menu)
calibration_widget.set_destination_menu(calibration_menu)

chord_menu_back_widget.set_destination_menu(main_menu)
chord_menu_clear_widget.set_destination_menu(chord_menu)

calibration_cancel_widget.set_destination_menu(global_menu_2)
calibration_save_widget.set_destination_menu(global_menu_2)

### registering all the callbacks ###

J_center_irq.register([main_menu,edit_menu,chord_menu,global_menu,global_menu_2,calibration_menu])
J_up_irq.register([main_menu,edit_menu,chord_menu,global_menu,global_menu_2,calibration_menu])
J_down_irq.register([main_menu,edit_menu,chord_menu,global_menu,global_menu_2,calibration_menu])
J_left_irq.register([main_menu,edit_menu,chord_menu,global_menu,global_menu_2,calibration_menu])
J_right_irq.register([main_menu,edit_menu,chord_menu,global_menu,global_menu_2,calibration_menu])

################################################################################################################################################################
### launching the app ###
main_menu.enter()