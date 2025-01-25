### NOH-modular Pianist firmware v1.2 - licensed under a CC-BY-NC-SA 4.0 license - https://creativecommons.org/licenses/by-nc-sa/4.0/
#Library Imports

from machine import Pin, PWM, I2C, Timer
from oled import Write, GFX
from oled.fonts import ubuntu_12, ubuntu_20
from math import ceil
from random import getrandbits, randint
import framebuf, ad5593_edited, rp2, ssd1306, gc


################################################################################################################################################################
### Screen Set-up and Functions ###

W = 128
H = 64
i2c = I2C(1,scl=Pin(3),sda=Pin(2),freq=400000)
oled = ssd1306.SSD1306_I2C(W,H,i2c)
draw = GFX(W,H,oled.pixel)
WriteS = Write(oled, ubuntu_12)
WriteL = Write(oled, ubuntu_20)
WriteF = oled


### DAC Set-up and Functions ###


i2c = I2C(0,scl=Pin(5),sda=Pin(4),freq=400000)
DAC = ad5593_edited.AD5593(i2c, 0x11)
DAC.SetAllDAC()
DAC.SetIntRef(1)
DAC.SetDACRefGain(2)
DAC.SetLDAC(0)


### Pi Pico Pin Set-up ####


Center = Pin(18, Pin.IN, Pin.PULL_UP)
Up = Pin(0, Pin.IN, Pin.PULL_UP)
Down = Pin(26, Pin.IN, Pin.PULL_UP)
Left = Pin(19, Pin.IN, Pin.PULL_UP)
Right = Pin(1, Pin.IN, Pin.PULL_UP)
red = Pin(21, Pin.OUT)
green = Pin(20, Pin.OUT)
blue =  Pin(22, Pin.OUT)
PSLED = Pin(11, Pin.OUT)
TRIGIN = Pin(17, Pin.IN, Pin.PULL_DOWN)
PSIN = Pin(16, Pin.IN, Pin.PULL_DOWN)
CLKIN = Pin(15, Pin.IN)


################################################################################################################################################################
### Screen Menu Text Arrays -- Global Variables, Counters, and Timers  ###


time_buf = Timer()             #creates a timer do substitute the "sleep" function
tb_flag = True                 #the time buffer flag == on when the timer == complete

screen_saver_timer = Timer()   # a one minute timer that increments the count, screen saver at threshold
screen_saver_count = 0
screen_saver_threshold = 3
screen_saver_interval = 120000  # 120 seconds / 2 minutes
screen_saver_flag = False

Selection_Timer = Timer()
Selection_Blink_Flag = False   #for the blinking function to indicate an item == being edited

fast_paste_flag = False
fast_paste_counter = 0

select_flag = False            #the select flag shows where the user wants to change an object or just hover over it
edit_menu_flag = False
options_menu_flag = False
options_menu_2_flag = False
calibration_menu_flag = False
chord_menu_flag = False
ps_menu_flag = False
PS_CV_ready_flag = False
EDIT_CV_ready_flag = False

CLOCK_flag = False

TRIG_flag = False
freeze_flag = False
random_flag = False
shift_trig_flag = False
spread_trig_flag = False


### CV and DAC --- Arrays, Counters,Variables ###


Octave = 12

NOTES = [0,71,140,209,278,347,416,485,554,623,692,762,
         830,899,969,1038,1107,1176,1244,1313,1382,1451,1520,1589,
         1658,1727,1796,1865,1934,2003,2072,2141,2210,2279,2348,2417,
         2487,2555,2625,2693,2763,2832,2901,2970,3039,3108,3177,3246,
         3316,3385,3454,3523,3593,3662,3731,3800,3869,3938,4007,4076]

VOCT_buffer = [0,0,0,0,0,0,0,0]

### X and Y coordinates ###


Horizontal_Pos = [0,0,0]
Vertical_Pos = 1

Edit_Horizontal = False
Edit_Vertical = 0

Options_Horizontal = 0
Options_Vertical = 0

Options_2_Horizontal = 0
Options_2_Vertical = 0

Calibration_Horizontal = 0
Calibration_Vertical = 0

Chord_Horizontal = 0
Chord_Vertical = 0


### storing the select rectangles positions for each menu ###


SR = [[[0,50,14,14],[18,51,9,10],[32,51,9,10],[46,51,9,10],[60,51,9,10],
       [74,51,9,10],[88,51,9,10],[102,51,9,10],[116,51,9,10]],
      
      [[0,20,30,24],[30,20,20,24],[50,20,17,24],[67,17,35,16],[67,32,35,15],[106,20,22,24]],
      
      [[0,0,28,14],[31,0,46,14],[80,0,48,14]]]

Edit_SR = [[[27,38,33,15],[69,38,33,14]],
      
      [[28,25,32,14],[69,25,31,14]],
      
      [[48,10,33,14]]]

Options_SR_1 = [[[2,46,34,16],[46,46,20,16],[66,46,20,16],[86,46,20,16],[106,46,20,16]],
      
      [[2,29,40,14],[45,29,40,14],[88,29,38,14]],
           
      [[43,0,44,14],[86,0,42,14]]]

Options_SR_2 = [[[60,46,25,16],[88,46,38,16]],
      
      [[2,29,40,14],[45,29,16,14],[69,29,16,14],[88,29,38,14]],
           
      [[0,0,44,14],[43,0,44,14]]]

Calibration_SR = [[[22,46,83,16]],
      
      [[2,17,40,26],[45,17,40,26],[88,17,38,26]],
           
      [[39,0,53,14]]]

Chord_SR = [[[35,46,20,16],[55,46,22,16],[106,46,20,16]],
      
      [[2,29,40,14],[45,29,40,14],[88,29,38,14]],
           
      [[0,0,44,14],[43,0,44,14],[86,0,42,14]]]


### text and stored counters to recall each step on the main menu ###


Root = ['   A','Bb ','   B ','   C ','Db','   D','  Eb','   E ','   F ','Gb ','   G ','Ab ']
Root_Counter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]        #for the 32 different steps
Active_Chord = 0                                        #this points to the chord currently on screen
Next_Active_Chord = 0
Next_Next_Active_Chord = 0

Third = [' _ ','M', '+ ','- ','o ','o ']
Third_Counter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]       #same principle

Scale_Check = [True,False,True,False,True,True,False,True,False,True,False,True]
Scale_Shift = [0,0,9,2,4,5,7,11]
Scale_Quality = [1,0,3,0,3,1,0,0,0,3,0,5]

Seventh = ['_ ','7']
Seventh_Counter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

Color = [' ','sus2   ','sus4   ','b5    ','#5    ','b6    ','add6  ','min7   ','maj7  ','oct.   ','b9    ','add9 ','#9      ','b11    ','add11','#11    ']
Color_Counter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
Color_2_Counter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]     # the two color slots use the same text array
C1R_Counter = 0
C2R_Counter = 0

Copy_Buffer = [0,0,0,0,0,0,0,0,0]                             # used to store each chord components (root, third, fifth,...)

Over = [' ','A   ','Bb','B   ','C   ','Db','D   ','Eb ',' E  ',' F  ','Gb',' G  ','Ab']
Over_Counter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

Page = 0                                                #for N Pages of 8 steps
steps = 32                                              #Used to set the number of Pages, HAS TO BE A MULTIPLE OF 8

VOCT_STORAGE = [[0 for i in range(8)] for j in range(steps)]
repeat_finish_flag = [False]*steps

### Options Menu Variables and counters ###


Input = [' reset  ','randm','  shift  ','spread','freeze ',' jump ']
Input_Counter = 0

Mode = ['normal',' chord ',' plaits ',' organ  ']
Mode_Counter = 0

Sequence_Speed = ['  none  ','normal']
Sequence_Speed_Counter = True

Scale  = ['free ','maj ','min ','dor.','phr.','lyd. ','myx','locr. ']
Scale_Counter = 0

SaveLoad = ['save   -','load   -']
SaveLoad_flag = True

Contrast = ['low ','med',' full ']
Contrast_Counter = 2

Page_Select_Counter = [0,0]

Scale_Root_Counter = 0

### calibration menu variables and counter ###

Channel_Counter = 0

Vout_Counter = 1

Calibration_offset = [0,0,0,0,0,0,0,0]

CO_buffer = [0,0,0,0,0,0,0,0]

### Chord Menu Variables and counters ###


voicing_flag = [True]*steps

Shift = ['   -   ',' + 1 ',' + 2 ',' + 3 ',' + 4 ',' + 5 ',' + 6 ',' + 7 ',' + 8 ',' + 9 ',' +10 ',
         '  -10 ','  - 9 ','  - 8 ','  - 7 ','  - 6 ','  - 5 ','  - 4 ','  - 3 ','  - 2 ','  - 1 ']
Shift_Counter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

Spread = ['   -   ',' + 1 ',' + 2 ',' + 3 ',' + 4 ',' + 5 ',' + 6 ',' + 7 ',' + 8 ',' + 9 ',' +10 ']
Spread_Counter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

Goto = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

GotoRepeat = ['  -    ','x 1  ','x 2  ','x 3  ','x 4  ','x 5  ','x 6  ','x 7  ','x 8  ','x 9  ','x10','x11','x12','x13','x14','x15']
GotoRepeat_Counter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
Sequence_Repeat_Counter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

GotoThen = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,0]


################################################################################################################################################################
### CORE --SCREEN-- FUNCTIONS ###
  
 
def screen_saver_increment(source):
    global screen_saver_count, screen_saver_threshold
    global screen_saver_flag, select_flag, ps_menu_flag
    
    screen_saver_count = screen_saver_count+1
    if screen_saver_count == screen_saver_threshold:
        if ps_menu_flag:
            Display_Sequence_Back()
            screen_saver_count = 0
        else:
            screen_saver_flag = True
            screen_saver_count = 0
            Selection_Timer.deinit()
            select_flag = False
            rgb_off()
            oled.fill(0)
            screen_saver_timer.deinit()
            oled.show()
    else:
        pass

def tb_flag_on(Source):                                                         #to reset the time buffer (means 200ms elapsed)
    global tb_flag
    
    tb_flag = 1

def tb_trigger(a):                                                              #triggers the counter
    global tb_flag, time_buf, fast_paste_flag,fast_paste_counter
    
    if a:
        fast_paste_flag = False
        fast_paste_counter = 0
    else:
        pass
    
    tb_flag = 0
    time_buf.init(mode = Timer.ONE_SHOT, period = 250, callback = tb_flag_on)
    
def FastPaste(Source=0):
    global fast_paste_flag,Active_Chord,Goto,GotoThen,Calibration_offset,Channel_Counter
    
    if fast_paste_flag and not Center.value():
        if Source == 0: #chord copy
            PasteActiveChord()
            RefreshActiveChord()
        elif Source == 1: #goto set
            Goto[Active_Chord] = Active_Chord+1
            PrintGoto()
        elif Source == 2: #then set
            GotoThen[Active_Chord] = 0
            PrintGotoThen()
        elif Source == 3: #calibration offset
            for i in range(8):
                Calibration_offset[i] = Calibration_offset[Channel_Counter]
        else:
            pass
    else:
        pass
    oled.show()
    fast_paste_flag = False
    
def Write_Selection(value=1):
    global Horizontal_Pos, Vertical_Pos, SR, edit_menu_flag, options_menu_flag
    global Edit_SR, Options_SR_1, Edit_Horizontal, Edit_Vertical, Options_Horizontal, Options_Vertical
    global Options_2_Horizontal, Options_2_Vertical, options_menu_2_flag, chord_menu_flag, Chord_Horizontal
    global Chord_Vertical, Chord_SR, calibration_menu_flag, Calibration_SR, Calibration_Horizontal, Calibration_Vertical
    
    if edit_menu_flag:
        oled.rect(Edit_SR[Edit_Vertical][Edit_Horizontal][0],
                  Edit_SR[Edit_Vertical][Edit_Horizontal][1],
                  Edit_SR[Edit_Vertical][Edit_Horizontal][2],
                  Edit_SR[Edit_Vertical][Edit_Horizontal][3],value)
    elif options_menu_flag:
        oled.rect(Options_SR_1[Options_Vertical][Options_Horizontal][0],
                  Options_SR_1[Options_Vertical][Options_Horizontal][1],
                  Options_SR_1[Options_Vertical][Options_Horizontal][2],
                  Options_SR_1[Options_Vertical][Options_Horizontal][3],value)
    elif options_menu_2_flag:
        oled.rect(Options_SR_2[Options_2_Vertical][Options_2_Horizontal][0],
                  Options_SR_2[Options_2_Vertical][Options_2_Horizontal][1],
                  Options_SR_2[Options_2_Vertical][Options_2_Horizontal][2],
                  Options_SR_2[Options_2_Vertical][Options_2_Horizontal][3],value)
    elif calibration_menu_flag:
        oled.rect(Calibration_SR[Calibration_Vertical][Calibration_Horizontal][0],
                  Calibration_SR[Calibration_Vertical][Calibration_Horizontal][1],
                  Calibration_SR[Calibration_Vertical][Calibration_Horizontal][2],
                  Calibration_SR[Calibration_Vertical][Calibration_Horizontal][3],value)
    elif chord_menu_flag:
        oled.rect(Chord_SR[Chord_Vertical][Chord_Horizontal][0],
                  Chord_SR[Chord_Vertical][Chord_Horizontal][1],
                  Chord_SR[Chord_Vertical][Chord_Horizontal][2],
                  Chord_SR[Chord_Vertical][Chord_Horizontal][3],value)
    else:
        oled.rect(SR[Vertical_Pos][Horizontal_Pos[Vertical_Pos]][0],
                  SR[Vertical_Pos][Horizontal_Pos[Vertical_Pos]][1],
                  SR[Vertical_Pos][Horizontal_Pos[Vertical_Pos]][2],
                  SR[Vertical_Pos][Horizontal_Pos[Vertical_Pos]][3],value)
    
def RefreshActiveChord():
    PrintRoot()
    PrintThird()
    PrintSeventh()
    PrintColor()
    PrintColor2()
    PrintOver()
    
def UpdateNextChordPLAYSTOP(): #refresh seq
    global Root_Counter, Root, Next_Active_Chord
    global Third_Counter, Third, Active_Chord
    global Seventh_Counter, Seventh, Active_Chord
    global Color_2_Counter, Color_Counter, Color, Active_Chord
    global Over_Counter, Over, Active_Chord, Root_Sequence
    
    oled.rect(1,1,100,25,0,True)
    oled.rect(110,1,15,25,0,True)
    if Third_Counter[Active_Chord] == 5:
        WriteF.text(Third[Third_Counter[Active_Chord]].replace(' ',''),25,12)
        oled.line(25,19,31,13,1)
    elif Third_Counter[Active_Chord] != 0:
        WriteF.text(Third[Third_Counter[Active_Chord]].replace(' ',''),25,12)
    else:
        pass
    if Third_Counter[Active_Chord] == 0:
        WriteF.text(Root[Root_Counter[Active_Chord]].replace('  ',''),18,12)
    else:
        WriteF.text(Root[Root_Counter[Active_Chord]].replace('  ',''),5,12)
    if Seventh_Counter[Active_Chord] == 1:
        WriteF.text(Seventh[Seventh_Counter[Active_Chord]].replace('_','   '),38,12)
    else:
        pass
    WriteF.text(Color[Color_Counter[Active_Chord]].replace(' ',''),58,6)
    WriteF.text(Color[Color_2_Counter[Active_Chord]].replace(' ',''),58,17)
    WriteF.text(Over[Over_Counter[Active_Chord]].replace(' ',''),110,12)
    
