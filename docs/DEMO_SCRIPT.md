# SIH 2026 Presentation: ANVAY Demo Script

**Estimated Duration: 90 - 120 Seconds**

## Setup (Before Stage)
- 3 laptops arranged side-by-side.
- Laptop 1 (Center): Running Server + Dashboard + Camera 1 (Webcam)
- Laptop 2 (Left): Running Camera 2 (Webcam/Simulation)
- Laptop 3 (Right): Running Camera 3 (Webcam/Simulation)
- All connected to the same Wi-Fi.

## [0:00 - 0:20] The Introduction
**Presenter:**
"Good morning judges. We present to you ANVAY. This is not a concept or a slideshow. We are running a live, distributed multi-camera vehicle intelligence network right here on stage."

*(Gestures to the laptops)*

"This center screen is our Command Dashboard. It is receiving live, processed data from these three separate physical edge nodes. You can see the three camera feeds streaming live, confirming their 'ONLINE' status."

## [0:20 - 0:45] The Inference Demo
**Presenter:**
*(Holds up a phone or printed paper with a vehicle and Indian license plate to Laptop 1's Webcam)*

"Watch the Camera 1 panel. ANVAY's edge node instantly detects the vehicle, estimates its colour, locates the license plate, and runs OCR to extract the registration."

*(Points to the Dashboard)*

"You can see the raw intelligence overlaid right on the video feed. More importantly, this edge node has transmitted this data to our central server. The vehicle is now logged in the 'Tracked Vehicles' pane below."

## [0:45 - 1:10] The Multi-Camera Tracking Demo
**Presenter:**
"Now for the real power of ANVAY: Cross-camera tracking without huge bandwidth costs."

*(Moves the same picture from Laptop 1 to Laptop 2)*

"As the vehicle leaves Camera 1's field of view and enters Camera 2, watch the Live Journey Map in the center."

*(The trajectory map draws a line connecting Node 1 to Node 2)*

"Our backend tracking engine recognized the same vehicle based on its extracted metadata—not by streaming gigabytes of video to the cloud. We achieved multi-camera re-identification entirely using lightweight metadata payloads."

## [1:10 - 1:30] Conclusion
**Presenter:**
"ANVAY works on 3 cameras, and it scales to 3,000. By pushing inference to the edge and only centralizing structured metadata, we save bandwidth, reduce latency, and create a truly scalable Smart City infrastructure."

"Thank you."
