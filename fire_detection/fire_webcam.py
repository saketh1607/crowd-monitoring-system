import torch
from ultralytics import YOLO
import cv2

# 1. Check for GPU
print("CUDA available:", torch.cuda.is_available())
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

# 2. Load YOLO model and move it to GPU
model = YOLO("best.pt")
model.model.to(device)

# 3. Optional: Swap class names if needed
orig = model.model.names
model.model.names = {0: orig[1], 1: orig[0]}
print("Class mapping:", model.model.names)

# 4. Set inference resolution
INF_W, INF_H = 640, 384  # Lower resolution = faster inference

# 5. Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open webcam")
    exit()

# 6. Webcam loop
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Frame grab failed.")
        break

    # Resize for inference
    resized = cv2.resize(frame, (INF_W, INF_H))

    # Inference with GPU
    results = model(resized, device=device, conf=0.4)[0]

    # Annotate and resize back to original
    annotated_small = results.plot()
    annotated = cv2.resize(annotated_small, (frame.shape[1], frame.shape[0]))

    # Display
    cv2.imshow("🔥 Fire & Smoke Detection", annotated)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# 7. Cleanup
cap.release()
cv2.destroyAllWindows()