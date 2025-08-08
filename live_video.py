import cv2
from deepface import DeepFace

# Init webcam
cap = cv2.VideoCapture(0)
frame_count = 0
emotion_label = "Analyzing..."

# Optional: store in a list for later processing
emotion_log = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    try:
        # Run DeepFace emotion detection
        analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        emotion_label = analysis[0]['dominant_emotion']
    except Exception as e:
        emotion_label = "Unknown"

    # Save to list
    emotion_log.append((frame_count, emotion_label))

    # Print to terminal
    print(f"Frame {frame_count}: {emotion_label}")

    # Overlay on frame
    cv2.putText(frame, f"Emotion: {emotion_label}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Show webcam feed
    cv2.imshow("Live Emotion Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Optional: Print final emotion log
# print(emotion_log)
