from .RESTORE.sceneRadiance import sceneRadianceRGBMIP
from .RESTORE.TM import getTransmission
from .RESTORE.getRefinedTramsmission import Refinedtransmission
from .RESTORE.EstimateDepth import DepthMap
from .RESTORE.BL import getAtomsphericLight

from .DCP.GuidedFilter import GuidedFilter
from .DCP.main import getMinChannel
from .DCP.main import getDarkChannel
from .DCP.main import getAtomsphericLight

from .ENHANCE.LabStretching import LABStretching
from .ENHANCE.color_equalisation import RGB_equalisation_RGHS
from .ENHANCE.global_stretching_RGB import stretching

from matplotlib import pyplot as plt
from django.shortcuts import render
from .models import InputRestore, InputClassify, InputEnhance

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


def restore(request):
    return render(request, 'restore.html', {'img1': "static/ip_img.jpg", 'v': "hidden", 'in': "visible"})


def enhance(request):
    return render(request, 'enhance.html', {'img1': "static/ip_img.jpg", 'v': "hidden", 'in': "visible"})


def classify(request):
    return render(request, 'classify.html', {'img1': "static/ip_img.jpg"})


def about(request):
    return render(request, 'about.html')


def get_image_restore(request):
    if not os.path.exists("UWIE/static/Input/RESTORED/"):
        os.makedirs("UWIE/static/Input/RESTORED/")

    shutil.rmtree("UWIE/static/Input/RESTORED/")

    if request.method == "POST":
        in_img = request.FILES['image']
        in_img.name = "input.jpg"
        input = InputRestore(img=in_img)
        input.save()
        restoreMethod("UWIE/static")
        img1 = "static/Input/RESTORED/input.jpg"
        img2 = "RESTORED.jpg"
        hist_in = "hist_in.jpg"
        hist_out = "hist_op.jpg"
    return render(request, 'restore.html', {'img1': img1, 'img2': img2, 'D': "RESTORED_diff.jpg",'hist_in': hist_in,'hist_out': hist_out,
                                        'TR': "RESTORED_tr.jpg", 'RT': "RESTORED_rtra.jpg", 'TM': "RESTORED_TM.jpg", 'in': 'none'})


def restoreMethod(folder):
    img = cv2.imread(folder + '/Input/RESTORED/input.jpg')

    if not os.path.exists(folder+"/Output/RESTORED/"):
        os.makedirs(folder+"/Output/RESTORED/")

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

    cv2.imwrite(folder + '/Output/RESTORED/' + 'RESTORED_TM.jpg',
                np.uint8(transmission * 255))
    cv2.imwrite(folder + '/Output/RESTORED/' + 'RESTORED_diff.jpg', np.uint8(Diff * 255))
    cv2.imwrite(folder + '/Output/RESTORED/' + 'RESTORED_tr.jpg', np.uint8(Tr * 255))
    cv2.imwrite(folder + '/Output/RESTORED/' + 'RESTORED_rtra.jpg', np.uint8(Rtr * 255))
    cv2.imwrite(folder + '/Output/RESTORED/' + 'RESTORED.jpg', sceneRadiance)

    inp = plt.figure()
    plt.hist(img.flatten(), 256, [0, 256])
    inp.savefig(folder+'/Output/RESTORED/hist_in.jpg')
    plt.close(inp)

    op = plt.figure()
    plt.hist(sceneRadiance.flatten(), 256, [0, 256])
    op.savefig(folder+'/Output/RESTORED/hist_op.jpg')
    plt.close(op)


def get_image_enhance(request):
    if not os.path.exists("UWIE/static/Input/ENHANCED/"):
        os.makedirs("UWIE/static/Input/ENHANCED/")

    shutil.rmtree("UWIE/static/Input/ENHANCED/")

    if request.method == "POST":
        in_img = request.FILES['image']
        in_img.name = "input.jpg"
        input = InputEnhance(img=in_img)
        input.save()
        enhanceMethod("UWIE/static")
        img1 = "static/Input/ENHANCED/input.jpg"
        img2 = "ENHANCED.jpg"
        hist_in = "hist_in.jpg"
        hist_out = "hist_op.jpg"
    return render(request, 'enhance.html', {'img1': img1, 'img2': img2, 'R': "ENHANCED_RGB.jpg", 'S': "ENHANCED_stretch.jpg", 'in': 'none','hist_in': hist_in,'hist_out': hist_out,})


def enhanceMethod(folder):
    img = cv2.imread(folder + '/Input/ENHANCED/input.jpg')

    if not os.path.exists(folder+"/Output/ENHANCED/"):
        os.makedirs(folder+"/Output/ENHANCED/")

    height = len(img)

    width = len(img[0])

    sceneRadiance = img

    sceneRadiance = RGB_equalisation_RGHS(img)
    cv2.imwrite(folder+'/Output/ENHANCED/'+'ENHANCED_RGB.jpg', sceneRadiance)

    sceneRadiance = stretching(sceneRadiance)
    cv2.imwrite(folder+'/Output/ENHANCED/'+'ENHANCED_stretch.jpg', sceneRadiance)

    sceneRadiance = LABStretching(sceneRadiance)

    cv2.imwrite(folder+'/Output/ENHANCED/'+'ENHANCED.jpg', sceneRadiance)

    inp = plt.figure()
    plt.hist(img.flatten(), 256, [0, 256])
    inp.savefig(folder+'/Output/ENHANCED/hist_in.jpg')
    plt.close(inp)

    op = plt.figure()
    plt.hist(sceneRadiance.flatten(), 256, [0, 256])
    op.savefig(folder+'/Output/ENHANCED/hist_op.jpg')
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
