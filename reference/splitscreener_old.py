#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 20:32:04 2022

@author: brunoreis
"""

class Canvas:
    def __init__(self,width: int = 1920,height: int = 1080):
        self.width = width,
        self.height = height

class Grid:
    
    def __init__(self,
                 canvas: Canvas(),
                 columns: int = 12,
                 rows: int = 6,
                 margin_top: int = 30,
                 margin_bottom: int = 30,
                 margin_left: int = 30,
                 margin_right: int = 30,
                 gutter: int = 15,
                 ):
        self.columns = columns,
        self.rows = rows,
        self.margin_top = margin_top,
        self.margin_bottom = margin_bottom,
        self.margin_left = margin_left,
        self.margin_right = margin_right,
        self.gutter = gutter
        
    def __post_init__(self):
        self.column_width = (self.canvas.width - 
                             self.margin_left - 
                             self.margin_right -
                             (self.columns-1) * self.gutter) / self.columns
        self.row_height = (self.canvas.height - 
                             self.margin_top - 
                             self.margin_bottom -
                             (self.rows-1) * self.gutter) / self.rows
        
    

class Screen:
    
    def __init__(self,
                 grid: Grid(),
                 colspan: int = 6,
                 rowspan: int = 3,
                 colx: float = 1,
                 coly: float = 1):
        self.colspan = colspan
        self.rowspan = rowspan
        self.colx = colx
        self.coly = coly
      
        # CALCULAR O TAMANHO DAS COISASSS
    # def __post_init__(self):
    #     self.width = width
    #     self.height = height
    #     self.x = x
    #     self.y = y
        
    def __str__(self):
        return f"Width: {self.width}\nHeight: {self.height}\nCenter.X: {self.x}\nCenter.Y: {self.y}"
     
    #Retrieve values
    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def get_dimensions(self):
        return (self.get_width(), self.get_height())

    def get_position(self):
        return (self.get_x(), self.get_y())

    def get_properties(self):
        return {'Width': self.get_width(),
                'Height': self.get_height(),
                'Center.X': self.get_x(),
                'Center.Y': self.get_y()}
    
    #Set new values
    def set_width(self, width: float):
        self.width = width
        
    def set_height(self, height: float):
        self.height = height
        
    def set_x(self, x: float):
        self.x = x
        
    def set_y(self, y: float):
        self.y = y
        

screen = Screen()        

print(screen.get_properties())
    
screen.set_y(.25)

print(screen.y)
