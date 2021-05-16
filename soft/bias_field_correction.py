from __future__ import print_function

import SimpleITK as sitk
import sys
import os
import time

begin = time.time() 

if len(sys.argv) < 2:
    print("Usage: N4BiasFieldCorrection inputImage " +
          "outputImage [shrinkFactor] [maskImage] [numberOfIterations] " +
          "[numberOfFittingLevels]")
    sys.exit(1)

inputImage = sitk.ReadImage(sys.argv[1], sitk.sitkFloat32)
image = inputImage

if len(sys.argv) > 4:
    maskImage = sitk.ReadImage(sys.argv[4], sitk.sitkUint8)
else:
    maskImage = sitk.OtsuThreshold(inputImage, 0, 1, 200)

if len(sys.argv) > 3:
    image = sitk.Shrink(inputImage,
                             [int(sys.argv[3])] * inputImage.GetDimension())
    maskImage = sitk.Shrink(maskImage,
                            [int(sys.argv[3])] * inputImage.GetDimension())

corrector = sitk.N4BiasFieldCorrectionImageFilter()

numberFittingLevels = 4

if len(sys.argv) > 6:
    numberFittingLevels = int(sys.argv[6])
    

if len(sys.argv) > 5:
    corrector.SetMaximumNumberOfIterations([int(sys.argv[5])]
                                           * numberFittingLevels)

print("Applying N4BiasFieldCorrection...")
output = corrector.Execute(image, maskImage)

print("Getting Log Bias Field as image...")
log_bias_field = corrector.GetLogBiasFieldAsImage(inputImage)

output = inputImage / sitk.Exp( log_bias_field )

print("Saving image...")
sitk.WriteImage(output, sys.argv[2])

end = time.time() 
print("Total time taken :", (end - begin)//60 ,"min.", (end - begin)%60 , "s")
