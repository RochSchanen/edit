# convert data to bitmap and back to data

import base
from wx import Image
from numpy import zeros, frombuffer

# must be instanciated to use ConvertToBitmap
A = base.App() 

w, h, d = 2, 4, 3

data0 = zeros((h, w, 3), 'uint8')
data0[:,:,] = (10, 20, 30)

print(data0)
print('---')

flatdata0 = data0.tostring()

image0 = Image(w, h)

image0.SetData(flatdata0)

bitmap = image0.ConvertToBitmap()

image1 = bitmap.ConvertToImage()

flatdata1 = image1.GetData()

lineardata  = frombuffer(flatdata1, 'uint8')

data1 = lineardata.reshape(h, w, 3)

print(data1)
print('---')

    # def bitmapFromData(self, data):
    #     # get the data shape
    #     height, width, depth = data.shape
    #     # flatten to byte string
    #     flatdata = data.tostring()
    #     # create image of the right shape
    #     image = Image(width, height)     
    #     # load image with byte string
    #     image.SetData(flatdata)
    #     # convert image to bitmap
    #     bitmap = image.ConvertToBitmap()
    #     # done
    #     return bitmap

    # def dataFromBitmap24(self, bitmap):
    #     depth = 3 # the byte depth 
    #     # get the bitmap shape
    #     width, height = bitmap.GetSize()
    #     # convert to image
    #     image = bitmap.ConvertToImage()
    #     # flatten to byte string
    #     flatdata = image.GetData()
    #     # convert to one dimensional data array
    #     linear = frombuffer(flatdata, 'uint8')
    #     # re-shape into three dimentional array
    #     data = linear.reshape(height, width, depth)
    #     # done
    #     return data
