import imghdr
import struct
import os,glob
import imageio


def image2DogDislay(image):
  image = image.transpose(1,0)
  data = list()
  for line in range(0,4):
    y = 8*line
    for col in range(0,32):
      newByte = 0
      for b in range(0,8):
        pixel = (image[col,y+b] & 1)<<b
        newByte |= pixel
      data.append(newByte^255)
  return(data)

def printImageInfos(bmpFile):
  bmp = open(picFile, 'rb')
  print('Type:', bmp.read(2).decode())
  print('Size: %s' % struct.unpack('I', bmp.read(4)))
  print('Reserved 1: %s' % struct.unpack('H', bmp.read(2)))
  print('Reserved 2: %s' % struct.unpack('H', bmp.read(2)))
  print('Offset: %s' % struct.unpack('I', bmp.read(4)))
  print('DIB Header Size: %s' % struct.unpack('I', bmp.read(4)))
  print('Width: %s' % struct.unpack('I', bmp.read(4)))
  print('Height: %s' % struct.unpack('I', bmp.read(4)))
  print('Colour Planes: %s' % struct.unpack('H', bmp.read(2)))
  print('Bits per Pixel: %s' % struct.unpack('H', bmp.read(2)))
  print('Compression Method: %s' % struct.unpack('I', bmp.read(4)))
  print('Raw Image Size: %s' % struct.unpack('I', bmp.read(4)))
  print('Horizontal Resolution: %s' % struct.unpack('I', bmp.read(4)))
  print('Vertical Resolution: %s' % struct.unpack('I', bmp.read(4)))
  print('Number of Colours: %s' % struct.unpack('I', bmp.read(4)))
  print('Important Colours: %s' % struct.unpack('I', bmp.read(4)))
  bmp.close()
  

def compressImage(picRaw):
  picComp = list()
  oldByte = -1
  sameCounter = 0
  for p in picRaw:
    if p==0 or p==255 or oldByte==0 or oldByte==255:
      if oldByte==p:
        sameCounter+=1
      else:
        if oldByte==0 or oldByte==255:
          if sameCounter>255:
            while(sameCounter>255):
              picComp.append(oldByte)
              picComp.append(255)
              sameCounter-=256
          picComp.append(oldByte)
          picComp.append(sameCounter)
          sameCounter=0
        if p!=0 and p!=255:
          picComp.append(p)
        
    else:
      picComp.append(p)
    oldByte = p
      
  # falls am Ende mehrere 0xff 0der 0x00 stehen:
  if sameCounter>0:
    if sameCounter>255:
      while(sameCounter>255):
        picComp.append(oldByte)
        picComp.append(255)
        sameCounter-=256
    picComp.append(oldByte)
    picComp.append(sameCounter)

  # Kontrolle
  contrCounter = 0
  spc = False
  for i in picComp:
    if spc == True:
      contrCounter+=i+1
      spc = False
    else:
      if(i==0 or i==255):
        spc = True
      else:
        contrCounter += 1
  print (contrCounter)
  return(picComp)

rootdir = '/home/chrak/Daten/Software/repositories/BadDisplay/bitmaps/pictures'
resultPath = "/home/chrak/Daten/Software/repositories/BadDisplay/bitmaps/"
resultFileName = "Bitmaps"
doCompact = True

resultCppFile = open(resultPath+resultFileName+".cpp", "w")
resulthFile = open(resultPath+resultFileName+".h", "w")

resultCppFile.write("#include \"%s.h\"\n\n"%resultFileName)


resulthFile.write("#ifndef %s_H_\n"%resultFileName.upper())
resulthFile.write("#define %s_H_\n\n"%resultFileName.upper())

resulthFile.write("#include <avr/pgmspace.h>\n\n")

files = glob.glob(rootdir+'/*.bmp') 
print(files)

for picFile in files:
  print("------------- %s -------------"%picFile)
  if doCompact:
    picName = os.path.basename(picFile).replace('.','_c')
  else:
    picName = os.path.basename(picFile).replace('.','_')
  printImageInfos(picFile)
  image = imageio.imread(os.path.join(".",picFile))
  print(image.shape)
  rawdata = image2DogDislay(image)
  if doCompact:
    data = compressImage(rawdata)
  else:
    data = rawdata

      
  resulthFile.write("extern const char data_%s[] PROGMEM;\n"%picName)
  resultCppFile.write("const char data_%s[] PROGMEM = {\n"%picName)
  
  notReady = True
  j=0
  dataSize = len(data)
  while notReady:
    resultCppFile.write("  ")
    i=0
    while i<16 and notReady:
      resultCppFile.write("0x%02x,"%data[j])
      i+=1
      j+=1
      if j>=dataSize:
        notReady=False
    resultCppFile.write("\n")
      
  resultCppFile.write("};\n\n")
resultCppFile.close()   

resulthFile.write("\n#endif /* %s_H_ */\n"%resultFileName.upper())
resulthFile.close() 
 

