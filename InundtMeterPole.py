#
#
#
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class ImageObject:
    def __init__(self, FILE, CANVAS ): 
        self.thisImage = Image.open( FILE ).convert('RGBA')
        self.CANVAS = CANVAS

    def Resize(self, SIZE_PERC):
        wh = (SIZE_PERC*np.array( self.thisImage.size )).astype( np.int16 ) 
        #import pdb ; pdb.set_trace()
        self.thisImage = self.thisImage.resize( (wh[0],wh[1]), Image.Resampling.LANCZOS )

    def Paste(self, AT_W, AT_H, normalized=True, centroid=False ): 
        ''' reference point is Upper-Left, otherwise 'centroid' is True  '''
        wc,hc = self.CANVAS.size
        wi,hi = self.thisImage.size 
        if normalized:
            AT_W = int(AT_W*wc) 
            AT_H = int(AT_H*hc) 
        if centroid:
            AT_W = int(wc/2 - wi/2) 
            AT_H = int(hc/2 - hi/2)
        self.CANVAS.alpha_composite( self.thisImage , (AT_W,AT_H) )

class InundatMeter:
    def __init__(self, DTM ):
        self.DTM = DTM
        self.POLE = 12.0  # meter
        self.PEA_METER = 1.75  # meter from ground
        self.MSL_METER = DTM + self.PEA_METER

        self.CANVAS_UPPER = 0.040
        self.CANVAS_LOWER = 0.875
        self.NORM_METER = (self.CANVAS_LOWER-self.CANVAS_UPPER)/self.POLE  # pixel per meter

        PIC_DIR = Path( r'./pics/' )
        self.Canvas = Image.new("RGBA",  (427,1260), (255,255,255,255) )

        ImageFont.load_default(size=12)
        self.DRAW = ImageDraw.Draw( self.Canvas )

        elect_pole = ImageObject( PIC_DIR / 'PEA_Pole.png', self.Canvas )
        elect_pole.Paste( 0.5, 0.5, centroid=True ) 
        #import pdb ; pdb.set_trace()
        self.green_meter = ImageObject( PIC_DIR/'WattHourMeter_GREEN.png', self.Canvas )
        self.green_meter.Resize( 0.15 )

        self.red_meter = ImageObject( PIC_DIR/'WattHourMeter_RED.png', self.Canvas )
        self.red_meter.Resize( 0.15 )

        if 0: # test
            self.green_meter.Paste( 0.5, self.CANVAS_UPPER  )
            self.red_meter.Paste( 0.5, self.CANVAS_LOWER  )
        
    def PlotLevel(self, TEXT, AT_MSL, color ):
        "draw line and text at specified level"
        def Calc_row( AT_MSL ):   # normalized!
            #import pdb ; pdb.set_trace()
            return self.CANVAS_LOWER-self.NORM_METER*(AT_MSL-self.DTM)
        row_norm = Calc_row(AT_MSL)
        at_hei = int( self.Canvas.size[1]*row_norm )
        self.DRAW.line( [ (10,at_hei), (250,at_hei) ], fill=color, width=5 ) 
        self.DRAW.text( ( 10,at_hei), f'{TEXT}={AT_MSL:+.2f}m.', fill=color, font_size=32 )
        return at_hei,row_norm 

    def WetMeter(self, FLOOD_LEVEL ):
        assert self.MSL_METER<=FLOOD_LEVEL
        self.PlotLevel( 'DTM', self.DTM, 'brown' ) 
        at_hei,row_norm = self.PlotLevel( 'PEA', self.PEA_METER+self.DTM, 'red' ) 
        #import pdb ; pdb.set_trace()
        self.red_meter.Paste( 0.55, row_norm )
        at_hei,row_norm = self.PlotLevel( 'FLOOD', FLOOD_LEVEL, 'blue' ) 
        self.green_meter.Paste( 0.55, row_norm )

    def DryMeter(self, FLOOD_LEVEL ):
        assert self.MSL_METER>=FLOOD_LEVEL
        self.PlotLevel( 'DTM', self.DTM, 'brown' ) 
        at_hei,row_norm = self.PlotLevel( 'PEA', self.PEA_METER+self.DTM, 'green' ) 
        self.green_meter.Paste( 0.55, row_norm )
        self.PlotLevel( 'FLOOD', FLOOD_LEVEL, 'blue' ) 
        #import pdb ; pdb.set_trace()

    def show(self):
        self.Canvas.show()

    def save(self, DIAGRAM ):
        self.Canvas.save( DIAGRAM )

############################################################################
if __name__ == '__main__':
    im = InundatMeter( DTM=200)
    im.WetMeter( 205.4 )
    print('Writing "DiagramWetMeter.png" ...')
    im.save( "DiagramWetMeter.png")
    ##########################################
    im = InundatMeter( DTM=300)
    im.DryMeter( FLOOD_LEVEL=301.1 )
    print('Writing "DiagramDryMeter.png" ...')
    im.save( "DiagramDryMeter.png")
