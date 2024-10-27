#
# Script Name: InundtMeter.py
# Description: Draw a diagram of a 'wet' or 'dry' wattmeter installed at a height
#              of 1.75 meters off the ground. Also, show a scenario where
#              the wattmeter should be elevated.
# Author: P.Santitamnont (phisan.s@cdg.co.th, phisan.chula@gmai.com )
# Version: 0.5 
# Date:  2024-Oct-27
#     
#
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class ImageObject:
    def __init__(self, FILE, CANVAS, centroid=False ): 
        self.thisImageCNTR = centroid
        self.thisImage = Image.open( FILE ).convert('RGBA')
        self.CANVAS = CANVAS

    def Resize(self, SIZE_PERC):
        wh = (SIZE_PERC*np.array( self.thisImage.size )).astype( np.int16 ) 
        self.thisImage = self.thisImage.resize( (wh[0],wh[1]), Image.Resampling.LANCZOS )

    def Paste(self, AT_W, AT_H, normalized=True ): 
        ''' reference point is Upper-Left, otherwise 'centroid' is True  '''
        wc,hc = self.CANVAS.size
        wi,hi = self.thisImage.size 
        if normalized:
            AT_W = int(AT_W*wc) 
            AT_H = int(AT_H*hc) 
        if self.thisImageCNTR:
            AT_W = AT_W - int(wi/2) 
            AT_H = AT_H - int(hi/2)
        self.CANVAS.alpha_composite( self.thisImage , (AT_W,AT_H) )
        #import pdb ; pdb.set_trace()

class InundatMeter:
    def __init__(self, DTM ):
        self.DTM = DTM
        self.POLE = 12.0  # meter
        self.PEA_METER = 1.75  # meter from ground
        self.MSL_METER = DTM + self.PEA_METER

        self.CANVAS_UPPER = 0.040
        self.CANVAS_LOWER = 0.875
        self.X_METER     = 0.72

        self.NORM_METER = (self.CANVAS_LOWER-self.CANVAS_UPPER)/self.POLE  # pixel per meter

        PIC_DIR = Path( r'./pics/' )
        self.Canvas = Image.new("RGBA",  (427,1260), (255,255,255,255) )
        self.NP_ARR = np.array(self.Canvas)

        ImageFont.load_default(size=12)
        self.DRAW = ImageDraw.Draw( self.Canvas )

        elect_pole = ImageObject( PIC_DIR / 'PEA_Pole_GRAY.png', self.Canvas )
        elect_pole.Paste( 0.0, 0.0 ) 
        #import pdb ; pdb.set_trace()
        self.green_meter = ImageObject( PIC_DIR/'WattHourMeter_GREEN.png', self.Canvas, centroid=True )
        self.green_meter.Resize( 0.15 )

        self.red_meter = ImageObject( PIC_DIR/'WattHourMeter_RED.png', self.Canvas, centroid=True )
        self.red_meter.Resize( 0.15 )

        self.PlotLevel( 'DTM', self.DTM, 'brown', lw=10 ) 
        
    def MSL_NORM( self, MSL ):  # normalized!
        return self.CANVAS_LOWER-self.NORM_METER*(MSL-self.DTM)

    def PlotLevel(self, TEXT, AT_MSL, color, lw=5 ):
        "draw line and text at specified level"
        def Calc_row( AT_MSL ):   # normalized!
            return self.CANVAS_LOWER-self.NORM_METER*(AT_MSL-self.DTM)
        row_norm = Calc_row(AT_MSL)
        at_hei = int( self.Canvas.size[1]*row_norm )
        self.DRAW.line( [ (10,at_hei), (250,at_hei) ], fill=color, width=lw ) 
        self.DRAW.text( ( 10,at_hei), f'{TEXT}={AT_MSL:+.2f}m.', fill=color, font_size=24 )
        return at_hei,row_norm 

    def WetMeter(self, FLOOD_LEVEL ):
        assert self.MSL_METER<=FLOOD_LEVEL
        hei_PEA,row_norm = self.PlotLevel( 'PEA', self.PEA_METER+self.DTM, 'red' ) 
        self.red_meter.Paste( self.X_METER, row_norm )
        hei_FLD,row_norm = self.PlotLevel( 'FLOOD', FLOOD_LEVEL, 'blue' ) 
        self.green_meter.Paste( self.X_METER, row_norm )
        #import pdb ; pdb.set_trace()
        self.DRAW.line( [ (350,hei_PEA), (350,hei_FLD ) ], fill='green', width=10 ) 
        def DrawArrow( xy ):
            x,y = xy; s = 20
            self.DRAW.line( [ (x,y), (x-s,y+s) ], fill='green', width=10 ) 
            self.DRAW.line( [ (x,y), (x+s,y+s) ], fill='green', width=10 ) 
        DrawArrow( ( 350,hei_FLD ) )
        UP_OFF = FLOOD_LEVEL-self.MSL_METER
        MID = self.MSL_NORM( (FLOOD_LEVEL + self.MSL_METER)/2 ) *  self.Canvas.size[1]
        self.DRAW.text( ( 190, MID ), f'UP={UP_OFF:+.2f}m.', fill='green', font_size=24 )

    def DryMeter(self, FLOOD_LEVEL ):
        assert self.MSL_METER>=FLOOD_LEVEL
        at_hei,row_norm = self.PlotLevel( 'PEA', self.PEA_METER+self.DTM, 'green' ) 
        self.green_meter.Paste( 0.55, row_norm )
        self.PlotLevel( 'WATER', FLOOD_LEVEL, 'blue' ) 
        #import pdb ; pdb.set_trace()

    def show(self):
        self.Canvas.show()

    def save(self, DIAGRAM ):
        self.Canvas.save( DIAGRAM )

############################################################################
if __name__ == '__main__':
    if 1:
        im = InundatMeter( DTM=200)
        im.WetMeter( 205.4 )
        print('Writing "DiagramWetMeter.png" ...')
        im.save( "DiagramWetMeter.png")
    ##########################################
    if 1:
        im = InundatMeter( DTM=300)
        im.DryMeter( FLOOD_LEVEL=301.1 )
        print('Writing "DiagramDryMeter.png" ...')
        im.save( "DiagramDryMeter.png")
