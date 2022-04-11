from .MIP.sceneRadiance import sceneRadianceRGBMIP
from .MIP.TM import getTransmission
from .MIP.getRefinedTramsmission import Refinedtransmission
from .MIP.EstimateDepth import DepthMap
from .MIP.BL import getAtomsphericLight

from .DCP.GuidedFilter import GuidedFilter
from .DCP.main import getMinChannel
from .DCP.main import getDarkChannel
from .DCP.main import getAtomsphericLight

from .RGHS.LabStretching import LABStretching
from .RGHS.color_equalisation import RGB_equalisation_RGHS
from .RGHS.global_stretching_RGB import stretching

from matplotlib import pyplot as plt
from django.shortcuts import render
from .models import InputMIP, InputClassify, InputRGHS

import cv2
import shutil
import os
import numpy as np
import os

from keras.models import load_model
from keras.preprocessing import image as image_utils

from PIL import Image, ImageOps

import matplotlib
matplotlib.use('Agg')
plt.ioff()


def index(request):
    return render(request, 'index.html')


def mip(request):
    return render(request, 'mip.html', {'img1': "static/ip_img.jpg", 'v': "hidden", 'in': "visible"})


def rghs(request):
    return render(request, 'rghs.html', {'img1': "static/ip_img.jpg", 'v': "hidden", 'in': "visible"})


def classify(request):
    return render(request, 'classify.html', {'img1': "static/ip_img.jpg"})


def about(request):
    return render(request, 'about.html')


def get_image_mip(request):
    if not os.path.exists("UWIE/static/Input/MIP/"):
        os.makedirs("UWIE/static/Input/MIP/")

    shutil.rmtree("UWIE/static/Input/MIP/")

    if request.method == "POST":
        in_img = request.FILES['image']
        in_img.name = "input.jpg"
        input = InputMIP(img=in_img)
        input.save()
        restoreMIP("UWIE/static")
        img1 = "static/Input/MIP/input.jpg"
        img2 = "MIP.jpg"
        hist_in = "hist_in.jpg"
        hist_out = "hist_op.jpg"
    return render(request, 'mip.html', {'img1': img1, 'img2': img2, 'D': "MIP_diff.jpg",'hist_in': hist_in,'hist_out': hist_out,
                                        'TR': "MIP_tr.jpg", 'RT': "MIP_rtra.jpg", 'TM': "MIP_TM.jpg", 'in': 'none'})


def restoreMIP(folder):
    img = cv2.imread(folder + '/Input/MIP/input.jpg')

    if not os.path.exists(folder+"/Output/MIP/"):
        os.makedirs(folder+"/Output/MIP/")

    blockSize = 9

    Diff = None
    Tr = None
    Rtr = None

    largestDiff = DepthMap(img, blockSize)
    Diff = largestDiff

    transmission = getTransmission(largestDiff)
    Tr = transmission

    transmission = Refinedtransmission(transmission, img)
    Rtr = transmission

    AtomsphericLight = getAtomsphericLight(transmission, img)

    sceneRadiance = sceneRadianceRGBMIP(
        img, transmission, AtomsphericLight)

    cv2.imwrite(folder + '/Output/MIP/' + 'MIP_TM.jpg',
                np.uint8(transmission * 255))
    cv2.imwrite(folder + '/Output/MIP/' + 'MIP_diff.jpg', np.uint8(Diff * 255))
    cv2.imwrite(folder + '/Output/MIP/' + 'MIP_tr.jpg', np.uint8(Tr * 255))
    cv2.imwrite(folder + '/Output/MIP/' + 'MIP_rtra.jpg', np.uint8(Rtr * 255))
    cv2.imwrite(folder + '/Output/MIP/' + 'MIP.jpg', sceneRadiance)

    inp = plt.figure()
    plt.hist(img.flatten(), 256, [0, 256])
    inp.savefig(folder+'/Output/MIP/hist_in.jpg')
    plt.close(inp)

    op = plt.figure()
    plt.hist(sceneRadiance.flatten(), 256, [0, 256])
    op.savefig(folder+'/Output/MIP/hist_op.jpg')
    plt.close(op)


