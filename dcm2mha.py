import sys
import SimpleITK as sitk
import os


def main():
    print("[dcm2mha] Reading DICOM directory: \"./input\"")
    reader = sitk.ImageSeriesReader()
    seriesuid = reader.GetGDCMSeriesIDs("./input")
    # reader.LoadPrivateTagsOn()
    for uid in seriesuid:
        dicom_names = reader.GetGDCMSeriesFileNames("./input", uid)
        reader.SetFileNames(dicom_names)
        image: sitk.Image = None
        try:
            image = reader.Execute()
        except:
            # return -1
            print(f"Unable to read image: {uid}")
            continue
        print(f"[dcm2mha] Image: size {image.GetSize()}, pixel type {image.GetPixelIDTypeAsString()}, spacing {image.GetSpacing()}")
        print("[dcm2mha] Writing as MHA to ./output")
        filename = os.path.join("./output", uid + ".mha")
        if os.path.exists(filename):
            print(f"[dcm2mha] File exists, overwriting: \"{filename}\"")
        sitk.WriteImage(image, filename)
        print("[dcm2mha] DICOM saved as MHA")
    return 0
        # else:
        #     print("[dcm2mha] SeriesInstanceUID not found")
        #     print("[dcm2mha] Unable to save as MHA")
        #     return -1
    

if __name__ == "__main__":
    main()