def UpdateNextActiveDirection(): #refresh direction
    global Active_Chord, Goto, Sequence_Repeat_Counter, GotoThen, Over, Next_Active_Chord
    
    oled.rect(2,33,22,20,0,True)
    oled.rect(47,45,46,10,0,True)
    oled.rect(107,45,18,10,0,True)
    if Active_Chord < 9: #active chord number
        WriteF.text('{}'.format(Active_Chord+1),10,45)
    else:
        WriteF.text('{}'.format(Active_Chord+1),7,45)
        
    if (Goto[Active_Chord] == 0) or (Sequence_Repeat_Counter[Active_Chord] == 0): #where it goes
        WriteF.text('{}'.format(GotoThen[Active_Chord]+1),52,45)
    else:
        WriteF.text('{}'.format((Goto[Active_Chord])),52,45)
        WriteF.text('x{}'.format((Sequence_Repeat_Counter[Active_Chord])),74-(5*(Sequence_Repeat_Counter[Active_Chord]>9)),45)
        
    WriteF.text(Over[Root_Counter[Next_Active_Chord]+1],107,45) #the root of the next chord
    
def RefreshChordPage():
    PrintInvert()
    PrintShift()
    PrintSpread()
    PrintChordNumber()
    PrintGoto()
    PrintGotoRepeat()
    PrintGotoThen()
    PrintRootHelp()
    
def ClearAllChords():
    global Root_Counter, Third_Counter, Seventh_Counter, Color_Counter, Color_2_Counter, Over_Counter,steps
    global Shift_Counter, Spread_Counter, voicing_flag, Goto, GotoRepeat_Counter, GotoThen, Active_Chord
    
    for i in range(steps):
        Root_Counter[i] = 0
        Third_Counter[i] = 0
        Seventh_Counter[i] = 0
        Color_Counter[i] = 0
        Color_2_Counter[i] = 0
        Over_Counter[i] = 0
        voicing_flag[i] = True
        Shift_Counter[i] = 0
        Spread_Counter[i] = 0
        Goto[i] = 0
        GotoRepeat_Counter[i] = 0
        GotoThen[i] = ((i+1)%(steps))  
    RefreshVOCTSTORAGE()
    
def ClearActiveChord():
    global Root_Counter, Third_Counter, Seventh_Counter,Color_Counter, Color_2_Counter, Over_Counter
    global Shift_Counter, Spread_Counter, voicing_flag,Goto, GotoRepeat_Counter, GotoThen, Active_Chord, steps
    
    Root_Counter[Active_Chord] = 0
    Third_Counter[Active_Chord] = 0
    Seventh_Counter[Active_Chord] = 0
    Color_Counter[Active_Chord] = 0
    Color_2_Counter[Active_Chord] = 0
    Over_Counter[Active_Chord] = 0
    voicing_flag[Active_Chord] = True
    Shift_Counter[Active_Chord] = 0
    Spread_Counter[Active_Chord] = 0
    Goto[Active_Chord] = 0
    GotoRepeat_Counter[Active_Chord] = 0
    GotoThen[Active_Chord] = ((Active_Chord+1)%(steps))
    
def CopyActiveChord():
    global Root_Counter,Third_Counter,Seventh_Counter,Color_Counter,Color_2_Counter,Over_Counter
    global Copy_Buffer,Active_Chord,voicing_flag,Shift_Counter,Spread_Counter
    
    Copy_Buffer[0] = Root_Counter[Active_Chord]
    Copy_Buffer[1] = Third_Counter[Active_Chord]
    Copy_Buffer[2] = Seventh_Counter[Active_Chord]
    Copy_Buffer[3] = Color_Counter[Active_Chord]
    Copy_Buffer[4] = Color_2_Counter[Active_Chord]
    Copy_Buffer[5] = Over_Counter[Active_Chord]
    Copy_Buffer[6] = voicing_flag[Active_Chord]
    Copy_Buffer[7] = Shift_Counter[Active_Chord]
    Copy_Buffer[8] = Spread_Counter[Active_Chord]
    
def PasteActiveChord():
    global Root_Counter, Third_Counter, Seventh_Counter,Color_Counter, Color_2_Counter, Over_Counter
    global Copy_Buffer, Active_Chord, voicing_flag, Shift_Counter, Spread_Counter
    
    Root_Counter[Active_Chord] = Copy_Buffer[0]
    Third_Counter[Active_Chord] = Copy_Buffer[1]
    Seventh_Counter[Active_Chord] = Copy_Buffer[2]
    Color_Counter[Active_Chord] = Copy_Buffer[3]
    Color_2_Counter[Active_Chord] = Copy_Buffer[4]
    Over_Counter[Active_Chord] = Copy_Buffer[5]
    voicing_flag[Active_Chord] = Copy_Buffer[6]
    Shift_Counter[Active_Chord] = Copy_Buffer[7]
    Spread_Counter[Active_Chord] = Copy_Buffer[8]
    if not(Scale_Counter):
        pass
    else:
        Update_Scaled_Root()

def Reset_Screen_Saver_Count(): #refresh screen after screen saver
    global screen_saver_count,CO_buffer,screen_saver_flag, Calibration_offset,Page, Active_Chord
    
    screen_saver_count = 0
    if not screen_saver_flag:
        pass
    else:
        screen_saver_timer.init(mode = Timer.PERIODIC, period = screen_saver_interval, callback = screen_saver_increment)
        screen_saver_flag = False
        ResetFlags()
        rgb_off()
        Calibration_offset = CO_buffer
        Active_Chord = 0
        Page = ceil((Active_Chord+1)/8)-1
        MainMenu()
        

def ResetPosition():
    global Edit_Horizontal, Edit_Vertical, Horizontal_Pos,Calibration_Vertical
    global Vertical_Pos, Options_Horizontal, Options_Vertical,Calibration_Horizontal
    global Chord_Horizontal, Chord_Vertical, Options_2_Horizontal, Options_2_Vertical
    
    Vertical_Pos = 1
    Horizontal_Pos[Vertical_Pos] = 0
    Edit_Vertical = 2
    Edit_Horizontal = False
    Options_Vertical = 2
    Options_Horizontal = 0
    Horizontal_Pos[2] = 0
    Chord_Vertical = 2
    Chord_Horizontal = 0
    Options_2_Horizontal = 0
    Options_2_Vertical = 2
    Calibration_Horizontal = 0
    Calibration_Vertical = 2
    
def ResetChordPage():
    global Active_Chord, voicing_flag, Shift_Counter,Spread_Counter, Goto, GotoRepeat_Counter
    global GotoThen, steps
    
    voicing_flag[Active_Chord] = True
    Shift_Counter[Active_Chord] = 0
    Spread_Counter[Active_Chord] = 0
    Goto[Active_Chord] = 0
    GotoRepeat_Counter[Active_Chord] = 0
    GotoThen[Active_Chord] = (Active_Chord+1)%steps
    
def ResetSequenceRepeats(): 
    global Sequence_Repeat_Counter,GotoRepeat_Counter, steps
    
    for i in range(steps):
        Sequence_Repeat_Counter[i] = GotoRepeat_Counter[i]
    
def ResetFlags():
    global edit_menu_flag, options_menu_flag,chord_menu_flag, ps_menu_flag,CLOCK_flag, TRIG_flag
    global EDIT_CV_ready_flag, freeze_flag, random_flag
    global shift_trig_flag, spread_trig_flag, options_menu_2_flag,calibration_menu_flag,SaveLoad_flag
    
    edit_menu_flag = False
    options_menu_flag = False
    options_menu_2_flag = False
    calibration_menu_flag = False
    chord_menu_flag = False
    ps_menu_flag = False
    CLOCK_flag = False
    TRIG_flag = False
    EDIT_CV_ready_flag = False
    freeze_flag = False
    random_flag = False
    shift_trig_flag = False
    spread_trig_flag = False
    SaveLoad_flag = True
    
def Selection_Toggle_Main():
    global select_flag, Horizontal_Pos, Vertical_Pos, Active_Chord,edit_menu_flag, options_menu_flag, Selection_Timer
    global fast_paste_flag,Page, chord_menu_flag,EDIT_CV_ready_flag,fast_paste_counter
    
    if select_flag and (Vertical_Pos == 0) and (Horizontal_Pos[Vertical_Pos] > 0):                     #on a sequence dot item
        if (not fast_paste_flag) and ((Active_Chord+1) != (Horizontal_Pos[Vertical_Pos]+(8*Page))):    #not the same dot as the one already selected
            fast_paste_flag = True
            RemoveSelectedChord()
            Active_Chord = (8*(Page))+(Horizontal_Pos[Vertical_Pos]-1)
            RefreshActiveChord()
            PrintSelectedChord()
            select_flag = not select_flag
        else:
            select_flag = not select_flag
            fast_paste_counter += 1
            if fast_paste_counter == 5:
                FastPaste()
                fast_paste_counter = 0
            
        EDIT_CV_ready_flag = False
        
    elif select_flag and (Vertical_Pos == 2) and (Horizontal_Pos[Vertical_Pos] == 0): #on the "edit" item
        edit_menu_flag = True
        select_flag = not select_flag
        EditMenu()
    
    elif select_flag and (Vertical_Pos == 2) and (Horizontal_Pos[Vertical_Pos] == 1): #on the "CHORD" item
        chord_menu_flag = True
        select_flag = not select_flag
        ChordMenu()
    
    elif select_flag and (Vertical_Pos == 2) and (Horizontal_Pos[Vertical_Pos] == 2): #on the "menu" item
        options_menu_flag = True
        select_flag = not select_flag
        OptionsMenu1()
        
    elif select_flag:
        Write_Selection(0)
        Selection_Timer.init(mode = Timer.PERIODIC, period = 300, callback = Selection_Blink)
        
    else:
        Selection_Timer.deinit()
        EDIT_CV_ready_flag = False
        Write_Selection()
        
def Selection_Toggle_Edit():
    global select_flag, Edit_Horizontal, Edit_Vertical,edit_menu_flag
    
    Write_Selection()
    
    if select_flag and Edit_Vertical == 2:       #on 'Back'
        edit_menu_flag = False
        select_flag = not select_flag
        MainMenu()
        
    elif select_flag and Edit_Vertical == 1:     # on 'Copy'
        if not Edit_Horizontal:
            CopyActiveChord()
            edit_menu_flag = False
            select_flag = not select_flag
            MainMenu()
        else:                                    # on 'Clear'
            ClearActiveChord()
            edit_menu_flag = False
            select_flag = not select_flag
            MainMenu()
            
    elif select_flag and Edit_Vertical == 0:     # on 'Paste'
        if not Edit_Horizontal:
            PasteActiveChord()
            edit_menu_flag = False
            select_flag = not select_flag
            MainMenu()
        else:                                    # on 'Cl. All'
            ClearAllChords()
            edit_menu_flag = False
            select_flag = not select_flag
            MainMenu()
    else:
        pass

def ManageSaveLoad(slot):
    global Page, select_flag, options_menu_flag, Active_Chord, SaveLoad_flag
    
    screen_saver_timer.deinit()
    
    if SaveLoad_flag:
        LoadScene(slot)
        RefreshVOCTSTORAGE()
        EDIT_CV_ready_flag = False
    else:
        SaveScene(slot)
    
    screen_saver_timer.init(mode = Timer.PERIODIC, period = screen_saver_interval, callback = screen_saver_increment)
    options_menu_flag = False
    SaveLoad_flag = True
    select_flag = not select_flag
    Page = ceil((Active_Chord+1)/8)-1
    rgb_off()
    MainMenu()

def Selection_Toggle_Options():
    global select_flag, Options_Horizontal,Options_Vertical,options_menu_2_flag,options_menu_flag,Page,SaveLoad_flag
    
    Write_Selection()
    
    if select_flag and Options_Vertical == 2:
        if Options_Horizontal == 0:     #on 'Back'
            options_menu_flag = False
            SaveLoad_flag = True
            select_flag = not select_flag
            Page = ceil((Active_Chord+1)/8)-1
            rgb_off()
            RefreshVOCTSTORAGE()
            MainMenu()
        else: # on '>>>'
            options_menu_flag = False
            select_flag = not select_flag
            rgb_off()
            options_menu_2_flag = True
            OptionsMenu2()
            
        
    elif select_flag and (Options_Vertical == 0) and (Options_Horizontal > 0): #on save/load slots
        if Options_Horizontal == 1:    #on slot 1
            ManageSaveLoad(1)
            
        elif Options_Horizontal == 2: #on slot 2
            ManageSaveLoad(2)
            
        elif Options_Horizontal == 3: #on slot 3
            ManageSaveLoad(3)
            
        else: #on load 4
            ManageSaveLoad(4)
    
    elif select_flag:
        Write_Selection(0)
        Selection_Timer.init(mode = Timer.PERIODIC, period = 300, callback = Selection_Blink)
        
    else:
        Selection_Timer.deinit()
        Write_Selection()
        
def Selection_Toggle_Options_2(): #options 2 toggle
    global select_flag, Options_2_Horizontal, Options_2_Vertical, options_menu_2_flag, calibration_menu_flag
    global options_menu_flag, Page,Vout_Counter,Calibration_Vertical,SaveLoad_flag,Sequence_Speed_Counter
    
    Write_Selection()
    
    if select_flag and Options_2_Vertical == 2:
        if Options_2_Horizontal == 0:     #on '<<<'
            options_menu_2_flag = False
            select_flag = not select_flag
            options_menu_flag = True
            OptionsMenu1()
        else: # on 'back'
            options_menu_2_flag = False
            SaveLoad_flag = True
            select_flag = not select_flag
            Page = ceil((Active_Chord+1)/8)-1
            MainMenu()
        
    elif select_flag and (Options_2_Vertical == 1) and (Options_2_Horizontal == 0): # on speed flag
        Sequence_Speed_Counter = not Sequence_Speed_Counter
        select_flag = not select_flag
        PrintSequenceSpeed()
        Write_Selection()
    
    elif select_flag and (Options_2_Vertical == 0) and (Options_2_Horizontal == 1): #on 'calibration'
        options_menu_2_flag = False
        select_flag = not select_flag
        calibration_menu_flag = True
        Vout_Counter = 1
        Calibration_Vertical = 2
        Update_Calibration_Out(Vout_Counter)
        CalibrationMenu()
    
    elif select_flag:
        Write_Selection(0)
        Selection_Timer.init(mode = Timer.PERIODIC, period = 300, callback = Selection_Blink)
        
    else:
        Selection_Timer.deinit()
        Write_Selection()
        
