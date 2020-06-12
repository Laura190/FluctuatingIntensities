#Retrive credentials. 
  
from cryptography.fernet import Fernet 
import os 
  
cred_filename = '/storage/maths/masqhp/WMS/OmeroTest/CredFile.ini'
key_file = '/storage/maths/masqhp/WMS/OmeroTest/key.key'
  
key = '' 
  
with open(key_file,'r') as key_in: 
    key = key_in.read().encode() 
  
#If you want the Cred file to be of one  
# time use uncomment the below line 
#os.remove(key_file) 
  
f = Fernet(key) 
with open(cred_filename,'r') as cred_in: 
    lines = cred_in.readlines() 
    config = {} 
    for line in lines: 
        tuples = line.rstrip('\n').split('=',1) 
        if tuples[0] in ('Username','Password'): 
            config[tuples[0]] = tuples[1] 
  
    passwd = f.decrypt(config['Password'].encode()).decode()
    usernm = config['Username']

