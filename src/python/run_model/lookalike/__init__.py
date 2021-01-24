import os
import face_recognition
from joblib import load

clf = load(os.environ['MODEL_PATH'])


def find_lookalike(image_path):
    unknown_image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(unknown_image)
    if len(face_locations) == 0:
        return {'success': False, 'result': 'no_face'}
    elif len(face_locations) > 1:
        return {'success': False, 'result': 'multiple_faces'}
    unknown_face_encodings = face_recognition.face_encodings(unknown_image, known_face_locations=face_locations)
    name = clf.predict([unknown_face_encodings[0]])
    print(name)
    return {'success': True, 'result': name.tolist()}