def Selection_Toggle_Calibration():
    global select_flag, Calibration_Vertical, CO_buffer,calibration_menu_flag, EDIT_CV_ready_flag, options_menu_2_flag
    global Calibration_offset,Calibration_Horizontal,fast_paste_counter,fast_paste_flag
    
    Write_Selection()
    
    if select_flag and Calibration_Vertical == 2: # on 'cancel'
        calibration_menu_flag = False
        select_flag = not select_flag
        options_menu_2_flag = True
        Calibration_offset = CO_buffer
        EDIT_CV_ready_flag = False
        OptionsMenu2()
        
    elif select_flag and Calibration_Vertical == 0: #on 'save & exit'
        select_flag = not select_flag
        SaveCalibrationSettings()
        calibration_menu_flag = False
        options_menu_2_flag = True
        EDIT_CV_ready_flag = False
        OptionsMenu2()
    
    elif select_flag:
        if (Calibration_Vertical == 1) and (Calibration_Horizontal == 2): #on the offset
            fast_paste_counter += 1
            if fast_paste_counter == 5:
                fast_paste_flag = True
                FastPaste(3)
                fast_paste_counter = 0
            else:
                pass
        Write_Selection(0)
        Selection_Timer.init(mode = Timer.PERIODIC, period = 300, callback = Selection_Blink)
        
    else:
        Selection_Timer.deinit()
        Write_Selection()
        
def Selection_Toggle_Chord():
    global select_flag, Chord_Horizontal, Chord_Vertical,chord_menu_flag, voicing_flag, Active_Chord
    global Page, EDIT_CV_ready_flag, fast_paste_counter, fast_paste_flag
    
    Write_Selection()
    
    if select_flag and (Chord_Vertical == 2) and (Chord_Horizontal == 2): #on 'clear'
        select_flag = not select_flag
        EDIT_CV_ready_flag = False
        ResetChordPage()
        RefreshChordPage()
        Write_Selection()    
        
    elif select_flag and (Chord_Vertical == 2) and (Chord_Horizontal == 0): #on 'Back'           
        chord_menu_flag = False
        select_flag = not select_flag
        Page = ceil((Active_Chord+1)/8)-1
        MainMenu()
        
    elif select_flag and (Chord_Vertical == 1) and (Chord_Horizontal == 0): #on the invert toggle
        voicing_flag[Active_Chord] = not voicing_flag[Active_Chord]         
        select_flag = not select_flag
        EDIT_CV_ready_flag = False
        PrintInvert()
        Write_Selection()
        
    elif select_flag:
        if (Chord_Vertical == 0) and (Chord_Horizontal == 0): #on go to
            fast_paste_counter += 1
            if fast_paste_counter == 3:
                fast_paste_flag = True
                FastPaste(1)
                fast_paste_counter = 0
            else:
                pass
        if (Chord_Vertical == 0) and (Chord_Horizontal == 2): #on then
            fast_paste_counter += 1
            if fast_paste_counter == 3:
                fast_paste_flag = True
                FastPaste(2)
                fast_paste_counter = 0
            else:
                pass
        Write_Selection(0)
        Selection_Timer.init(mode = Timer.PERIODIC, period = 300, callback = Selection_Blink)
        
    else:
        Selection_Timer.deinit()
        EDIT_CV_ready_flag = False
        Write_Selection()
    
def Selection_Blink(Source):
    global Selection_Blink_Flag
    
    Selection_Blink_Flag = not Selection_Blink_Flag
    if Selection_Blink_Flag:
        Write_Selection()
    else:
        Write_Selection(0)
    oled.show()
    
def PrintRoot(): #print stuff
    global Root_Counter, Root, Active_Chord
    
    if Root_Counter[Active_Chord]==6: #Eb
        WriteL.text(' Eb ',1,21)
    else:
        WriteL.text(Root[Root_Counter[Active_Chord]],3,21)
    
def PrintThird():
    global Third_Counter, Third, Active_Chord
    
    if Third_Counter[Active_Chord] == 5:
        WriteL.text(Third[Third_Counter[Active_Chord]],32,21)
        oled.line(32,38,42,28,1)
    elif Third_Counter[Active_Chord]==3:
        WriteL.text('m ',32,21)
    else:
        WriteL.text(Third[Third_Counter[Active_Chord]],32,21)
    
def PrintSeventh():
    global Seventh_Counter, Seventh, Active_Chord
    
    WriteL.text(Seventh[Seventh_Counter[Active_Chord]],52,21)
    
def PrintColor():
    global Color_Counter, Color, Active_Chord
    
    if Color_Counter[Active_Chord]==0:
        WriteS.text('    _    ',69,18)
    else:
        WriteS.text(Color[Color_Counter[Active_Chord]],69,18)
    
def PrintColor2():
    global Color_2_Counter, Color, Active_Chord
    
    if Color_2_Counter[Active_Chord]==0:
        WriteS.text('    _    ',69,32)
    else:
        WriteS.text(Color[Color_2_Counter[Active_Chord]],69,32) 
    
def PrintOver():
    global Over_Counter, Over, Active_Chord
    
    if Over_Counter[Active_Chord]==0:
        WriteS.text(' _   ',109,27)
    else:
        WriteS.text(Over[Over_Counter[Active_Chord]],109,27)
    
def PrintPage():
    global Page
    
    WriteS.text(str(int(Page+1)),4,50)
    
def PrintChordNumber():
    global Active_Chord
    
    oled.rect(71,0,18,14,0,True)
    
    if Active_Chord < 9:
        WriteS.text(str(Active_Chord+1),74,0)
    else:
        WriteS.text(str(Active_Chord+1),71,0)

def PrintInvert():
    global voicing_flag, Active_Chord
    
    if voicing_flag[Active_Chord]:
        WriteS.text('on ',15,29)
    else:
        WriteS.text('off',14,29)
        
def PrintInput():
    global Input, Input_Counter
    
    WriteS.text(Input[Input_Counter],6,29)
    
def PrintMode():
    global Mode, Mode_Counter
    
    WriteS.text(Mode[Mode_Counter],47,29)
    
def PrintSequenceSpeed(): # global sequence speed
    global Sequence_Speed, Sequence_Speed_Counter
    
    WriteS.text(Sequence_Speed[Sequence_Speed_Counter],4,29)
        
def PrintContrast():
    global Contrast,Contrast_Counter
    
    WriteS.text(Contrast[Contrast_Counter],96,29)
    
def PrintPageSelect():
    global Page_Select_Counter
    
    oled.fill_rect(45,29,40,15,0)
    WriteS.text(str(Page_Select_Counter[0]+1),50-(3*(Page_Select_Counter[0]>8)),29)
    WriteS.text(str(Page_Select_Counter[1]+1),74-(3*(Page_Select_Counter[1]>8)),29)
    oled.hline(63,36,4,1)
    
def PrintScaleRoot():
    global Root,Scale_Root_Counter
    
    oled.fill_rect(60,46,25,16,0)
    WriteS.text(Root[Scale_Root_Counter].replace(' ',''),64,47)
    
def PrintChannelSelect():
    global Channel_Counter
    
    WriteL.text(str(Channel_Counter+1),16,19)
    
def PrintChannelVout():
    global Vout_Counter
    
    oled.fill_rect(45,17,40,26,0)
    if Vout_Counter == 0:
        WriteS.text('0.25',48,26)
        WriteL.text('V',71,19)
    else:
        WriteL.text(str(Vout_Counter)+'V',54,19)
    
def PrintChannelOffset():
    global Channel_Counter, Calibration_offset
    
    oled.fill_rect(88,17,38,26,0)
    offset = Calibration_offset[Channel_Counter]
    if -10 < offset < 10:
        if offset >= 0:
            WriteL.text('+',94,19)
        else:
            WriteL.text('-',97,19)
        WriteL.text(str(abs(offset)),107,19)
    else:
        if offset >= 0:
            WriteL.text('+',89,19)
        else:
            WriteL.text('-',92,19)
        WriteL.text(str(abs(offset)),102,19)
    
def Update_All_Calibration():
    PrintChannelSelect()
    PrintChannelOffset()
    
def PrintSaveLoad():
    global SaveLoad_flag, SaveLoad
    
    WriteS.text(SaveLoad[SaveLoad_flag],8,47)
    
def PrintScale():
    global Scale, Scale_Counter
    
    WriteS.text(Scale[Scale_Counter],97,29)
    
def PrintRootHelp():
    global Active_Chord, Root_Counter, Over
    
    WriteS.text(Over[Root_Counter[Active_Chord]+1],47,0)
    oled.vline(65,4,7,1) #chord root/number seperation
    
def PrintShift():
    global Shift, Shift_Counter, Active_Chord
    
    WriteS.text(Shift[Shift_Counter[Active_Chord]],54,29)
    
def PrintSpread():
    global Spread, Spread_Counter, Active_Chord
    
    WriteS.text(Spread[Spread_Counter[Active_Chord]],97,29)
    
def PrintGoto():
    global Goto, Active_Chord
    
    oled.rect(38,46,16,16,0,True)
    
    if Goto[Active_Chord] == 0:
        WriteS.text(' - ',41,47)
    elif Goto[Active_Chord] < 10:
        WriteS.text(str(Goto[Active_Chord]),42,47)
    else:
        WriteS.text(str(Goto[Active_Chord]),39,47)
    
def PrintGotoRepeat():
    global GotoRepeat, GotoRepeat_Counter, Active_Chord
    
    WriteS.text(GotoRepeat[GotoRepeat_Counter[Active_Chord]],58,47)
    
def PrintGotoThen():
    global GotoThen, Active_Chord
    
    oled.rect(106,46,18,16,0,True)
    
    if GotoThen[Active_Chord] < 9:
        WriteS.text(str((GotoThen[Active_Chord])+1),113,47)
    else:
        WriteS.text(str((GotoThen[Active_Chord])+1),110,47)
    
    
def RemoveSelectedChord():
    global Vertical_Pos, Horizontal_Pos, Active_Chord
    
    oled.rect(19+((Active_Chord%8)*14),52,7,8,0,True)
    oled.rect(21+((Active_Chord%8)*14),54,3,4,1,True)
    
    
def PrintSelectedChord():
    global Vertical_Pos, Page, Active_Chord
    
    if (8*Page) <= (Active_Chord) <= 7+(8*Page): #checks the right Page == displayed before updating the dot
        oled.rect(19+((Active_Chord%8)*14),52,7,8,1,True)
        
    else:
        pass
    
def Root_Selector(up_down): #root select
    global Scale_Check,Active_Chord,Root_Counter,Root,Scale_Shift,Scale_Counter
    
    if up_down:
        Root_Counter[Active_Chord] = (Root_Counter[Active_Chord]+1)%len(Root)
        if Scale_Counter == 0:
            pass
        else:
            Update_Scaled_Root()
        
    else:
        Root_Counter[Active_Chord] = (Root_Counter[Active_Chord]-1)%len(Root)
        if Scale_Counter == 0:
            pass
        else:
            Update_Scaled_Root(True)
            
def Update_Scaled_Third():
    global Active_Chord,Root_Counter,Scale_Shift,Scale_Counter,Third_Counter,Scale_Quality,Scale_Root_Counter
    
    if Scale_Counter == 0:
        pass
    else:
        Third_Counter[Active_Chord] = Scale_Quality[(Root_Counter[Active_Chord]+Scale_Shift[Scale_Counter]-Scale_Root_Counter)%12]
        PrintThird()
        
def Update_All_Scaled_Third():
    global Root_Counter,Scale_Shift, Scale_Counter, Third_Counter,Scale_Quality,Scale_Root_Counter
    
    if Scale_Counter == 0:
        pass
    else:
        for i in range(32):
            Third_Counter[i] = Scale_Quality[(Root_Counter[i]+Scale_Shift[Scale_Counter]-Scale_Root_Counter)%12]

def Update_Scaled_Root(down_flg=False):
    global Scale_Check,Active_Chord,Root_Counter,Root,Scale_Shift,Scale_Counter,Scale_Root_Counter
    
    if Scale_Check[(Root_Counter[Active_Chord]+Scale_Shift[Scale_Counter]-Scale_Root_Counter)%12]:
        pass
    else:
        Root_Counter[Active_Chord] = (Root_Counter[Active_Chord]+(1-(2*down_flg)))%len(Root)
                
    Update_Scaled_Third()
                
def Update_All_Scaled_Root():
    global Scale_Check,Root_Counter,Root,Scale_Shift,Scale_Counter,steps,Scale_Root_Counter
    
    if Scale_Counter == 0:
        pass
    else:
        for i in range(steps):
            if Scale_Check[(Root_Counter[i]+Scale_Shift[Scale_Counter]-Scale_Root_Counter)%12]:
                pass
            else:
                Root_Counter[i] = (Root_Counter[i]+1)%len(Root)
                
def UpdateContrast():
    global Contrast_Counter
    
    if Contrast_Counter == 0:
        oled.contrast(10)
    elif Contrast_Counter == 1:
        oled.contrast(128)
    else:
        oled.contrast(255)
    
def Move_Up():
    global Vertical_Pos, edit_menu_flag, options_menu_flag,Edit_Vertical, Options_Vertical, Edit_Horizontal
    global Options_Horizontal, Horizontal_Pos,calibration_menu_flag,Calibration_Horizontal,Calibration_Vertical
    global chord_menu_flag, Chord_Vertical,options_menu_2_flag, Options_2_Horizontal, Options_2_Vertical
    
    Write_Selection(0)
    
    if edit_menu_flag:
        if Edit_Horizontal and (Edit_Vertical == 1):
            Edit_Horizontal = False
            Edit_Vertical = min(Edit_Vertical+1,2)
        else:
            Edit_Vertical = min(Edit_Vertical+1,2)
            
    elif options_menu_flag:
        if Options_Vertical == 1:
            Options_Horizontal = 0
        elif Options_Vertical == 0:
            Options_Horizontal = min(Options_Horizontal,2)
        else:
            pass
        Options_Vertical = min(Options_Vertical+1,2)
        
    elif options_menu_2_flag:
        if Options_2_Vertical == 1:
            Options_2_Horizontal = 1
        elif Options_2_Vertical == 0:
            Options_2_Horizontal += 2
        else:
            pass
        Options_2_Vertical = min(Options_2_Vertical+1,2)
    
    elif calibration_menu_flag:
        if Calibration_Vertical == 0:
            Calibration_Horizontal = 1
        elif Calibration_Vertical == 1:
            Calibration_Horizontal = 0
        else:
            pass
        Calibration_Vertical = min(Calibration_Vertical+1,2)
        
    elif chord_menu_flag:
        Chord_Vertical = min(Chord_Vertical+1,2)
        
    else:
        if Vertical_Pos and Horizontal_Pos[Vertical_Pos] == 4:
            Horizontal_Pos[Vertical_Pos] = Horizontal_Pos[Vertical_Pos]-1
            
        else:
            Vertical_Pos = min(Vertical_Pos+1,2)
    
    Write_Selection()
    
