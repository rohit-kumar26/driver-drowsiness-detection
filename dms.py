import cv2
import numpy as np
import time
from collections import deque
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

LEFT_EYE_POINTS = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_POINTS = [33, 160, 158, 133, 153, 144]

EAR_THRESHOLD = 0.21
ALERT_FRAMES = 15


def calculate_ear(eye):
    v1 = np.linalg.norm(eye[1] - eye[5])
    v2 = np.linalg.norm(eye[2] - eye[4])
    h = np.linalg.norm(eye[0] - eye[3])
    
    return (v1 + v2) / (2.0 * h)


def get_eye_landmarks(landmarks, indices, width, height):
    coords = []
    for i in indices:
        pt = landmarks[i]
        coords.append([int(pt.x * width), int(pt.y * height)])
    return np.array(coords)


def main():
    video_path = None
    
    if video_path:
        cap = cv2.VideoCapture(video_path)
    else:
        cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Can't open camera/video")
        return
    
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    closed_eye_frames = 0
    frame_times = deque(maxlen=30)
    total_frames = 0
    
    print("Starting DMS... Press 'q' to quit")
    
    while True:
        start_time = time.time()
        
        ret, frame = cap.read()
        if not ret:
            break
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        
        h, w = frame.shape[:2]
        
        if results.multi_face_landmarks:
            face = results.multi_face_landmarks[0]
            
            left_eye = get_eye_landmarks(face.landmark, LEFT_EYE_POINTS, w, h)
            right_eye = get_eye_landmarks(face.landmark, RIGHT_EYE_POINTS, w, h)
            
            left_ear = calculate_ear(left_eye)
            right_ear = calculate_ear(right_eye)
            ear = (left_ear + right_ear) / 2.0
            
            mp_drawing.draw_landmarks(
                frame, face,
                mp_face_mesh.FACEMESH_LEFT_EYE,
                None,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
            )
            mp_drawing.draw_landmarks(
                frame, face,
                mp_face_mesh.FACEMESH_RIGHT_EYE,
                None,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
            )
            
            if ear < EAR_THRESHOLD:
                closed_eye_frames += 1
                status = f"Eyes closing... {closed_eye_frames}/{ALERT_FRAMES}"
                color = (0, 165, 255)
            else:
                closed_eye_frames = 0
                status = "Alert"
                color = (0, 255, 0)
            
            if closed_eye_frames >= ALERT_FRAMES:
                status = "DROWSINESS ALERT!"
                color = (0, 0, 255)
            
            cv2.putText(frame, f"EAR: {ear:.3f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, status, (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        else:
            closed_eye_frames += 1
            cv2.putText(frame, "No face detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        frame_time = (time.time() - start_time) * 1000
        frame_times.append(frame_time)
        total_frames += 1
        
        avg_time = np.mean(frame_times)
        fps = 1000 / avg_time if avg_time > 0 else 0
        
        cv2.putText(frame, f"FPS: {fps:.1f} | Latency: {frame_time:.1f}ms", 
                   (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow('DMS', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    avg_latency = np.mean(frame_times) if frame_times else 0
    print(f"\nProcessed {total_frames} frames")
    print(f"Average latency: {avg_latency:.2f}ms")
    print(f"Average FPS: {1000/avg_latency:.2f}")


if __name__ == "__main__":
    main()
