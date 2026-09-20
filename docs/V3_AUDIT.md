# ANVAY V3 AUDIT REPORT

## Current Repository Structure
- `camera_node/` - Node-based processing scripts
- `core/` - Core logic (`config.py`, `models.py`)
- `dashboard/` - Frontend UI (`app.js`, `index.html`, `style.css`)
- `data/` - Datasets and OCR results
- `models/` - PyTorch model checkpoints
- `scripts/` - Inference, OCR, and testing scripts
- `server/` - Backend server (`main.py`, `tracking.py`)

## Current Models
- `models/license-plate-finetune-v1n.pt`
- `models/license-plate-finetune-v2-best.pt`
- `models/yolo11n.pt`

## Current Datasets
- `data/indian_demo/` - Realistic ANPR testing/demo dataset
- `data/license_plate/` - License plate detection training dataset
- `data/temp_plate_dataset/` - Supplementary image data
- `data/veri/VeRi/` - Vehicle re-identification dataset

## Current Scripts
- `scripts/plate_ocr.py` (V1 pipeline)
- `scripts/plate_ocr_v2.py` (V2 pipeline)
- `scripts/simulate_demo.py`
- `scripts/test_plate.py`, `scripts/test_yolo.py`, `scripts/select_demo.py`
- Utilities for dataset processing (`check_plate_dataset.py`, `convert_plate_dataset.py`)

## Current Environment
- **Python**: 3.13.6
- **Packages**: `ultralytics`, `cv2` (opencv-python), `pytesseract`, `pandas` are installed and working.
- **Tesseract Version**: 5.5.3

## V1 Results
- Total detections: 1714
- Non-empty OCR: 1557
- Empty OCR: 157
- 8-12 character OCR: 1309

## V2 Results
- Total detections: 1714
- Non-empty OCR: 1713
- Empty OCR: 1
- 8-12 character OCR: 1535

## Identified Weaknesses
- Many visually different images produce the exact same wrong string (e.g., `MH47Y1124`).
- Minor visual variations output visually similar but structurally incorrect strings (e.g. `MHO2DS9365` vs `MH02DS9365`).
- Preprocessing and crop quality is insufficiently robust for diverse real-world Indian demo footage.
- No temporal or multi-frame consensus across tracked vehicles.
- Lack of explicit structural formatting and Indian plate validation limits the confidence of the OCR results.

## Proposed V3 Architecture
- **Phase 3**: Improve Plate Detection (Make confidence configurable and evaluate tradeoffs on demo dataset).
- **Phase 4**: Smart Plate Cropping (Reject invalid crops, preserve aspect ratio, generate crop variants like tight/5%/10%).
- **Phase 5**: Quality Checking (Calculate brightness, contrast, and Laplacian variance for sharpness to classify crops).
- **Phase 6**: Advanced Preprocessing (Implement multiple variations like grayscale, CLAHE, adaptive thresholding, etc., with intelligent scaling).
- **Phase 7**: Multi-OCR (Leverage different PSM modes (6, 7, 8, 13) and aggregate results).
- **Phase 8**: OCR Normalization (Contextual character correction specific to Indian plates).
- **Phase 9**: Indian Plate Format Validation (State + District + Letters + Numbers).
- **Phase 10**: Candidate Scoring (Transparent scoring function incorporating detection, OCR confidence, format score, consensus, etc.).
- **Phase 11**: Multi-frame Consensus (Aggregate OCR results across multiple video frames).
- **Phase 12**: Temporal / Vehicle ID (Prepare for cross-camera re-ID matching).
- **Phase 13**: V3 Pipeline Assembly (Robust script combining all steps).

## Exact Commands Used During Audit
```bash
pwd
find . -maxdepth 2 -type f | sort
find models -maxdepth 2 -type f | sort
find scripts -maxdepth 2 -type f | sort
find data -maxdepth 2 -type d | sort
python --version
which python
python -c "import ultralytics; print('ultralytics OK')"
python -c "import cv2; print('opencv OK')"
python -c "import pytesseract; print('pytesseract OK')"
python -c "import pandas; print('pandas OK')"
tesseract --version
```