def Move_Down():
    global Vertical_Pos, edit_menu_flag, options_menu_flag,Calibration_Vertical,Options_2_Vertical
    global Edit_Vertical, Options_Vertical, Horizontal_Pos,calibration_menu_flag,Calibration_Horizontal
    global chord_menu_flag, Chord_Vertical,Options_Horizontal, options_menu_2_flag, Options_2_Horizontal
    
    Write_Selection(0)
    
    if edit_menu_flag:
        Edit_Vertical = max(Edit_Vertical-1,0)
        
    elif options_menu_flag:
        if Options_Vertical == 2:
            if Options_Horizontal == 1:
                Options_Horizontal = 2
            else:
                Options_Horizontal = 1
        else:
            pass
        Options_Vertical = max(Options_Vertical-1,0)
        
    elif options_menu_2_flag:
        if Options_2_Vertical == 1:
            Options_2_Horizontal = (Options_2_Horizontal==3)
        else:
            pass
        Options_2_Vertical = max(Options_2_Vertical-1,0)
    
    elif calibration_menu_flag:
        if Calibration_Vertical == 2:
            Calibration_Horizontal = 1
        elif Calibration_Vertical == 1:
            Calibration_Horizontal = 0
        else:
            pass
        Calibration_Vertical = max(Calibration_Vertical-1,0)
        
    elif chord_menu_flag:
        Chord_Vertical = max(Chord_Vertical-1,0)
        
    else:
        if Vertical_Pos and Horizontal_Pos[Vertical_Pos] == 3:
            Horizontal_Pos[Vertical_Pos] = Horizontal_Pos[Vertical_Pos]+1
            
        else:
            Vertical_Pos = max(Vertical_Pos-1,0)
        
    Write_Selection()
    
def Move_Left():
    global Vertical_Pos, Horizontal_Pos, edit_menu_flag, options_menu_flag
    global Edit_Horizontal, Options_Horizontal,chord_menu_flag, Chord_Horizontal, Scale_Counter
    global options_menu_2_flag, Options_2_Horizontal, Options_2_Vertical,calibration_menu_flag,Calibration_Horizontal
    
    Write_Selection(0)
    
    if edit_menu_flag:
        Edit_Horizontal = False
        
    elif options_menu_flag:
        Options_Horizontal = max(Options_Horizontal-1,0)
        
    elif options_menu_2_flag:
        Options_2_Horizontal = max(Options_2_Horizontal-1,0)
        
    elif calibration_menu_flag:
        Calibration_Horizontal = max(Calibration_Horizontal-1,0)
        
    elif chord_menu_flag:
        Chord_Horizontal = max(Chord_Horizontal-1,0)
        
    else:
        if Vertical_Pos and Horizontal_Pos[Vertical_Pos] >= 4:
            Horizontal_Pos[Vertical_Pos] = Horizontal_Pos[Vertical_Pos]-2
        elif (Vertical_Pos == 1) and (Horizontal_Pos[Vertical_Pos] == 2):
            if Scale_Counter == 0:
                Horizontal_Pos[Vertical_Pos] = Horizontal_Pos[Vertical_Pos]-1
            else:
                Horizontal_Pos[Vertical_Pos] = Horizontal_Pos[Vertical_Pos]-2
        
        else:
            Horizontal_Pos[Vertical_Pos] = max(Horizontal_Pos[Vertical_Pos]-1,0)
    
    Write_Selection()
    
def Move_Right():
    global Vertical_Pos, Horizontal_Pos, edit_menu_flag, options_menu_flag,Edit_Vertical, Options_Vertical
    global chord_menu_flag, Chord_Horizontal, Scale_Counter, Edit_Horizontal, Options_Horizontal,Calibration_Vertical
    global options_menu_2_flag, Options_2_Horizontal, Options_2_Vertical,calibration_menu_flag,Calibration_Horizontal
    
    Write_Selection(0)
    
    if edit_menu_flag:
        if Edit_Vertical == 2:
            pass
        else:
            Edit_Horizontal = True
            
    elif options_menu_flag:
        if Options_Vertical == 2:
            Options_Horizontal = min(Options_Horizontal+1,1)
        elif Options_Vertical == 1:
            Options_Horizontal = min(Options_Horizontal+1,2)
        else:
            Options_Horizontal = min(Options_Horizontal+1,4)
    
    elif options_menu_2_flag:
        if Options_2_Vertical == 1:
            Options_2_Horizontal = min(Options_2_Horizontal+1,3)
        else:
            Options_2_Horizontal = min(Options_2_Horizontal+1,1)
        
    elif calibration_menu_flag:
        if Calibration_Vertical == 1:
            Calibration_Horizontal = min(Calibration_Horizontal+1,2)
        else:
            pass
            
    elif chord_menu_flag:
        Chord_Horizontal = min(Chord_Horizontal+1,2)
            
    else:
        if Vertical_Pos == 0:
            Horizontal_Pos[Vertical_Pos] = min(Horizontal_Pos[Vertical_Pos]+1,8)
            
        elif Vertical_Pos == 1:
            if Horizontal_Pos[Vertical_Pos] == 0:
                if Scale_Counter == 0:
                    Horizontal_Pos[Vertical_Pos] = Horizontal_Pos[Vertical_Pos]+1
                else:
                    Horizontal_Pos[Vertical_Pos] = Horizontal_Pos[Vertical_Pos]+2
                    
            elif Horizontal_Pos[Vertical_Pos] == 3:
                Horizontal_Pos[Vertical_Pos] = Horizontal_Pos[Vertical_Pos]+2
            
            else:
                Horizontal_Pos[Vertical_Pos] = min(Horizontal_Pos[Vertical_Pos]+1,5)
            
        elif Vertical_Pos == 2:
            Horizontal_Pos[Vertical_Pos] = min(Horizontal_Pos[Vertical_Pos]+1,2)
            
        else:
            pass
    
    Write_Selection()
    
def Update_Up(): #update up
    global Vertical_Pos, Horizontal_Pos, Page, Active_Chord, steps, Third, Third_Counter
    global Over_Counter, Over, Seventh_Counter, Seventh, Color
    
    if Vertical_Pos == 0:
        if Horizontal_Pos[Vertical_Pos] == 0:
            Page = (Page+1)%int(steps/8)
            PrintPage()
            Write_Selection()
            if (Page*8) <= Active_Chord < ((Page*8)+8):
                PrintSelectedChord()
            else:
                RemoveSelectedChord()
        else:
            pass
        
    elif Vertical_Pos == 1:
        if Horizontal_Pos[Vertical_Pos] == 0:
            Root_Selector(True)
            PrintRoot()
            Write_Selection()
            
        elif Horizontal_Pos[Vertical_Pos] == 1:
            Third_Counter[Active_Chord] = (Third_Counter[Active_Chord]+1)%len(Third)
            PrintThird()
            
        elif Horizontal_Pos[Vertical_Pos] == 2:
            Seventh_Counter[Active_Chord] = (Seventh_Counter[Active_Chord]+1)%len(Seventh)
            PrintSeventh()
            
        elif Horizontal_Pos[Vertical_Pos] == 3:
            Color_Counter[Active_Chord] = (Color_Counter[Active_Chord]+1)%len(Color)
            if (Color_Counter[Active_Chord] != 0) and (Color_Counter[Active_Chord] == Color_2_Counter[Active_Chord]):
                Color_Counter[Active_Chord] = (Color_Counter[Active_Chord]+1)%len(Color)
            else:
                pass
            PrintColor()
            
        elif Horizontal_Pos[Vertical_Pos] == 4:
            Color_2_Counter[Active_Chord] = (Color_2_Counter[Active_Chord]+1)%len(Color)
            if (Color_2_Counter[Active_Chord] != 0) and (Color_Counter[Active_Chord] == Color_2_Counter[Active_Chord]):
                Color_2_Counter[Active_Chord] = (Color_2_Counter[Active_Chord]+1)%len(Color)
            else:
                pass
            PrintColor2()
            Write_Selection()
            
        elif Horizontal_Pos[Vertical_Pos] == 5:
            Over_Counter[Active_Chord] = (Over_Counter[Active_Chord]+1)%len(Over)
            PrintOver()
        else:
            pass
    else:
        pass
    
def Update_Down():
    global Vertical_Pos, Horizontal_Pos, Page,Active_Chord,steps,Third, Third_Counter,Over_Counter, Over
    global Seventh, Color,Seventh_Counter
    
    if Vertical_Pos == 0:
        if Horizontal_Pos[Vertical_Pos] == 0:
            Page = (Page-1)%int(steps/8)
            PrintPage()
            Write_Selection()
            if (Page*8) <= Active_Chord < ((Page*8)+8):
                PrintSelectedChord()
            else:
                RemoveSelectedChord()
        else:
            pass
        
    elif Vertical_Pos == 1:
        if Horizontal_Pos[Vertical_Pos] == 0:
            Root_Selector(False)
            PrintRoot()
            Write_Selection()
            
        elif Horizontal_Pos[Vertical_Pos] == 1:
            Third_Counter[Active_Chord] = (Third_Counter[Active_Chord]-1)%len(Third)
            PrintThird()
            
        elif Horizontal_Pos[Vertical_Pos] == 2:
            Seventh_Counter[Active_Chord] = (Seventh_Counter[Active_Chord]-1)%len(Seventh)
            PrintSeventh()
            
        elif Horizontal_Pos[Vertical_Pos] == 3:
            Color_Counter[Active_Chord] = (Color_Counter[Active_Chord]-1)%len(Color)
            
            if (Color_Counter[Active_Chord] != 0) and (Color_Counter[Active_Chord] == Color_2_Counter[Active_Chord]):
                Color_Counter[Active_Chord] = (Color_Counter[Active_Chord]-1)%len(Color)
                
            else:
                pass
            
            PrintColor()
            
        elif Horizontal_Pos[Vertical_Pos] == 4:
            Color_2_Counter[Active_Chord] = (Color_2_Counter[Active_Chord]-1)%len(Color)
            
            if (Color_2_Counter[Active_Chord] != 0) and (Color_Counter[Active_Chord] == Color_2_Counter[Active_Chord]):
                Color_2_Counter[Active_Chord] = (Color_2_Counter[Active_Chord]-1)%len(Color)
                
            else:
                pass
            
            PrintColor2()
            Write_Selection()
            
        elif Horizontal_Pos[Vertical_Pos] == 5:
            Over_Counter[Active_Chord] = (Over_Counter[Active_Chord]-1)%len(Over)
            PrintOver()
        else:
            pass
    else:
        pass

def Update_Up_Options():
    global Options_Vertical,Options_Horizontal,Input_Counter,Mode_Counter,Scale_Counter,Input,Mode, Scale,SaveLoad_flag
        
    if Options_Vertical == 1:
        if Options_Horizontal == 0:
            Input_Counter = (Input_Counter+1)%len(Input)
            PrintInput()
            Write_Selection()
            UpdateRGB()
            
        elif Options_Horizontal == 1:
            Mode_Counter = (Mode_Counter+1)%len(Mode)
            PrintMode()
            Write_Selection()
            
        elif Options_Horizontal == 2:
            Scale_Counter = (Scale_Counter+1)%len(Scale)
            PrintScale()
            Write_Selection()
        
        else:
            pass
    elif (Options_Vertical == 0) and (Options_Horizontal == 0):
        SaveLoad_flag = not SaveLoad_flag
        PrintSaveLoad()
        Write_Selection()
        
    else:
        pass
    
def Update_Down_Options():
    global Options_Vertical, Options_Horizontal,Input_Counter,Mode_Counter,Scale_Counter,Input,Mode,Scale,SaveLoad_flag
        
    if Options_Vertical == 1:
        if Options_Horizontal == 0:
            Input_Counter = (Input_Counter-1)%len(Input)
            PrintInput()
            Write_Selection()
            UpdateRGB()
            
        elif Options_Horizontal == 1:
            Mode_Counter = (Mode_Counter-1)%len(Mode)
            PrintMode()
            Write_Selection()
            
        elif Options_Horizontal == 2:
            Scale_Counter = (Scale_Counter-1)%len(Scale)
            PrintScale()
            Write_Selection()
        
        else:
            pass
    elif (Options_Vertical == 0) and (Options_Horizontal == 0):
        SaveLoad_flag = not SaveLoad_flag
        PrintSaveLoad()
        Write_Selection()
        
    else:
        pass
    
def Update_Up_Options_2():
    global Options_2_Vertical,Options_2_Horizontal,Sequence_Speed,Sequence_Speed_Counter,Contrast_Counter,Contrast,Scale_Root_Counter
    global Page_Select_Counter
    
    if Options_2_Vertical == 1 :
        if Options_2_Horizontal == 3: #on contrast level
            Contrast_Counter = (Contrast_Counter+1)%len(Contrast)
            PrintContrast()
            UpdateContrast()
            Write_Selection()
        elif Options_2_Horizontal == 2: # on jump max select
            Page_Select_Counter[1] = (Page_Select_Counter[1]+1)%32
            PrintPageSelect()
            Write_Selection()
        elif Options_2_Horizontal == 1: # on jump min select
            Page_Select_Counter[0] = (Page_Select_Counter[0]+1)%32
            PrintPageSelect()
            Write_Selection()
        else:
            pass
        
    elif (Options_2_Vertical==0) and (Options_2_Horizontal == 0): #on scale root
        Scale_Root_Counter = (Scale_Root_Counter+1)%len(Root)
        PrintScaleRoot()
        Write_Selection()
    else:
        pass
    
def Update_Down_Options_2():
    global Options_2_Vertical,Options_2_Horizontal,Sequence_Speed,Sequence_Speed_Counter,Contrast_Counter,Contrast,Scale_Root_Counter
    global Page_Select_Counter
    
    if Options_2_Vertical == 1:
        if Options_2_Horizontal == 3: #on contrast level
            Contrast_Counter = (Contrast_Counter-1)%len(Contrast)
            PrintContrast()
            UpdateContrast()
            Write_Selection()
        elif Options_2_Horizontal == 2: # on jump max select
            Page_Select_Counter[1] = (Page_Select_Counter[1]-1)%32
            PrintPageSelect()
            Write_Selection()
        elif Options_2_Horizontal == 1: # on jump select
            Page_Select_Counter[0] = (Page_Select_Counter[0]-1)%32
            PrintPageSelect()
            Write_Selection()
        else:
            pass
        
    elif (Options_2_Vertical==0) and (Options_2_Horizontal == 0): #on scale root
        Scale_Root_Counter = (Scale_Root_Counter-1)%len(Root)
        PrintScaleRoot()
        Write_Selection()
        
    else:
        pass
    
