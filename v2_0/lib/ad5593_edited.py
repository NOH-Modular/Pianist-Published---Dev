###############################################################
###                                                         ###
###            MicroPython AD5593 ADC/DAC/GPIO I2C          ###
###             Library created by Tristan Muller           ###
###                 https://101robotics.com                 ###
###    Inspired by the library  created for the PCF8574     ###
###     https://github.com/mcauser/micropython-pcf8574      ###
###                                                         ###
###############################################################

### Copyright 2021 Tristan Muller
### THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
### EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
### MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
### IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM
### DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
### ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
### DEALINGS IN THE SOFTWARE.

###############################################################
###                                                         ###
###                         CHANGELOG                       ###
###     18/05/2020: v0.1: Creation of th lib with ADC and   ###
###                 GPIO outputs capabilites                ###
###                                                         ###
###############################################################

### Keywords :
AD5593_ALL = 0
AD5593_ADC = 1
AD5593_DAC = 2
AD5593_OUTPUT = 3
AD5593_INPUT  = 4

##### POINTER BYTE CONSTANTS :
### Mode bits :
AD5593_CONFIG_MODE  = 0b0000 << 4
AD5593_DAC_WRITE    = 0b0001 << 4
AD5593_ADC_READBACK = 0b0100 << 4
AD5593_DAC_READBACK = 0b0101 << 4
AD5593_GPIO_READBACK= 0b0110 << 4
AD5593_REG_READBACK = 0b0111 << 4

### Control Register : (Descriptions from the datasheet)
AD5593_NOP           = 0b0000      # No operation
AD5593_ADC_SEQ_REG   = 0b0010      # Selects ADC for conversion (1 byte blank and 1 for the 8 I/Os)
AD5593_GP_CONTR_REF  = 0b0011      # DAC and ADC control register
AD5593_ADC_PIN_CONF  = 0b0100      # Selects which pins are ADC inputs
AD5593_DAC_PIN_CONF  = 0b0101      # Selects which pins are DAC outputs
AD5593_PULLDOWN_CONF = 0b0110      # Selects which pins have an 85kOhms pull-down resistor to GND
AD5593_LDAC_MODE     = 0b0111      # Selects the operation of the load DAC
AD5593_GPIO_W_CONF   = 0b1000      # Selects which pins are general-purpose outputs
AD5593_GPIO_W_DATA   = 0b1001      # Writes data to general-purpose outputs
AD5593_GPIO_R_CONF   = 0b1010      # Selects which pins are general-purpose inputs
AD5593_PWRDWN_REFCONF= 0b1011      # Powers down the DACs and enables/disables the reference
AD5593_OPENDRAIN_CONF= 0b1100      # Selects open-drain or push-pull for general-purpose outputs
AD5593_3_STATES_PINS = 0b1101      # Selects which pins are three-stated
AD5593_SOFT_RESET    = 0b1111      # Resets the AD5593R
AD5593_BLANK         = 0b00000000  # For a blank MSB or LSB
AD5593_FULL          = 0b11111111  # For a full MSB or LSB

class AD5593:
    def __init__(self, i2c, address=0x11,advance=0):
        self._i2c = i2c
        self._address = address
        self._data = bytearray(3)
        self._advance = advance
        if i2c.scan().count(address) == 0:
            raise OSError('AD5593 not found at I2C address {:#x}'.format(address))

    def writeRegister(self, reg, msb, lsb):
        self._data[0] = reg   #Pointer Byte
        self._data[1] = msb   #MSB
        self._data[2] = lsb   #LSB
        self._write()

    def readValues(self):
        return self._i2c.readfrom(self._address,2)

    def _read(self,reg=AD5593_BLANK,nbBytes=2):
        self._i2c.writeto(self._address, bytearray(reg))
        return self._i2c.readfrom(self._address,nbBytes)

    def _write(self):
        self._i2c.writeto(self._address, self._data)
        
    def validate(self, val, a, b):
        if not a <= val <= b:
            raise ValueError('Invalid input {}. Use {}-{}.'.format(val,a,b))
        return val
    
### CONFIGURING THE AD5593
    
    def SetIntRef(self,state):
        state = self.validate(state,0,1)
        if state: #internal Reference turned on
            self.writeRegister(AD5593_CONFIG_MODE | AD5593_PWRDWN_REFCONF, 0x02, AD5593_BLANK)
        else:     #internal Reference turned off
            self.writeRegister(AD5593_CONFIG_MODE | AD5593_PWRDWN_REFCONF, AD5593_BLANK, AD5593_BLANK)
            
    def SetDACRefGain(self, gain):
        gain = self.validate(gain,1,2)
        if gain is 1:  #gain set to 1xVref
            self.writeRegister(AD5593_CONFIG_MODE | AD5593_GP_CONTR_REF, AD5593_BLANK, AD5593_BLANK)
        else:          #gain set to 2xVref
            self.writeRegister(AD5593_CONFIG_MODE | AD5593_GP_CONTR_REF, AD5593_BLANK, 0x10)
        
    def SetAllDAC(self):
        self.writeRegister(AD5593_CONFIG_MODE | AD5593_DAC_PIN_CONF, AD5593_BLANK, AD5593_FULL)
        
    def SetLDAC(self,val):
        val = self.validate(val,0,2)
        if val is 1:   #DAC output does not update, only the input register
            self.writeRegister(AD5593_CONFIG_MODE | AD5593_LDAC_MODE, AD5593_BLANK, 0x01)
            
        elif val is 2: #all the DAC outputs update, then the LDAC goes to the '1' mode
            self.writeRegister(AD5593_CONFIG_MODE | AD5593_LDAC_MODE, AD5593_BLANK, 0x02)
            
        else:          #DAC output updates as soon as new data is transferred
            self.writeRegister(AD5593_CONFIG_MODE | AD5593_LDAC_MODE, AD5593_BLANK, AD5593_BLANK)
            
### WRITING TO THE AD5593
        
    def WriteDAC(self,pin,val):
        pin = self.validate(pin,0,7)
        val = self.validate(val,0,4095)
        MSBLSB = (((1<<15) | (pin<<12)) | val)
        self.writeRegister((AD5593_DAC_WRITE | pin),(MSBLSB>>8),(MSBLSB-((MSBLSB>>8)<<8)))
