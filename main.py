import yolov5
import yaml
import pathlib
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

model = yolov5.load(r"C:\\Users\\solomon\\Desktop\\AI_project_3\\yolov5_best.pt")

img = 'model_test/test_5.png'
result = model(img, size=500, augment=False)

result.show()
result.save(save_dir='results/')
