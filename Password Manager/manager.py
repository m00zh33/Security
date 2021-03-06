#!/usr/bin/python

"""

Objective: The password file is encrypted with the public key and the private key
is encrypted with a password. The password from input decrypts the private
key which in turn decrypts the password file

The account needed is given as a parameter and the password is parsed from
the password file. The password is then pasted to clipboard

Reference: https://medium.com/@ismailakkila/black-hat-python-encrypt-and-decrypt-with-rsa-
cryptography-bd6df84d65bc

The encryption code is generic and taken from online resource (above).

"""

from key_gen import Generator
from Crypto.Cipher import AES
from passlib.hash import pbkdf2_sha256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import bcrypt
import getpass
import sys
import struct
import base64
import gzip
import zlib
import optparse
import time
import os
import pyperclip
import pygame
import random

def decrypt_key(edit,view,account):
   
    passwd = getpass.getpass("Enter Password: ")
    
    hash2 = "$2a$12$hLiCfiMkJQcIt.h9zw4pXOCiWQXw4.Nv4m1alSKrhuaUVZ08AcVGS"
  
    if (hash2 == bcrypt.hashpw(str(passwd),hash2)) == False:
        print "[!] Incorrect password. Goodbye."
        sys.exit()

    plaintext = ''

    with open("private_key.pem.e",'rb') as ciphertext:

        size = struct.unpack('<Q',ciphertext.read(struct.calcsize('Q')))[0]
        iv = ciphertext.read(16)

        decryptor = AES.new(passwd,AES.MODE_CBC,iv)

        while True:
            
            chunks = ciphertext.read(24*1024)
            if len(chunks) == 0:
                break
            elif len(chunks) % 16 != 0:
                chunks += ' ' * (16 - len(chunks) % 16)

            plaintext += decryptor.decrypt(chunks)
        
        plaintext = plaintext[:int(size)]

    with open("passwords.enc","rb") as ciphertext:
        passwords_enc = ciphertext.read()

    private_key = RSA.importKey(plaintext)

    private_key = PKCS1_OAEP.new(private_key)

    chunk_size = 512
    offset = 0
    decrypted = ""

    passwords_enc = base64.b64decode(passwords_enc)

    while offset < len(passwords_enc):

        chunk = passwords_enc[offset:offset+chunk_size]
        decrypted += private_key.decrypt(chunk)
        offset += chunk_size

    passwords = zlib.decompress(decrypted)

    if view:
         
        with open("temporary","wb") as fobj:
            fobj.write(passwords)

        with open("temporary", "rb") as fobj:
            lines = fobj.read().splitlines()
        
        count = 0

        for i in range(len(lines)):

            check_list = lines[i].split(":")

            if account == check_list[0]:

                account_info = lines[i].split(":")
                count += 1
                
        if count != 1:
            print "[!] Aww, gee, you got me there, Rick."
            sys.exit()

        pyperclip.copy(account_info[2])
        account_passwd = pyperclip.paste()
        
        audio_seeks = {
                1:"./Audio/Hi_I'm_mr_meeseeks_look_at_me.wav",
                2:"./Audio/Oooo_yeah__caaan_doo!.wav",
                3:"./Audio/stickler.mp3",
                4:"./Audio/woo_vu_luvub_dub_dub.wav",
                5:"./Audio/yessir.mp3"
                }

        audio_num = random.randint(1,5)

        pygame.init()

        pygame.mixer.music.load(audio_seeks[audio_num])
        pygame.mixer.music.play()

        time.sleep(30)
        pyperclip.copy("WUBBA LUBBA DUB DUBS!!!")
        clear_passwd = pyperclip.paste()
        os.system("shred temporary")
        time.sleep(1)
        os.system("rm temporary")

        print "[*] Meeseeks don't usually have to exist for this long. It's gettin' weeeiiird.."

    
    if edit:
        with open("passwords","wb") as fobj:
            fobj.write(passwords)


def encrypt_file():

    test = Generator()
    test.RSA_encrypt("passwords")
    time.sleep(2)
    print "[*] Saving new password file..."
    os.system("shred passwords")
    time.sleep(2)
    os.system("rm passwords")
    print "Done."

def main():

    parser = optparse.OptionParser("usage: %prog" + " --view [view passwords] --account [specify account] --edit [edit passwords]")
    parser.add_option("--view",action="store_true",dest="view",default=False,help="to view passwords use --view")
    parser.add_option("--account",dest="account",type="string",help="to view account use --account")
    parser.add_option("--edit",action="store_true",dest="edit",default=False,help="to edit passwords use --edit")
    parser.add_option("--encrypt",action="store_true",dest="encrypt",default=False,help="encrypt file")

    (options,args) = parser.parse_args()
    view = options.view
    edit = options.edit
    encrypt = options.encrypt
    account = options.account

    if view or edit:
        decrypt_key(edit,view,account)
    elif encrypt:
        encrypt_file()
    else:
        parser.error("[!] Please select an option")



main()


