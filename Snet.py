from resnet50 import ResNet50
from keras.applications import imagenet_utils
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from pathos.helpers.mp_helper import random_state
from keras.layers import Flatten,Dense
from keras.models import Model
import cv2


inputShape = (197, 197)
preprocess = imagenet_utils.preprocess_input


print("Loading ResNet50...")
model = ResNet50(weights='imagenet', include_top=False, input_shape=(197,197,3))

for layer in model.layers:
    layer.trainable=False
##model.layers.pop()
##model.layers[-1].outbound_nodes = []
##model.outputs = [model.layers[-1].output]
output = model.get_layer('avg_pool').output
output = Flatten()(output)
output = Dense(activation="relu", units=1000)(output) # your newlayer Dense(...)
output = Dense(activation="relu", units=500)(output)
output = Dense(activation="relu", units=250)(output)
output = Dense(activation="relu", units=100)(output)
output = Dense(activation="relu", units=50)(output)
output = Dense(activation="relu", units=4)(output)
model = Model(model.input, output)

print("Compiling...")
model.compile(loss='mean_squared_error', optimizer='rmsprop',metrics=['mse', 'acc'])
print("Successfully Compiled...")

train = pd.read_csv('training.csv')
train = train.iloc[:8000]


x_train,x_test,y_train,y_test = train_test_split(train['image_name'],train[['x1','x2','y1','y2']],random_state=42, test_size=0.1)

filename = 'images/'
test_images = []
print('Creating test data !!!')
testCount = 0
##for img in x_test:
##    print("Test image number = {}".format(testCount))
##    #image = load_img(filename+str(img), target_size=inputShape)
##    image = cv2.imread(filename+str(img))
##    image = cv2.resize(image, inputShape)
##    image = image[...,::-1]
##    image = img_to_array(image)
##    image = np.expand_dims(image, axis = 0) # image.shape = (1, 224, 224, 3)
##    image = preprocess(image) # image.shape = (1, 224, 224, 3)
##    test_images.append(image)
##    testCount += 1
##y_test = np.array(y_test).reshape(len(y_test),4)   
##test_images = np.array(test_images).reshape(len(test_images),224,224,3)
##print('Created !')

batch = 200
Count = 0
print('Creating train data !!!')
for count in range(int(len(x_train)/batch)):
    images=[]
    for img in x_train[count*batch: (count+1)*batch]:
        print("Train image number = {}".format(Count))
        image = cv2.imread(filename+str(img))
        image = cv2.resize(image, inputShape)
        image = image[...,::-1]
        image = img_to_array(image)
        image = np.expand_dims(image, axis = 0) # image.shape = (1, 224, 224, 3)
        image = preprocess(image) # image.shape = (1, 224, 224, 3)
        images.append(image)
        Count+=1
    images = np.array(images).reshape(batch,197,197,3)    
    out = np.array(y_train[count*batch: (count+1)*batch]).reshape(len(y_train[count*batch: (count+1)*batch]),4)
    out[:,0],out[:,2] = out[:,0]*(197/640),out[:,2]*(197/640)
    out[:,1],out[:,3] = out[:,1]*(197/480),out[:,3]*(197/480)
    print('Training the model')
    model.fit(images,out,epochs=2,batch_size=20)
    print('Done for batch number {}'.format(count))
    del images
    print ('Saving The Model')
    #    
    fname = "Detector"

    model_json = model.to_json()
    with open(fname + ".json", "w") as json_file:
        json_file.write(model_json)
    # # serialize weights to HDF5
    model.save_weights(fname + ".h5")
    print("Saved model to disk")

        
print ('Saving The Model')
#    
fname = "Detector"

model_json = model.to_json()
with open(fname + ".json", "w") as json_file:
    json_file.write(model_json)
# # serialize weights to HDF5
model.save_weights(fname + ".h5")
print("Saved model to disk")