def Update_Up_Calibration():
    global Calibration_Horizontal, Calibration_Vertical,Channel_Counter, Vout_Counter, Calibration_offset
    
    if Calibration_Vertical == 1:
        if Calibration_Horizontal == 0: #on channel select
            Channel_Counter = (Channel_Counter+1)%8
            Update_All_Calibration()
            Write_Selection()
            
        elif Calibration_Horizontal == 1: #on Vout
            Vout_Counter = (Vout_Counter+1)%6
            PrintChannelVout()
            Update_Calibration_Out(Vout_Counter)
            Write_Selection()
            
        else: #on offset
            Calibration_offset[Channel_Counter] = min(Calibration_offset[Channel_Counter]+1,15)
            PrintChannelOffset()
            Update_Calibration_Out(Vout_Counter)
            Write_Selection()
    else:
        pass
    
def Update_Down_Calibration():
    global Calibration_Horizontal, Calibration_Vertical,Channel_Counter, Vout_Counter, Calibration_offset
    
    if Calibration_Vertical == 1:
        if Calibration_Horizontal == 0: #on channel select
            Channel_Counter = (Channel_Counter-1)%8
            Update_All_Calibration()
            Write_Selection()
            
        elif Calibration_Horizontal == 1: #on Vout
            Vout_Counter = (Vout_Counter-1)%6
            PrintChannelVout()
            Update_Calibration_Out(Vout_Counter)
            Write_Selection()
            
        else: #on offset
            Calibration_offset[Channel_Counter] = max(Calibration_offset[Channel_Counter]-1,-15)
            PrintChannelOffset()
            Update_Calibration_Out(Vout_Counter)
            Write_Selection()
        
    else:
        pass
    
def Update_Up_Chord():
    global Chord_Vertical, Chord_Horizontal,Shift_Counter, Spread_Counter,Active_Chord, GotoRepeat_Counter
    global Goto, GotoThen, Shift, Spread,GotoRepeat
    
    if Chord_Vertical == 1: #on the chord edit
        if Chord_Horizontal == 1:
            Shift_Counter[Active_Chord] = (Shift_Counter[Active_Chord]+1)%len(Shift)
            PrintShift()
            Write_Selection()
            
        elif Chord_Horizontal == 2:
            Spread_Counter[Active_Chord] = (Spread_Counter[Active_Chord]+1)%len(Spread)
            PrintSpread()
            Write_Selection()
            
        else:
            pass
        
    elif (Chord_Vertical == 2) and (Chord_Horizontal == 1):
        Active_Chord = (Active_Chord+1)%32
        RefreshChordPage()
        Write_Selection()
        
    elif Chord_Vertical == 0: #on the sequence edit
        if Chord_Horizontal == 0: #on jump select
            Goto[Active_Chord] = (Goto[Active_Chord]+1)%33
            PrintGoto()
            Write_Selection()
        
        elif Chord_Horizontal == 1: #on repeat select
            GotoRepeat_Counter[Active_Chord] = (GotoRepeat_Counter[Active_Chord]+1)%len(GotoRepeat)
            PrintGotoRepeat()
            Write_Selection()
        
        elif Chord_Horizontal == 2: #on normal sequence select
            GotoThen[Active_Chord] = (GotoThen[Active_Chord]+1)%32
            PrintGotoThen()
            Write_Selection()
        
        else:
            pass
    else:
        pass 
    
def Update_Down_Chord():
    global Chord_Vertical, Chord_Horizontal,Shift_Counter, Spread_Counter,Active_Chord, GotoRepeat_Counter
    global Goto, GotoThen, Shift, Spread,GotoRepeat, steps
    
    if Chord_Vertical == 1:
        if Chord_Horizontal == 1:
            Shift_Counter[Active_Chord] = (Shift_Counter[Active_Chord]-1)%len(Shift)
            PrintShift()
            Write_Selection()
            
        elif Chord_Horizontal == 2:
            Spread_Counter[Active_Chord] = (Spread_Counter[Active_Chord]-1)%len(Spread)
            PrintSpread()
            Write_Selection()
            
        else:
            pass
        
    elif (Chord_Vertical == 2) and (Chord_Horizontal == 1):
        Active_Chord = (Active_Chord-1)%steps
        RefreshChordPage()
        Write_Selection()
        
    elif Chord_Vertical == 0: #on the sequence edit
        if Chord_Horizontal == 0: #on jump select
            Goto[Active_Chord] = (Goto[Active_Chord]-1)%(steps+1)
            PrintGoto()
            Write_Selection()
        
        elif Chord_Horizontal == 1: #on repeat select
            GotoRepeat_Counter[Active_Chord] = (GotoRepeat_Counter[Active_Chord]-1)%len(GotoRepeat)
            PrintGotoRepeat()
            Write_Selection()
        
        elif Chord_Horizontal == 2: #on normal sequence select
            GotoThen[Active_Chord] = (GotoThen[Active_Chord]-1)%steps
            PrintGotoThen()
            Write_Selection()
        
        else:
            pass
    else:
        pass
    
def Update_Next_Active_Chord(flag): #refresh next
    global Active_Chord,Next_Active_Chord,Goto,Sequence_Repeat_Counter,GotoThen,Next_Next_Active_Chord
    global repeat_finish_flag, Sequence_Speed_Counter, GotoRepeat_Counter
    
    if not flag:
        pass
    else:
        if (Goto[Active_Chord] == 0) or (Sequence_Repeat_Counter[Active_Chord] == 0):
            if repeat_finish_flag[Active_Chord]:
                Sequence_Repeat_Counter[Active_Chord] = GotoRepeat_Counter[Active_Chord]
            else:
                pass
            Active_Chord = GotoThen[Active_Chord]
        else:
            Sequence_Repeat_Counter[Active_Chord] = Sequence_Repeat_Counter[Active_Chord]-1
            if Sequence_Repeat_Counter[Active_Chord] == 0:
                repeat_finish_flag[Active_Chord] = True
            else:
                pass
            Active_Chord = Goto[Active_Chord]-1
    
    if (Goto[Active_Chord] == 0) or (Sequence_Repeat_Counter[Active_Chord] == 0):
        Next_Active_Chord = GotoThen[Active_Chord]
    else:
        Next_Active_Chord = Goto[Active_Chord]-1

    if (Goto[Next_Active_Chord] == 0) or (Sequence_Repeat_Counter[Next_Active_Chord] == 0):
        Next_Next_Active_Chord = GotoThen[Next_Active_Chord]
    else:
        Next_Next_Active_Chord = Goto[Next_Active_Chord]-1
    
def RandomTrig(): #random trig
    global Active_Chord,Third_Counter,Color_2_Counter,random_flag, C1R_Counter,C2R_Counter,Sequence_Speed_Counter,Color
    
    random_flag = True
    big = getrandbits(6)
    col = (big>>2)
    if col%5 == 0: #if the two families of color are equal flip a bit to prevent that
        col ^= 0b1
    else:
        pass
    fam1 = (col & 0b0011)
    fam2 = (col >> 2)
    c2 = (big & 0b000001)
    choice = ((big>>2) & 0b0001)
    if Third_Counter[Active_Chord] == 0: #dominant chord
        if fam1 == 0:
            C1R_Counter = 1+choice #sus2 // sus4
        elif fam1 == 1:
            C1R_Counter = 5  #b6 (b13)
        elif fam1 == 2:
            C1R_Counter = 10+choice #b9 // add9
        else:
            C1R_Counter = 14  # add11
        if not c2:
            C2R_Counter = Color_2_Counter[Active_Chord]
        else:
            if fam2 == 0:
                C2R_Counter = 1+choice #sus2 // sus4
            elif fam2 == 1:
                C2R_Counter = 5 #b6 (b13)
            elif fam2 == 2:
                C2R_Counter = 10+choice #b9 // add9
            else:
                C2R_Counter = 14 # add11
    elif Third_Counter[Active_Chord] < 4: # M, +, m
        if fam1 == 0:
            C1R_Counter = 1 #sus2
        elif fam1 == 1:
            C1R_Counter = 5+(Third_Counter[Active_Chord]%2) # b6/add6
        elif fam1 == 2:
            C1R_Counter = 11 # add 9
        else:
            if Third_Counter[Active_Chord] == 3:
                C1R_Counter = 14 # add11
            else:
                C1R_Counter = 15 # #11
        if not c2:
            C2R_Counter = Color_2_Counter[Active_Chord]
        else:
            if fam2 == 0:
                C2R_Counter = 1
            elif fam2 == 1:
                C2R_Counter = 5+(Third_Counter[Active_Chord]%2)
            elif fam2 == 2:
                C2R_Counter = 11
            else:
                if Third_Counter[Active_Chord] == 3:
                    C2R_Counter = 14
                else:
                    C2R_Counter = 15
        
    else:   #o and half-o
        if not choice:
            C1R_Counter = 10-(Third_Counter[Active_Chord]-5) #b9 / add9
            if not c2:
                C2R_Counter = Color_2_Counter[Active_Chord]
            else:
                C2R_Counter = 14 #
        else:
            C1R_Counter = 14
            if not c2:
                C2R_Counter = Color_2_Counter[Active_Chord]
            else:
                C2R_Counter = 10-(Third_Counter[Active_Chord]-5)
        
    
    if Sequence_Speed_Counter == True:
        oled.rect(58,6,42,25,0,True)
        WriteF.text(Color[C1R_Counter].replace(' ',''),58,6)
        WriteF.text(Color[C2R_Counter].replace(' ',''),58,17)
    else:
        pass

def Selection_Manager():
    global select_flag, edit_menu_flag, options_menu_flag,chord_menu_flag, options_menu_2_flag,calibration_menu_flag
    
    select_flag = not select_flag
    
    if edit_menu_flag:
        Selection_Toggle_Edit()
        
    elif options_menu_flag:
        Selection_Toggle_Options()
    
    elif chord_menu_flag:
        Selection_Toggle_Chord()
    
    elif options_menu_2_flag:
        Selection_Toggle_Options_2()
    
    elif calibration_menu_flag:
        Selection_Toggle_Calibration()
        
    else:
        Selection_Toggle_Main()
        
def Update_Manager(way):
    global edit_menu_flag, options_menu_flag,chord_menu_flag, options_menu_2_flag,calibration_menu_flag
    
    if way:
        if edit_menu_flag:
            pass
        elif options_menu_flag:
            tb_trigger(True)
            Update_Up_Options()
        elif options_menu_2_flag:
            tb_trigger(True)
            Update_Up_Options_2()
        elif calibration_menu_flag:
            tb_trigger(True)
            Update_Up_Calibration()
        elif chord_menu_flag:
            tb_trigger(True)
            Update_Up_Chord()
        else:
            tb_trigger(True)
            Update_Up()
                        
    else:
        if edit_menu_flag:
            pass
        elif options_menu_flag:
            tb_trigger(True)
            Update_Down_Options()
        elif options_menu_2_flag:
            tb_trigger(True)
            Update_Down_Options_2()
        elif calibration_menu_flag:
            tb_trigger(True)
            Update_Down_Calibration()
        elif chord_menu_flag:
            tb_trigger(True)
            Update_Down_Chord()
        else:
            tb_trigger(True)
            Update_Down()
    
def MainMenu(flag=True): #Main Menu
    ResetPosition()
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
    
    WriteS.text('-chord-',37,0)
    oled.rect(103,21,2,23,1,True)
    WriteS.text('edit',3,0)
    WriteS.text('-global-',85,0)
    Update_All_Scaled_Root()
    Update_All_Scaled_Third()
    RefreshActiveChord()
    PrintPage()
    PrintSelectedChord()
    Selection_Toggle_Main()
    if flag:
        oled.show()
    else:
        pass

def EditMenu(): #Edit Menu
    oled.rect(21,7,86,50,0,True)
    oled.rect(20,6,88,52,1)
    oled.rect(19,5,90,54,1)
    oled.vline(64,27,24,1)
    
    WriteS.text('back',52,10)
    WriteS.text('copy',30,24)
    WriteS.text('clear',72,24)
    WriteS.text('paste',29,38)
    WriteS.text('cl. all',72,38)
    Selection_Toggle_Edit()
    oled.show()
    
def OptionsMenu1(): #Page 1 of the Global Menu
    oled.fill(0)
    oled.rect(0,15,128,30,1)
    oled.rect(0,44,128,20,1)
    oled.vline(43,16,28,1)
    oled.vline(86,16,28,1)
    
    WriteS.text('- back -',47,0)
    WriteS.text('>>>',98,0)
    WriteS.text('GATE',7,16)
    WriteS.text('MODE',48,16)
    WriteS.text('SCALE',90,16)

    WriteS.text('1',53,47)
    WriteS.text('2',73,47)
    WriteS.text('3',93,47)
    WriteS.text('4',113,47)
    
    PrintInput()
    PrintMode()
    PrintScale()
    PrintSaveLoad()
    UpdateRGB()
    Selection_Toggle_Options()
    oled.show()
    
def OptionsMenu2(): #Page 2 of the Global Menu
    oled.fill(0)
    oled.rect(0,15,128,30,1)
    oled.rect(0,44,128,20,1)
    oled.vline(43,16,28,1)
    oled.vline(86,16,47,1)
    
    WriteS.text('- back -',47,0)
    WriteS.text('<<<',14,0)
    WriteS.text('VIEW',8,16)
    WriteS.text('JUMP',50,16)
    WriteS.text('BRITE.',91,16)
    WriteS.text('calibr.',91,47)
    WriteS.text('scale root-',4,47)
    
    PrintSequenceSpeed()
    PrintPageSelect()
    PrintContrast()
    PrintScaleRoot()
    Selection_Toggle_Options_2()
    oled.show()
    
def CalibrationMenu(): #calibration menu
    global Vout_Counter
    
    oled.fill(0)
    oled.rect(0,15,128,30,1)
    oled.vline(43,16,28,1)
    oled.vline(86,16,28,1)
    
    WriteS.text('- cancel -',44,0)
    WriteS.text('- save & exit -',29,47)
    WriteS.text('out',4,0)
    WriteS.text('v1.2',105,0)
    
    oled.rect(0,0,26,16,1)
    oled.hline(3,15,3,0)
    oled.hline(9,15,3,0)
    oled.hline(15,15,3,0)
    oled.hline(21,15,3,0)
    
    PrintChannelSelect()
    PrintChannelVout()
    PrintChannelOffset()
    Selection_Toggle_Calibration()
    oled.show()

