# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 10:46:31 2023

@author: mjhar
FUNCTION FOR CHANGING END OF DATA FOLDER TO ']' << STILL WORKING ON MAKING THIS SEPARATE FILE, CURRENT HAVING AN ISSUE (6/24/23)
"""

import os

def endBracket(directory,file):
    with open(os.path.join(directory,file),'r') as f:
        fileData = f.readlines()
        
    replaceVar = list(fileData[0])
    replaceVar[-1] = ']'
    new_file = "".join(replaceVar)
    
    with open(os.path.join(directory,file),'w') as f:
        f.writelines(new_file)
