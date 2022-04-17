import numpy as np
from .GuidedFilter import GuidedFilter


def  Refinedtransmission(transmission,img):

    gimfiltR = 50  # The size of the radius when guiding the filter
    eps = 10 ** -3  # The value of epsilon during bootstrap filtering

    guided_filter = GuidedFilter(img, gimfiltR, eps)
    transmission = guided_filter.filter(transmission)
    transmission = np.clip(transmission,0.1, 0.9)

    return transmission