def ChordMenu(): #Chord Menu
    global Active_Chord
    
    oled.fill(0)
    oled.rect(0,15,128,30,1) #outline
    oled.rect(0,44,128,20,1)
    oled.vline(43,16,29,1)
    oled.vline(86,16,29,1)
    
    WriteS.text('clear',95,0)
    WriteS.text('- back -',4,0)
    WriteS.text('VOICE',4,16)
    WriteS.text('SHIFT',50,16)
    WriteS.text('SPRD.',92,16)
    WriteS.text('go to',4,47)
    WriteS.text('then',80,47)
    
    PrintRootHelp()
    PrintChordNumber()
    PrintInvert()
    PrintShift()
    PrintSpread()
    PrintGoto()
    PrintGotoRepeat()
    PrintGotoThen()
    Selection_Toggle_Chord()
    oled.show()

def PSMenu(first=True): #Play Stop Menu
    global Active_Chord
    
    oled.fill(0)
    oled.rect(103,6,2,20,1,True)
    oled.hline(0,63,28,1)
    oled.vline(28,31,32,1)
    oled.rect(29,43,17,11,1,True)
    draw.fill_triangle(29,37,29,59,37,50,1)
    #goto rectangles
    oled.rect(96,44,6,9,1,True)
    oled.rect(102,38,27,21,1)
    oled.rect(46,38,50,21,1)
    #center line
    oled.hline(29,31,100,1)
    oled.hline(0,0,127,1)
    oled.vline(0,0,63,1)
    #dotted line
    oled.hline(1,31,3,1)
    oled.hline(7,31,3,1)
    oled.hline(13,31,3,1)
    oled.hline(19,31,3,1)
    oled.hline(25,31,3,1)
    
    if first:
        Active_Chord = 0
        ResetSequenceRepeats()
        Update_Next_Active_Chord(False)
    else:
        pass
    UpdateNextChordPLAYSTOP()
    UpdateNextActiveDirection()
    UPDATE_OUTS(True)

################################################################################################################################################################
### CORE --SAVE/LOAD--  FUCTIONS
    

def SaveScene(slot): #save function
    global Root_Counter, Third_Counter, Seventh_Counter, Color_Counter, Color_2_Counter, steps
    global Over_Counter,voicing_flag,Shift_Counter,Spread_Counter,Goto,GotoRepeat_Counter,Scale_Root_Counter
    global GotoThen, Input_Counter, Scale_Counter, Mode_Counter, Sequence_Speed_Counter, Page_Select_Counter
    
    #create buffer in csv format with all the needed variables and arrays
    
    buffer = ''
    for i in range(steps):
        buffer += (str(Root_Counter[i])+',')
    for i in range(steps):
        buffer += (str(Third_Counter[i])+',')
    for i in range(steps):
        buffer += (str(Seventh_Counter[i])+',')
    for i in range(steps):
        buffer += (str(Color_Counter[i])+',')
    for i in range(steps):
        buffer += (str(Color_2_Counter[i])+',')
    for i in range(steps):
        buffer += (str(Over_Counter[i])+',')
    for i in range(steps):
        buffer += (str(int(voicing_flag[i]))+',')
    for i in range(steps):
        buffer += (str(Shift_Counter[i])+',')
    for i in range(steps):
        buffer += (str(Spread_Counter[i])+',')
    for i in range(steps):
        buffer += (str(Goto[i])+',')
    for i in range(steps):
        buffer += (str(GotoRepeat_Counter[i])+',')
    for i in range(steps):
        buffer += (str(GotoThen[i])+',')
    buffer += (str(Input_Counter)+',')
    buffer += (str(Mode_Counter)+',')
    buffer += (str(Sequence_Speed_Counter)+',')
    buffer += (str(Scale_Counter)+',')
    buffer += (str(Page_Select_Counter[0])+',')
    buffer += (str(Page_Select_Counter[1])+',')
    buffer += (str(Scale_Root_Counter))
    
    #write buffer to the correct slot file
    
    if slot == 1:
        save = open('slot1.csv', 'w')
        save.write(buffer)
        save.close()
    elif slot == 2:
        save = open('slot2.csv', 'w')
        save.write(buffer)
        save.close()
    elif slot == 3:
        save = open('slot3.csv', 'w')
        save.write(buffer)
        save.close()
    else:
        save = open('slot4.csv', 'w')
        save.write(buffer)
        save.close()

def LoadScene(slot): #load function
    global Root_Counter, Third_Counter, Seventh_Counter, Color_Counter, Color_2_Counter, steps
    global Over_Counter,voicing_flag,Shift_Counter,Spread_Counter,Goto,GotoRepeat_Counter,Scale_Root_Counter
    global GotoThen, Input_Counter, Scale_Counter, Mode_Counter, Sequence_Speed_Counter, Page_Select_Counter
    
    #load in the selected slot and create a buffer with all values
    
    if slot == 1:
        load = open('slot1.csv', 'r')
        buffer = load.read()
        load.close()
    elif slot == 2:
        load = open('slot2.csv', 'r')
        buffer = load.read()
        load.close()
    elif slot == 3:
        load = open('slot3.csv', 'r')
        buffer = load.read()
        load.close()
    else:
        load = open('slot4.csv', 'r')
        buffer = load.read()
        load.close()
    
    full = list(map(int,buffer.split(','))) #translates the csv to an int array
    
    #write all new values to the needed variables and arrays
    
    for i in range(steps):
        Root_Counter[i] = full[i]
    for i in range(steps):
        Third_Counter[i] = full[i+(steps)]
    for i in range(steps):
        Seventh_Counter[i] = full[i+(2*steps)]
    for i in range(steps):
        Color_Counter[i] = full[i+(3*steps)]
    for i in range(steps):
        Color_2_Counter[i] = full[i+(4*steps)]
    for i in range(steps):
        Over_Counter[i] = full[i+(5*steps)]
    for i in range(steps):
        voicing_flag[i] = full[i+(6*steps)]
    for i in range(steps):
        Shift_Counter[i] = full[i+(7*steps)]
    for i in range(steps):
        Spread_Counter[i] = full[i+(8*steps)]
    for i in range(steps):
        Goto[i] = full[i+(9*steps)]
    for i in range(steps):
        GotoRepeat_Counter[i] = full[i+(10*steps)]
    for i in range(steps):
        GotoThen[i] = full[i+(11*steps)]
    Input_Counter = full[12*steps]
    Mode_Counter = full[(12*steps)+1]
    Sequence_Speed_Counter = full[(12*steps)+2]
    Scale_Counter = full[(12*steps)+3]
    Page_Select_Counter[0] = full[(12*steps)+4]
    Page_Select_Counter[1] = full[(12*steps)+5]
    Scale_Root_Counter = full[(12*steps)+6]
    
### CALIBRATION SETTINGS SAVE/LOAD ###
    
def SaveCalibrationSettings():
    global Calibration_offset, CO_buffer
        
    CO_buffer = Calibration_offset
        
    buffer = ''
    for i in range(7):
        buffer += (str(Calibration_offset[i])+',')
    buffer += (str(Calibration_offset[7]))
    
    save = open('calibration.csv', 'w')
    save.write(buffer)
    save.close()
    
def LoadCalibrationSettings():
    global Calibration_offset, CO_buffer
    
    load = open('calibration.csv', 'r')
    buffer = load.read()
    load.close()
    
    full = list(map(int,buffer.split(','))) #translates the csv to an int array
    
    for i in range(8):
        Calibration_offset[i] = full[i]
    CO_buffer = Calibration_offset

################################################################################################################################################################
### CORE --DAC--  FUCTIONS


def snap_value(arr,value):
    
    return min(arr, key=lambda x:abs(x-value))

def restrict(val, minval, maxval):
    if val < minval: return minval
    if val > maxval: return maxval
    return val

def Root_Sort(out,oct_amt,over_enable=0):
    global NOTES, VOCT_buffer, Octave, Active_Chord, Over_Counter, Root_Counter
    
    if over_enable:
        if not Over_Counter[Active_Chord]:
            VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+Octave*oct_amt]
        else:
            VOCT_buffer[out] = NOTES[(Over_Counter[Active_Chord]-1)+(Octave*oct_amt)]
    else:
        VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+(Octave*oct_amt)]

def Third_Sort(out,oct_amt):
    global Root_Counter, Third_Counter, Color_Counter, Color_2_Counter, Active_Chord, NOTES, VOCT_buffer, Octave
    
    if Third_Counter[Active_Chord] < 3: #major quality
            VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+4+(Octave*oct_amt)]
            
    else: #minor quality
        VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+3+(Octave*oct_amt)]
            
    if Color_Counter[Active_Chord] == 1:     #sus2
        VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+2+(Octave*oct_amt)]
    elif Color_Counter[Active_Chord] == 2:   #sus4
        VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+5+(Octave*oct_amt)]
    elif Color_2_Counter[Active_Chord] == 1: #sus2
        VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+2+(Octave*oct_amt)]
    elif Color_2_Counter[Active_Chord] == 2: #sus4
        VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+5+(Octave*oct_amt)]
    else:
        pass
    
def Fifth_Sort(out,oct_amt):
    global Root_Counter, Third_Counter, Color_Counter, Color_2_Counter, NOTES, VOCT_buffer, Octave, Active_Chord
    
    if Third_Counter[Active_Chord] == 2: #augmented chord
        VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+8+(Octave*oct_amt)]
        
    elif (Third_Counter[Active_Chord] == 4) or (Third_Counter[Active_Chord] == 5): #diminished chord
        VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+6+(Octave*oct_amt)]
        
    elif Third_Counter[Active_Chord] == 0:
        if Color_Counter[Active_Chord] == 3: #b5
            VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+6+(Octave*oct_amt)]
            
        elif Color_Counter[Active_Chord] == 4: ##5
            VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+8+(Octave*oct_amt)]
            
        elif Color_2_Counter[Active_Chord] == 3: #b5
            VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+6+(Octave*oct_amt)]
            
        elif Color_2_Counter[Active_Chord] == 4: ##5
            VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+8+(Octave*oct_amt)]
            
        else: #none of the above
            VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+7+(Octave*oct_amt)]
            
    else: #no quality that changes the fifth
        VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+7+(Octave*oct_amt)]
        
def Seventh_Sort(out,oct_amt):
    global Root_Counter, Third_Counter, Seventh_Counter, Color_Counter, Color_2_Counter, Active_Chord, NOTES, VOCT_buffer, Octave
    
    if Seventh_Counter[Active_Chord]:
        if Third_Counter[Active_Chord] == 1:     #M7 quality
            VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+11+(Octave*oct_amt)]
        elif Third_Counter[Active_Chord] == 4:   #bb7 quality
            VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+9+(Octave*oct_amt)]
        else:                                    #m7 quality
            VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+10+(Octave*oct_amt)]
    else:
        if Color_Counter[Active_Chord] == 7:     #min7
            VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+10+(Octave*oct_amt)]
        elif Color_Counter[Active_Chord] == 8:   #maj7
            VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+11+(Octave*oct_amt)]
        elif Color_2_Counter[Active_Chord] == 7: #min7
            VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+10+(Octave*oct_amt)]
        elif Color_2_Counter[Active_Chord] == 8: #maj7
            VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+11+(Octave*oct_amt)]
        else:
            Fifth_Sort(out,1) #if no seventh == defined, the output == a fifth
            
def Color_Sort(out,oct_amt,color_number):
    global NOTES, VOCT_buffer, Octave, Active_Chord, Color_Counter, Color_2_Counter, Root_Counter, Mode_Counter
    
    if color_number == 1: #1st color
        if (Color_Counter[Active_Chord] < 5) or (6 < Color_Counter[Active_Chord] < 9):
            if Mode_Counter == 0:
                Fifth_Sort(out,1) #if no color and normal mode then color_1 becomes the fifth
            else:
                Seventh_Sort(out,1) #if no color and alt mode then color_1 becomes the seventh
        else:
            if Color_Counter[Active_Chord] < 7: #b6 or add6
                VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+Color_Counter[Active_Chord]+3+(Octave*oct_amt)]
            else: #all the higher octave colors
                VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+((Color_Counter[Active_Chord]+3)%12)+(Octave*(oct_amt+1))]
                
    elif color_number == 2: #2nd color
        if (Color_2_Counter[Active_Chord] < 5) or (6 < Color_2_Counter[Active_Chord] < 9):
            Third_Sort(out,1) #if no color then color_2 becomes the third
        else:
            if Color_2_Counter[Active_Chord] < 7: #b6 or add6
                VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+Color_2_Counter[Active_Chord]+3+(Octave*oct_amt)]
            else: #all the higher octave colors
                VOCT_buffer[out] = NOTES[Root_Counter[Active_Chord]+((Color_2_Counter[Active_Chord]+3)%12)+(Octave*(oct_amt+1))]
    else:
        pass

def Color_Sort_rndm(flag=True): #randomized coloring based on root and octave of colors
    global C1R_Counter,C2R_Counter,Color_Counter,Color_2_Counter,Root_Counter,Active_Chord,NOTES,VOCT_buffer,Octave,random_flag
    
    if C1R_Counter == Color_Counter or C1R_Counter == 0:
        pass
    elif 0 < C1R_Counter < 3 and flag: #sus2 or sus4
        oct_amt = int(VOCT_buffer[0]/(NOTES[Root_Counter[Active_Chord]+Octave]))
        VOCT_buffer[0] = NOTES[Root_Counter[Active_Chord]+1+C1R_Counter+(Octave*oct_amt)]
        while VOCT_buffer[0] > 4095:
            VOCT_buffer[0] = VOCT_buffer[0] - NOTES[Octave]
    elif 4 < C1R_Counter < 7: #b6 or add6
        oct_amt = int(VOCT_buffer[2]/(NOTES[Root_Counter[Active_Chord]+Octave]))
        VOCT_buffer[2] = NOTES[Root_Counter[Active_Chord]+C1R_Counter+3+(Octave*oct_amt)]
        while VOCT_buffer[2] > 4095:
            VOCT_buffer[2] = VOCT_buffer[2] - NOTES[Octave]
    elif C1R_Counter > 8: #colors above maj7
        oct_amt = int(VOCT_buffer[2]/(NOTES[Root_Counter[Active_Chord]+Octave]))
        VOCT_buffer[2] = NOTES[Root_Counter[Active_Chord]+((C1R_Counter+3)%12)+(Octave*(oct_amt+(oct_amt!=4)))]
        while VOCT_buffer[2] > 4095:
            VOCT_buffer[2] = VOCT_buffer[2] - NOTES[Octave]
    else:
        pass
    
    ##########
    
    if C2R_Counter == Color_2_Counter or C2R_Counter == 0:
        pass
    elif 0 < C2R_Counter < 3 and flag: #sus2 or sus4
        oct_amt = int(VOCT_buffer[0]/(NOTES[Root_Counter[Active_Chord]+Octave]))
        VOCT_buffer[0] = NOTES[Root_Counter[Active_Chord]+1+C2R_Counter+(Octave*oct_amt)]
        while VOCT_buffer[0] > 4095:
            VOCT_buffer[0] = VOCT_buffer[0] - NOTES[Octave]
    elif 4 < C2R_Counter < 7: #b6 or add6
        oct_amt = int(VOCT_buffer[3]/(NOTES[Root_Counter[Active_Chord]+Octave]))
        VOCT_buffer[3] = NOTES[Root_Counter[Active_Chord]+C2R_Counter+3+(Octave*oct_amt)]
        while VOCT_buffer[3] > 4095:
            VOCT_buffer[3] = VOCT_buffer[3] - NOTES[Octave]
    elif C2R_Counter > 8: #colors above maj7
        oct_amt = int(VOCT_buffer[3]/(NOTES[Root_Counter[Active_Chord]+Octave]))
        VOCT_buffer[3] = NOTES[Root_Counter[Active_Chord]+((C2R_Counter+3)%12)+(Octave*(oct_amt+(oct_amt!=4)))]
        while VOCT_buffer[3] > 4095:
            VOCT_buffer[3] = VOCT_buffer[3] - NOTES[Octave]
    else:
        pass
    
    ##########
    
    random_flag = False

