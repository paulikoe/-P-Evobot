

class StepperDriver:
    
    def __init__(self):
        """
        This method initialize the stepper driver object.
        """
        self.status = 0
        
    def updateStatus(self, status):
        """
        This method updates the status of the stepper driver.
        """
        self.status = status
        
    def isSwPressed(self):
        """
        This method returns the status of the switch.
        """
        if (self.getSwF() == 1):
            return True
        return False
        
    def isMotorTurning(self):
        """
        This method returns True if the motor is turning.
        """
        if (self.getMotStatus()==0 or self.getHiZ() == 1):
            return False
        return True
    
    def isError(self):
        error, msg = self.analyseStatus()
        return error
        
    def getStepLoss(self):
        step_loss = ((self.status>>13)&3)
        return step_loss
    
    def getOCD(self):
        ocd = (self.status>>12)&1 #bit 12
        return ocd
    
    def getThSd(self):
        th_sd = (self.status>>11)&1 #bit 11
        return th_sd
    
    def getThWrn(self):
        th_wrn = (self.status>>10)&1 #bit 10
        return th_wrn
    
    def getUVLO(self):
        uvlo = (self.status>>9)&1 #bit 9
        return uvlo
    
    def getWrongCmd(self):
        wrong_cmd = (self.status>>8)&1 #bit 8
        return 
    
    def getNotPerfCmd(self):
        not_perf_cmd = (self.status>>7)&1 #bit 7
        return not_perf_cmd
    
    def getMotStatus(self):
        mot_status = (self.status>>5)&3 #bits 6 and 5
        return mot_status
    
    def getSwEvn(self):
        sw_evn = (self.status>>3)&1 #bits 3
        return sw_evn
    
    def getSwF(self):
        sw_f = (self.status>>2)&1 #bit 2
        return sw_f
    
    def getBusy(self):
        busy = (self.status>>1)&1 #bit 1
        return busy
        
    def getHiZ(self):
        hiz = (self.status)&1 #bit 0
        return hiz
    

        
    def printStatus(self, onlyErrors = False):
        error, msg = self.analyseStatus()
        if(onlyErrors is True):
            if(error is True):
                print (msg)
        else:
             print (msg)   
        
    def analyseStatus(self):
        error = False
        message = ""
        step_loss = self.getStepLoss()
        if( step_loss != 3):
            message +="step_loss="
            message +=str(step_loss)
            error = True

        if(self.getOCD() == 0):
            message +=" OCD "
            error = True
            
        if(self.getThSd() == 0):
            message +=" TH_SD "
            error = True

        if(self.getThWrn() == 0):
            message +=" TH_WRN "
            error = True

        if (self.getUVLO() == 0):
            message +=" UVLO "
            error = True

        if(self.getWrongCmd() == 1):
            message +=" WRONG_CMD "
            error = True

        if(self.getNotPerfCmd() == 1):
            message +=" NOT_PERF_CMD "
            error = True

        if(self.getSwEvn() == 1):
            message +=" SW_EVN "
            error = True

        if(self.getSwF() == 1):
            message +=" SW_PRESSED "
            error = True

        
    
        message += "MOT_STATUS="
        mot_status = self.getMotStatus()
        if (mot_status == 0):
            message +="STOP"
        if (mot_status == 1):
            message +="ACC"
        if (mot_status == 2):
            message +="DEC"
        if (mot_status == 3):
            message +="C_SPEED"

        if(self.getBusy() == 0):
            message +=" BUSY "
	
        if(self.getHiZ() == 1):
            message +=" HIZ "

        return error, message
        