def get_image_rghs(request):
    if not os.path.exists("UWIE/static/Input/RGHS/"):
        os.makedirs("UWIE/static/Input/RGHS/")

    shutil.rmtree("UWIE/static/Input/RGHS/")

    if request.method == "POST":
        in_img = request.FILES['image']
        in_img.name = "input.jpg"
        input = InputRGHS(img=in_img)
        input.save()
        enhanceRGHS("UWIE/static")
        img1 = "static/Input/RGHS/input.jpg"
        img2 = "RGHS.jpg"
        hist_in = "hist_in.jpg"
        hist_out = "hist_op.jpg"
    return render(request, 'rghs.html', {'img1': img1, 'img2': img2, 'R': "RGHS_RGB.jpg", 'S': "RGHS_stretch.jpg", 'in': 'none','hist_in': hist_in,'hist_out': hist_out,})


def enhanceRGHS(folder):
    img = cv2.imread(folder + '/Input/RGHS/input.jpg')

    if not os.path.exists(folder+"/Output/RGHS/"):
        os.makedirs(folder+"/Output/RGHS/")

    height = len(img)

    width = len(img[0])

    sceneRadiance = img

    sceneRadiance = RGB_equalisation_RGHS(img)
    cv2.imwrite(folder+'/Output/RGHS/'+'RGHS_RGB.jpg', sceneRadiance)

    # sceneRadiance1 = RelativeGHstretching(sceneRadiance, height, width)
    # cv2.imwrite(folder+'/Output/RGHS/'+'RGHS_GH.jpg',sceneRadiance1)

    sceneRadiance = stretching(sceneRadiance)
    cv2.imwrite(folder+'/Output/RGHS/'+'RGHS_stretch.jpg', sceneRadiance)

    sceneRadiance = LABStretching(sceneRadiance)

    cv2.imwrite(folder+'/Output/RGHS/'+'RGHS.jpg', sceneRadiance)

    inp = plt.figure()
    plt.hist(img.flatten(), 256, [0, 256])
    inp.savefig(folder+'/Output/RGHS/hist_in.jpg')
    plt.close(inp)

    op = plt.figure()
    plt.hist(sceneRadiance.flatten(), 256, [0, 256])
    op.savefig(folder+'/Output/RGHS/hist_op.jpg')
    plt.close(op)


def classifyimage(request):

    folder = "UWIE/static/Input/CLASSIFY/"

    if not os.path.exists(folder):
        os.makedirs(folder)

    shutil.rmtree(folder)

    ans = None
    model = load_model('keras_model.h5')
    if request.method == "POST":
        in_img = request.FILES['image']
        in_img.name = "input.jpg"
        input = InputClassify(img=in_img)
        input.save()
    


        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        image = input 
        image = Image.open(folder + 'input.jpg')

        size = (224, 224)
        image = ImageOps.fit(image, size, Image.ANTIALIAS)

        image_array = np.asarray(image)
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
        data[0] = normalized_image_array

        prediction = model.predict(data)

        result = np.where(prediction == np.amax(prediction))

        if(result[-1]==0):
            ans = 'Macro'
        elif(result[-1]==1):
            ans = 'Monti'
        elif(result[-1]==2):
            ans = 'Pocill'
        if(result[-1]==3):
            ans = 'Porit'
        elif(result[-1]==4):
            ans = 'Sand'
        elif(result[-1]==5):
            ans = 'Turf'
        
    rr = prediction[-1]
    max = rr[np.argmax(rr)]
    per = float(max)*100
    percentage = round(per, 2)
    img1 = "static/Input/CLASSIFY/input.jpg"
    print( {'img1': img1, 'r': ans,'p':percentage})
    return render(request, 'classify.html', {'img1': img1, 'r': ans})