def ShiftChord():
    global NOTES, VOCT_buffer, Octave, Shift, Active_Chord, Shift_Counter
    
    #currently, shift goes from -10 to +10, needs change if that changes
    
    if Shift_Counter[Active_Chord] < 11: #positive shift
        shifts_done = 0
        while shifts_done < Shift_Counter[Active_Chord]:
            Sorted_Notes = sorted([VOCT_buffer[7],VOCT_buffer[0],VOCT_buffer[1],VOCT_buffer[2],VOCT_buffer[3]]) 
            note_to_shift = 0
            #finds which == the lowest to shift it up
            for i in range(5):
                if i == 4:
                    i = 7
                else:
                    pass
                if Sorted_Notes[0] == VOCT_buffer[i]:
                    note_to_shift = i
                else:
                    pass
            #shift up if possible
            if VOCT_buffer[note_to_shift]+NOTES[Octave] <= NOTES[11+(4*Octave)]:
                VOCT_buffer[note_to_shift] = snap_value(NOTES,VOCT_buffer[note_to_shift]+NOTES[Octave])
            else:
                pass
            shifts_done = shifts_done+1
            
    else: #negative shift
        n_shifts_done = 0
        while n_shifts_done < (len(Shift) - Shift_Counter[Active_Chord]):
            Sorted_Notes = sorted([VOCT_buffer[7],VOCT_buffer[0],VOCT_buffer[1],VOCT_buffer[2],VOCT_buffer[3]]) 
            note_to_shift = 0
            #finds which == the highest to shift it down
            for i in range(5):
                if i == 4:
                    i = 7
                else:
                    pass
                if Sorted_Notes[4] == VOCT_buffer[i]:
                    note_to_shift = i
                else:
                    pass
            #shift down if possible
            if VOCT_buffer[note_to_shift]-NOTES[Octave] >= 0:
                VOCT_buffer[note_to_shift] = snap_value(NOTES,VOCT_buffer[note_to_shift]-NOTES[Octave])
            else:
                pass
            n_shifts_done = n_shifts_done+1      
    
def ShiftChord_Trig(mode):
    global Trig_Shift_Counter, shift_trig_flag, VOCT_buffer, Octave
    
    if Trig_Shift_Counter == 0: #shift up two octaves (25% chance)
        if mode == 0:
            for i in range(5):
                if i == 4:
                    i = 7
                else:
                    pass
                if VOCT_buffer[i]+2*NOTES[Octave] <= 4095:
                    VOCT_buffer[i] = VOCT_buffer[i]+2*NOTES[Octave]
                elif VOCT_buffer[i]+NOTES[Octave] <= 4095:
                    VOCT_buffer[i] = VOCT_buffer[i]+NOTES[Octave]
                else:
                    pass
        else:
            for i in range(2,5):
                if i == 4:
                    i = 7
                else:
                    pass
                if VOCT_buffer[i]+2*NOTES[Octave] <= 4095:
                    VOCT_buffer[i] = VOCT_buffer[i]+2*NOTES[Octave]
                elif VOCT_buffer[i]+NOTES[Octave] <= 4095:
                    VOCT_buffer[i] = VOCT_buffer[i]+NOTES[Octave]
                else:
                    pass
            
    else: #shift up one octave (75% chance)
        if mode == 0:
            for i in range(5):
                if i == 4:
                    i = 7
                else:
                    pass
                if VOCT_buffer[i]+NOTES[Octave] <= 4095:
                    VOCT_buffer[i] = VOCT_buffer[i]+NOTES[Octave]
                else:
                    pass
        else:
            for i in range(2,5):
                if i == 4:
                    i = 7
                else:
                    pass
                if VOCT_buffer[i]+NOTES[Octave] <= 4095:
                    VOCT_buffer[i] = VOCT_buffer[i]+NOTES[Octave]
                else:
                    pass 
    
    ###########    
    shift_trig_flag = False
    
def SpreadChord(flag=False):
    global VOCT_buffer, Octave, Active_Chord, Spread_Counter, Trig_Spread_Counter, spread_trig_flag
    
    spreads_done = 0
    if flag:
        a = Trig_Spread_Counter
    else:
        a = Spread_Counter[Active_Chord]     
    while spreads_done < a:
        Sorted_Notes = sorted([VOCT_buffer[7],VOCT_buffer[0],VOCT_buffer[1],VOCT_buffer[2],VOCT_buffer[3]]) 
        note_to_spread = 0
        #finds which == the 2nd lowest//3rd lowest//4th lowest to spread them
        for i in range(5):
            if i == 4:
                i = 7
            else:
                pass
            if Sorted_Notes[(spreads_done%3)+1] == VOCT_buffer[i]:
                note_to_spread = i
            else:
                pass
        #spread if possible
        if VOCT_buffer[note_to_spread] <= 4095-NOTES[Octave]:
            VOCT_buffer[note_to_spread] = snap_value(NOTES,VOCT_buffer[note_to_spread]+NOTES[Octave])
        else:
            pass
        #spread done
        spreads_done = spreads_done+1
    
    ####
    spread_trig_flag = False
        
def VoiceChord():
    global NOTES, VOCT_buffer, Octave
    
    #settg where the gravity == (currently D + 1 octaves)
    gravity = NOTES[8+Octave]
    #voicing T1,S1,C1,C2,R3
    for i in range(5):
        if i == 4:
            i = 7
        else:
            pass
        if abs((VOCT_buffer[i]-NOTES[Octave])-gravity) <= abs(VOCT_buffer[i]-gravity):
            if VOCT_buffer[i]-NOTES[Octave] >= 0:
                VOCT_buffer[i] = snap_value(NOTES,VOCT_buffer[i]-NOTES[Octave])
            else:
                pass
            
        elif abs((VOCT_buffer[i]+NOTES[Octave])-gravity) < abs(VOCT_buffer[i]-gravity):
            if VOCT_buffer[i]+NOTES[Octave] <= NOTES[11+(4*Octave)]:
                VOCT_buffer[i] = snap_value(NOTES,VOCT_buffer[i]+NOTES[Octave])
            else:
                pass    
        else:
            pass

def ChordMode_Quality(out):
    global VOCT_buffer, Active_Chord, Color_Counter, Color_2_Counter, Third_Counter
    
    if Third_Counter[Active_Chord] == 0: #dom
        if (Color_Counter[Active_Chord] == 2) or (Color_2_Counter[Active_Chord] == 2): #sus4
            VOCT_buffer[out] = 3312
        else:
            VOCT_buffer[out] = 1147
    elif Third_Counter[Active_Chord] == 1: #maj
        if (Color_Counter[Active_Chord] == 1) or (Color_2_Counter[Active_Chord] == 1): #sus2
            VOCT_buffer[out] = 2621
        else:
            VOCT_buffer[out] = 0
    elif Third_Counter[Active_Chord] == 2: #aug
        VOCT_buffer[out] = 4095
    elif Third_Counter[Active_Chord] == 3: #min
        VOCT_buffer[out] = 655
    elif Third_Counter[Active_Chord] == 4: #dim
        VOCT_buffer[out] = 2129
    else: #half-dim
        VOCT_buffer[out] = 1638
        
def ChordMode_Voicing(out,root_out,c1_out,c2_out):
    global VOCT_buffer, Active_Chord, voicing_flag, Spread_Counter, Shift_Counter, Octave, Root_Counter
    
    spread = (Spread_Counter[Active_Chord] != 0) #spread or not
    inv_deg = 0
    oct_jmp = 0
    root = Root_Counter[Active_Chord]
    
    ### voice
    if voicing_flag[Active_Chord]:
        if root == 0:
            pass
        else:
            oct_jmp = -1
            if root < 5:
                inv_deg = 3
            elif root < 8:
                inv_deg = 2
            elif root < 11:
                inv_deg = 1
            else:
                pass
    else:
        pass
    
    ### invert
    if Shift_Counter[Active_Chord] == 0:
        pass
    else:
        inv_deg = 0
        oct_jmp = 0
        if Shift_Counter[Active_Chord] < 11:
            inv_deg = (Shift_Counter[Active_Chord])%4
            oct_jmp = int(Shift_Counter[Active_Chord]/4)
        elif Shift_Counter[Active_Chord] > 16:
            inv_deg = (Shift_Counter[Active_Chord]-21)%4
            oct_jmp = -1
        else:
            inv_deg = 0
            oct_jmp = -1
    
    ### assign vout
    if spread:
        if inv_deg == 0:
            VOCT_buffer[out] = 2826
        elif inv_deg == 1:
            VOCT_buffer[out] = 3071
        elif inv_deg == 2:
            VOCT_buffer[out] = 3317
        else:
            VOCT_buffer[out] = 3481
    else:
        if inv_deg == 0:
            VOCT_buffer[out] = 0
        elif inv_deg == 1:
            VOCT_buffer[out] = 860
        elif inv_deg == 2:
            VOCT_buffer[out] = 1761
        else:
            VOCT_buffer[out] = 2580
    if NOTES[Octave] <= VOCT_buffer[root_out] <= 4095-(2*NOTES[Octave]):
        VOCT_buffer[root_out] = snap_value(NOTES,VOCT_buffer[root_out]+(oct_jmp*NOTES[Octave]))
    else:
        pass
    if NOTES[Octave] <= VOCT_buffer[c1_out] <= 4095-(2*NOTES[Octave]) and oct_jmp > 0:
        VOCT_buffer[c1_out] = snap_value(NOTES,VOCT_buffer[c1_out]+(oct_jmp*NOTES[Octave]))
    else:
        pass
    if NOTES[Octave] <= VOCT_buffer[c2_out] <= 4095-(2*NOTES[Octave]) and oct_jmp > 0:
        VOCT_buffer[c2_out] = snap_value(NOTES,VOCT_buffer[c2_out]+(oct_jmp*NOTES[Octave]))
    else:
        pass
    
def ChordMode_SpreadTrig(out):
    global VOCT_buffer, spread_trig_flag
    
    if VOCT_buffer[out] == 0: #root position
        VOCT_buffer[out] = 2826
    elif VOCT_buffer[out] == 860: #1st inversion
        VOCT_buffer[out] = 3071
    elif VOCT_buffer[out] == 1761: #2nd inversion
        VOCT_buffer[out] = 3317
    elif VOCT_buffer[out] == 2580: #3rd inversion
        VOCT_buffer[out] = 3481
    else:
        pass #already spread
    
    ####
    spread_trig_flag = False
    
def PlaitsMode_Quality(out):
    global VOCT_buffer, Active_Chord, Seventh_Counter, Color_Counter, Color_2_Counter, Third_Counter
    
    if Third_Counter[Active_Chord] == 0: #dom
        VOCT_buffer[out] = 4095
    elif Third_Counter[Active_Chord] == 1: #maj
        if Color_Counter[Active_Chord] == 11 or Color_2_Counter[Active_Chord] == 11: #maj9
            VOCT_buffer[out] = 3194
        elif Color_Counter[Active_Chord] == 6 or Color_2_Counter[Active_Chord] == 6: #maj6
            VOCT_buffer[out] = 2785
        elif Seventh_Counter[Active_Chord] == 1: #seventh
            VOCT_buffer[out] = 3604
        else: #maj triad
            VOCT_buffer[out] = 4095
    elif Third_Counter[Active_Chord] == 2: #aug
        VOCT_buffer[out] = 4095
    elif Third_Counter[Active_Chord] == 3: #min
        if Color_Counter[Active_Chord] == 14 or Color_2_Counter[Active_Chord] == 14: #min11
            VOCT_buffer[out] = 2375
        elif Color_Counter[Active_Chord] == 11 or Color_2_Counter[Active_Chord] == 11: #min9
            VOCT_buffer[out] = 1966
        elif Seventh_Counter[Active_Chord] == 1: #seventh
            VOCT_buffer[out] = 1556
        else: #min triad
            VOCT_buffer[out] = 1147
    elif Third_Counter[Active_Chord] == 4: #dim
        VOCT_buffer[out] = 1147
    else: #half-dim
        VOCT_buffer[out] = 1147
    if Color_Counter[Active_Chord] == 2 or Color_2_Counter[Active_Chord] == 2: #sus4
        VOCT_buffer[out] = 778
    else:
        pass
    
def PlaitsMode_Voicing(out):
    global VOCT_buffer, Active_Chord, voicing_flag, Shift_Counter, Root_Counter
    
    #define and voice
    shift = 0
    if voicing_flag[Active_Chord]:
        a = Root_Counter[Active_Chord]
        if a == 2: #B
            shift = -1
        elif a == 3: #C
            shift = -2
        elif 3 < a < 7: #Eb, D, or Db
            shift = -3
        elif a == 7: #E
            shift = -4
        elif a == 8: #F
            shift = -5
        elif a == 9 or a == 10: #Gb or G
            shift = -6
        elif a == 11: #Ab
            shift = -7
        else: #Bb or A
            pass
    else:
        pass
    
    #shift input
    if Shift_Counter[Active_Chord] == 0:
        pass
    else:
        if Shift_Counter[Active_Chord] < 11:
            shift = Shift_Counter[Active_Chord]
        else:
            shift = Shift_Counter[Active_Chord]-21
    
    #assign output
    VOCT_buffer[out] = int(((2.5+(0.25*shift))/5)*4095)
    
