"""
Structure:
      <dir_001/>
        <person_1>/
          <person_1_face-1>.jpg
          <person_1_face-2>.jpg
          .
          .
          <person_1_face-n>.jpg
         <person_2>/
           <person_2_face-1>.jpg
           <person_2_face-2>.jpg
           .
           .
           <person_2_face-n>.jpg
          .
          .
          <person_n>/
            <person_n_face-1>.jpg
            <person_n_face-2>.jpg
            .
            .
            <person_n_face-n>.jpg
      <dir_002/>
      .
      .
      <dir_012/>
"""

import face_recognition
from sklearn import svm
from joblib import dump
import os
import traceback

# Training the SVC classifier

# The training data would be all the face encodings from all the known images and the labels are their names
encodings = []
names = []

# dataset_path = '/mnt/efs/fs1/dataset/'
dataset_path = os.environ['DATASET_PATH']

# Training directory
train_dir_path = os.path.join(dataset_path, 'train')
train_dirs = os.listdir(train_dir_path)

try:
    for train_dir in train_dirs:
        celebrities_path = os.path.join(train_dir_path, train_dir)
        celebrities = os.listdir(celebrities_path)
        # Loop through each person in the training directory
        for celebrity in celebrities:
            i = 0
            celebrity_path = os.path.join(celebrities_path, celebrity)
            try:
                pix = os.listdir(celebrity_path)
            except:
                traceback.print_exc()
                continue

            # Loop through each training image for the current person
            for person_img in pix:
                try:
                    celebrity_pic_path = os.path.join(celebrity_path, person_img)
                    # Get the face encodings for the face in each image file
                    face = face_recognition.load_image_file(celebrity_pic_path)
                    # face_bounding_boxes = face_recognition.face_locations(face, model='cnn')
                    face_bounding_boxes = face_recognition.face_locations(face)

                    #If training image contains exactly one face
                    if len(face_bounding_boxes) == 1:
                        face_enc = face_recognition.face_encodings(face, known_face_locations=face_bounding_boxes)[0]
                        # Add face encoding for current image with corresponding label (name) to the training data
                        encodings.append(face_enc)
                        names.append(celebrity)
                        print('Added ' + celebrity)
                    else:
                        print(celebrity + "/" + person_img + " was skipped and can't be used for training")
                        continue
                    break
                except Exception as e:
                    traceback.print_exc()
                    print(celebrity + "/" + person_img + " was skipped")
                    continue
finally:
    print('Done with training!')
    # Create and train the SVC classifier
    clf = svm.SVC(gamma='scale')
    clf.fit(encodings, names)
    model_path = os.path.join(dataset_path, 'model')
    dump(clf, model_path)
    print('Dumped model to: ' + model_path)

#
# # Load the test image with unknown faces into a numpy array
# test_image = face_recognition.load_image_file('test_image.jpg')
#
# # Find all the faces in the test image using the default HOG-based model
# face_locations = face_recognition.face_locations(test_image)
# no = len(face_locations)
# print("Number of faces detected: ", no)
#
# # Predict all the faces in the test image using the trained classifier
# print("Found:")
# for i in range(no):
#     test_image_enc = face_recognition.face_encodings(test_image)[i]
#     name = clf.predict([test_image_enc])
#     print(*name)
