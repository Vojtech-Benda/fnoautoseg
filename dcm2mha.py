import sys
import SimpleITK as sitk
import os


def main():
    print("[dcm2mha] Reading DICOM directory \"./input\"")
    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames("./input")
    seriesuid = reader.GetGDCMSeriesIDs("./input")[0]
    reader.SetFileNames(dicom_names)
    # reader.LoadPrivateTagsOn()
    image: sitk.Image = None
    try:
        image = reader.Execute()
    except:
        return -1
    print(f"[dcm2mha] Image: size {image.GetSize()}, pixel type {image.GetPixelIDTypeAsString()}, spacing {image.GetSpacing()}")
    print("[dcm2mha] Writing as MHA to ./output")
    if len(seriesuid) > 0:
        filename = os.path.join("./output", seriesuid + ".mha")
        if os.path.exists(filename):
            print(f"[dcm2mha] File \"{filename}\" exists")
            print(f"[dcm2mha] Not saving as MHA")
            return -1
        sitk.WriteImage(image, filename)
        print("[dcm2mha] DICOM saved as MHA")
        return 0
    else:
        print("[dcm2mha] SeriesInstanceUID not found")
        print("[dcm2mha] Unable to save as MHA")
        return -1
    

if __name__ == "__main__":
    main()