def OrganMode_Quality(out):
    global VOCT_buffer, Active_Chord, Seventh_Counter, Color_Counter, Color_2_Counter, Third_Counter
    
    if Third_Counter[Active_Chord] == 0: #dom
        VOCT_buffer[out] = 88
    elif Third_Counter[Active_Chord] == 1: #maj
        if Color_Counter[Active_Chord] == 11 or Color_2_Counter[Active_Chord] == 11: #maj9
            VOCT_buffer[out] = 776
        elif Color_Counter[Active_Chord] == 6 or Color_2_Counter[Active_Chord] == 6: #maj6
            VOCT_buffer[out] = 1625
        elif Seventh_Counter[Active_Chord] == 1: #seventh
            VOCT_buffer[out] = 432
        else: #maj triad
            VOCT_buffer[out] = 88
    elif Third_Counter[Active_Chord] == 2: #aug
        VOCT_buffer[out] = 2133
    elif Third_Counter[Active_Chord] == 3: #min
        if Color_Counter[Active_Chord] == 11 or Color_2_Counter[Active_Chord] == 11: #min9
            VOCT_buffer[out] = 945
        elif Color_Counter[Active_Chord] == 6 or Color_2_Counter[Active_Chord] == 6: #min6
            VOCT_buffer[out] = 1797
        elif Seventh_Counter[Active_Chord] == 1: #seventh
            VOCT_buffer[out] = 604
        else: #min triad
            VOCT_buffer[out] = 262
    elif Third_Counter[Active_Chord] == 4: #dim
        VOCT_buffer[out] = 1965
    else: #half-dim
        VOCT_buffer[out] = 1965
    if Color_Counter[Active_Chord] == 2 or Color_2_Counter[Active_Chord] == 2: #sus4
        VOCT_buffer[out] = 1115
    else:
        pass
    
def UpdateVOCTBuffer_Normal(mode):
    global Shift_Counter, Spread_Counter, voicing_flag, Active_Chord
    
    Root_Sort(4,0,1)
    Fifth_Sort(5,0)
    Root_Sort(6,1,1)
    Root_Sort(7,1)
    Color_Sort(2,1,1)
    Color_Sort(3,1,2)
    
    if mode == 1: #Chord (Qu-Bit Elec.)
        ChordMode_Quality(0)
        ChordMode_Voicing(1,7,2,3)
        
    elif mode == 2: #Plaits (MI)
        PlaitsMode_Quality(0)
        PlaitsMode_Voicing(1)
        
    elif mode == 3: #Chord Organ (MTM)
        OrganMode_Quality(0)
    
    else: #normal
        Third_Sort(0,1)
        Seventh_Sort(1,1) 
        if not voicing_flag[Active_Chord]:
            pass
        else:
            VoiceChord()
        ShiftChord()
        SpreadChord()
    
def LoadDAC():
    global VOCT_buffer,CV_ready_flag,Calibration_offset
    
    for i in range(8):
        if 14 < VOCT_buffer[i] < 4081:
            DAC.WriteDAC(i,VOCT_buffer[i]+Calibration_offset[i])
        else:
            DAC.WriteDAC(i,VOCT_buffer[i])
    CV_ready_flag = True
    
def EditCVManager():
    global Mode_Counter,Active_Chord,VOCT_STORAGE,VOCT_buffer
    
    UpdateVOCTBuffer_Normal(Mode_Counter)
    
    for i in range(8):
        VOCT_STORAGE[Active_Chord][i] = VOCT_buffer[i]
        
def Trig_Manager(): #manage trigs
    global Active_Chord, Input_Counter, freeze_flag,CLOCK_flag, random_flag, shift_trig_flag, spread_trig_flag
    global Trig_Shift_Counter, Trig_Spread_Counter, Page_Select_Counter
    
    if Input_Counter == 0: #reset trig
        rgb(1,0,0)
        Active_Chord = 0
        ResetSequenceRepeats()
        Update_Next_Active_Chord(False)
        if Sequence_Speed_Counter == True:
            UpdateNextChordPLAYSTOP()
            UpdateNextActiveDirection()
        else:
            pass
        
    elif Input_Counter == 1 and (not random_flag): #random trig
        rgb(1,0,1)
        RandomTrig()
        
    elif Input_Counter == 2: #shift trig
        rgb(0,1,0)
        shift_trig_flag = True
        Trig_Shift_Counter = getrandbits(2)
    
    elif Input_Counter == 3 and (not spread_trig_flag): #spread trig
        rgb(1,1,0)
        spread_trig_flag = True
        Trig_Spread_Counter = getrandbits(2)
    
    elif Input_Counter == 4: #freeze trig
        freeze_flag = True
        CLOCK_flag = False
        rgb(0,freeze_flag,freeze_flag)
        
    else: #pages trig
        rgb(0,0,1)
        if Page_Select_Counter[0] <= Page_Select_Counter[1]:
            Active_Chord = randint(Page_Select_Counter[0],Page_Select_Counter[1])
        else:
            Active_Chord = randint(Page_Select_Counter[1],Page_Select_Counter[0])
            
        Update_Next_Active_Chord(False)
        if Sequence_Speed_Counter == True:
            UpdateNextChordPLAYSTOP()
            UpdateNextActiveDirection()
        else:
            pass

def Trig_releasd():
    global Input_Counter, freeze_flag, TRIG_flag
    
    if Input_Counter == 4:
        freeze_flag = False
        rgb(0,0,0)
        TRIG_flag = False
    else:
        pass

def UPDATE_OUTS(flag=False):
    global VOCT_buffer,Sequence_Speed_Counter,VOCT_STORAGE,Active_Chord,Input_Counter
    
    if flag:
        for i in range(8):
            VOCT_buffer[i] = VOCT_STORAGE[Active_Chord][i]
        if 0 < Input_Counter < 4:
            applyCVchange()
        else:
            pass
        LoadDAC()
        if Sequence_Speed_Counter == False:
            pass
        else:
            SetAllPWM(VOCT_buffer)
    
    else:
        EditCVManager()
        LoadDAC()
        SetAllPWM(VOCT_buffer)
    
def Update_Calibration_Out(voltage):
    global VOCT_buffer,NOTES
    
    if voltage == 0:
        for i in range(8):
            VOCT_buffer[i] = 205
    elif voltage == 5:
        for i in range(8):
            VOCT_buffer[i] = 4095
    else:
        for i in range(8):     
            VOCT_buffer[i] = NOTES[12*voltage]
            
    LoadDAC()
    SetAllPWM(VOCT_buffer)
    
def RefreshVOCTSTORAGE():
    global Active_Chord, steps
    
    back = Active_Chord
    for i in range(steps):
        Active_Chord = i
        EditCVManager()
    Active_Chord = back
    
def applyCVchange():
    global Input_Counter,random_flag,shift_trig_flag,spread_trig_flag,Mode_Counter
    
    if Input_Counter == 1 and random_flag: #random
        if Mode_Counter == 0:
            Color_Sort_rndm()
        else:
            Color_Sort_rndm(False)
            
    elif Input_Counter == 2 and shift_trig_flag: #shift
        ShiftChord_Trig(Mode_Counter)
        
    elif Input_Counter == 3 and spread_trig_flag: #spread
        if Mode_Counter == 0:
            SpreadChord(True)
        elif Mode_Counter == 1:
            ChordMode_SpreadTrig(1)
        else:
            spread_trig_flag = False
    else:
        pass


################################################################################################################################################################
### CORE --LEDs-- FUNCTIONS


def rgb(r,g,b): #rgb led
    red.value(not r)
    green.value(not g)
    blue.value(not b)
    
def rgb_off():
    rgb(0,0,0)
    
def UpdateRGB():
    global Input_Counter
    
    if Input_Counter == 0:
        rgb(1,0,0)
    elif Input_Counter == 1:
        rgb(1,0,1)
    elif Input_Counter == 2:
        rgb(0,1,0)
    elif Input_Counter == 3:
        rgb(1,1,0)
    elif Input_Counter == 4:
        rgb(0,1,1)
    else:
        rgb(0,0,1)


################################################################################################################################################################
#PIO set-up and functions


@rp2.asm_pio(out_init=rp2.PIO.OUT_LOW, set_init=rp2.PIO.OUT_LOW, sideset_init=rp2.PIO.OUT_LOW)
def advance_demux(): # sideset == A0 // set == A1 // out == A2
    set(x,1)
    wait(1,gpio,9)
    
    wrap_target()
    
    mov(osr,null)
    out(pins,32) 
    set(pins,0)  .side(0) [5] #000
    set(pins,0)  .side(1) [7] #001
    set(pins,1)  .side(0) [7] #010
    set(pins,1)  .side(1) [7] #011
    mov(osr,x)
    out(pins,32) 
    set(pins,0)  .side(0) [5] #100
    set(pins,0)  .side(1) [7] #101
    set(pins,1)  .side(0) [7] #110
    set(pins,1)  .side(1) [7] #111
    
    wrap()
    
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def pwm_demux():
    set(pins,1)
    wait(1,gpio,6)
    set(pins,0)
    jmp('start')
    
    ###
    
    label('high_1')
    set(pins,1)
    nop()        [31]
    jmp('h1_back')
    label('high_2')
    set(pins,1)
    nop()        [31]
    jmp('h2_back')
    
    ###
    
    wrap_target()
    label('start')
    
    pull(noblock)
    mov(x,osr)
    set(y,3)
    
    label('repeat')
    mov(isr,y)
    
    out(y,4)
    label('h1_back')
    jmp(y_dec,'high_1')
    
    set(pins,0)
    
    wait(1,gpio,6)
    
    out(y,4)
    label('h2_back')
    jmp(y_dec,'high_2')
    
    set(pins,0)
    
    wait(0,gpio,6)
    mov(y,isr)
    jmp(y_dec,'repeat')
    
def SetAllPWM(a=[0,0,0,0,0,0,0,0]):
    tx_data = int(
        ((a[7]>>8)<<28)|
        ((a[6]>>8)<<24)|
        ((a[5]>>8)<<20)|
        ((a[4]>>8)<<16)|
        ((a[3]>>8)<<12)|
        ((a[2]>>8)<<8) |
        ((a[1]>>8)<<4) |
        ((a[0]>>8)))
    
    pwm_sm.put(tx_data)
    
rp2.PIO(0).remove_program()
rp2.PIO(1).remove_program()
control_sm = rp2.StateMachine(1, advance_demux, freq=20000, out_base=Pin(8), set_base=Pin(7), sideset_base=Pin(6))
pwm_sm = rp2.StateMachine(4, pwm_demux, freq=2000000, set_base=Pin(9))

control_sm.active(1)
pwm_sm.active(1)


################################################################################################################################################################
#Interrupt (Clock) set-up and functions


def clock_handler(pin):
    global CLOCK_flag,freeze_flag
    
    if not freeze_flag:
        CLOCK_flag = True
    else:
        pass
        

CLKIN.irq(handler=None,trigger=Pin.IRQ_RISING)


################################################################################################################################################################
#Set-up Code   
    
rgb(0,0,0)
PSLED.value(False)
LoadCalibrationSettings()
LoadScene(1)
RefreshVOCTSTORAGE()
screen_saver_timer.init(mode = Timer.PERIODIC, period = screen_saver_interval, callback = screen_saver_increment)
gc.collect()
MainMenu(False)
fb = framebuf.FrameBuffer(bytearray(oled.buffer),128,64,framebuf.MONO_VLSB)
oled.fill(0)
for i in range(10):
    draw.circle(64,32,i,1)
    oled.show()
for i in range(30):
    oled.blit(fb,0,0)
    d = int(((i+1)/30)*74)
    #erasing
    oled.fill_rect(0,0,64-d,64,0)
    oled.fill_rect(64+d,0,64-d,64,0)
    oled.fill_rect(64-d,0,2*d,32-d,0)
    oled.fill_rect(64-d,32+d,2*d,32-d,0)
    #circle
    for j in range(10):
        draw.circle(64,32,d+j,1)
    oled.show()

#finish
oled.fill(0)
MainMenu()

################################################################################################################################################################
#Loop Code


while True:
    
    if ps_menu_flag:
        if TRIGIN.value() and not TRIG_flag:
            TRIG_flag = True
            Trig_Manager()
        elif TRIG_flag and not TRIGIN.value():
            Trig_releasd()
        else:
            pass
        
        if not CLOCK_flag:
            pass
        else:
            UPDATE_OUTS(True)
            rgb(0,0,0)
            if not Sequence_Speed_Counter:
                pass
            else:
                oled.show()
            Update_Next_Active_Chord(True)
            TRIG_flag = False
            CLOCK_flag = False
            if Sequence_Speed_Counter == True:
                UpdateNextChordPLAYSTOP()
                UpdateNextActiveDirection()
            else:
                pass
        
    if (tb_flag and not ps_menu_flag) or (PSIN.value() and tb_flag):
        if PSIN.value():
            tb_trigger(True)
            ps_menu_flag = not ps_menu_flag
            PSLED.value(ps_menu_flag)
            rgb_off()
            Calibration_offset = CO_buffer
            RefreshVOCTSTORAGE()
            Selection_Timer.deinit()
            screen_saver_timer.deinit() #disable screen saver
            select_flag = False
            Active_Chord = 0
            if ps_menu_flag:
                if Sequence_Speed_Counter == True:
                    PSMenu()
                else:
                    oled.fill(0)
                oled.show()
                Update_Next_Active_Chord(True)
                if Sequence_Speed_Counter == True:
                    UpdateNextChordPLAYSTOP()
                    UpdateNextActiveDirection()
                else:
                    SetAllPWM()
                CLKIN.irq(handler=clock_handler,trigger=Pin.IRQ_RISING) #enable clock interrupt
            else:
                ResetFlags()
                CLKIN.irq(handler=None,trigger=Pin.IRQ_RISING) #disable clock interrupt
                Active_Chord = 0
                Page = ceil((Active_Chord+1)/8)-1
                screen_saver_count = 0
                screen_saver_timer.init(mode = Timer.PERIODIC, period = screen_saver_interval, callback = screen_saver_increment)
                MainMenu()
            
        else:
            pass
        
        if not ps_menu_flag: #in the main menu and other sub-menus
            gc.collect()
            if not Center.value() and (not screen_saver_flag):
                tb_trigger(False)
                Selection_Manager()
                oled.show()
            
            elif not Up.value():
                Reset_Screen_Saver_Count()
                if select_flag:
                    Update_Manager(1)   
                else:
                    tb_trigger(True)
                    Move_Up()
                oled.show()
                    
            elif not Down.value():
                Reset_Screen_Saver_Count()
                if select_flag:
                    Update_Manager(0)
                else:
                    tb_trigger(True)
                    Move_Down()
                oled.show()
                
            elif not Left.value():
                Reset_Screen_Saver_Count()
                if not select_flag:
                    tb_trigger(True)
                    Move_Left() 
                else:
                    pass
                oled.show()
                
            elif not Right.value():
                Reset_Screen_Saver_Count()
                if not select_flag:
                    tb_trigger(True)
                    Move_Right()
                else:
                    pass
                oled.show()
            else:
                pass
            
            if not EDIT_CV_ready_flag:
                UPDATE_OUTS()
                RefreshVOCTSTORAGE()
                EDIT_CV_ready_flag = True
            else:
                pass
        else: 
            pass   
    else:
        pass