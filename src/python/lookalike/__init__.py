import os
import face_recognition

HERE = os.path.dirname(os.path.abspath(__file__))

biden_image = face_recognition.load_image_file(os.path.join(HERE, "biden.jpg"))
trump_image = face_recognition.load_image_file(os.path.join(HERE, "trump.jpg"))
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]
trump_face_encoding = face_recognition.face_encodings(trump_image)[0]
known_faces = [
    biden_face_encoding,
    trump_face_encoding
]

FACES = 'faces'
BIDEN = 'biden'
TRUMP = 'trump'


def decide_between_presidents(image_path):
    ret = {FACES: False, BIDEN: False, TRUMP: False}
    unknown_image = face_recognition.load_image_file(image_path)
    unknown_face_encodings = face_recognition.face_encodings(unknown_image)
    if len(unknown_face_encodings) > 0:
        ret[FACES] = True
        for unknown_face_encoding in unknown_face_encodings:
            results = face_recognition.compare_faces(known_faces, unknown_face_encoding)
            if not ret[BIDEN]:
                ret[BIDEN] = bool(results[0])
            if not ret[TRUMP]:
                ret[TRUMP] = bool(results[1])
    return ret
