import cv2
import time
from deepface import DeepFace

cap = cv2.VideoCapture(0)
emotion_label = "Analyzing..."
emotion_log = []

frame_count = 0
last_capture_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_time = time.time()

    if current_time - last_capture_time >= 0.5:
        frame_count += 1
        try:
            analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            emotion_label = analysis[0]['dominant_emotion']
        except Exception as e:
            emotion_label = "Unknown"

        emotion_log.append((frame_count, emotion_label))
        print(f"Frame {frame_count}: {emotion_label}")

        last_capture_time = current_time

    cv2.putText(frame, f"Emotion: {emotion_label}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.imshow("Live Emotion Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("\nEmotion Log:")
print(emotion_log)
