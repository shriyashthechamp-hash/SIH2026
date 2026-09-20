import argparse
import csv
import cv2
import pytesseract
from pathlib import Path
import re
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed


VARIANTS = [
    "gray_2x", "contrast_2x", "clahe_2x", "otsu_2x", "adaptive_2x",
    "gray", "contrast", "clahe", "otsu", "adaptive"
]

def get_source_and_variant(filename):
    stem = filename.stem
    for var in VARIANTS:
        if stem.endswith(f"_{var}"):
            source = stem[:-(len(var)+1)]
            return source, var
    return stem, "unknown"

def process_image(img_path_str):
    img_path = Path(img_path_str)
    source, variant = get_source_and_variant(img_path)
    img = cv2.imread(str(img_path))
    if img is None:
        return []
    
    results = []
    psm_modes = [6, 7, 8, 13]
    whitelist = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    for psm in psm_modes:
        config = f"--psm {psm} -c tessedit_char_whitelist={whitelist}"
        try:
            data = pytesseract.image_to_data(img, config=config, output_type=pytesseract.Output.DICT)
            # Combine text and average confidence for non-empty words
            words = []
            confs = []
            for text, conf in zip(data['text'], data['conf']):
                text = text.strip()
                if text:
                    words.append(text)
                    if conf != '-1':
                        confs.append(float(conf))
            
            raw_text = " ".join(words)
            clean_text = re.sub(r'[^A-Z0-9]', '', raw_text)
            
            conf_val = ""
            if confs:
                conf_val = f"{sum(confs)/len(confs):.2f}"
            
            results.append({
                "source_image": source,
                "preprocess_variant": variant,
                "psm": psm,
                "raw_text": raw_text,
                "clean_text": clean_text,
                "ocr_confidence": conf_val
            })
        except Exception as e:
            pass
            
    return results

def main():
    parser = argparse.ArgumentParser(description="ANVAY V3 Multi-OCR Module")
    parser.add_argument("--input", type=str, required=True, help="Input directory")
    parser.add_argument("--output", type=str, required=True, help="Output CSV file")
    parser.add_argument("--smoke", action="store_true", help="Run on just 20 images")
    parser.add_argument("--workers", type=int, default=multiprocessing.cpu_count(), help="Number of workers")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_csv = Path(args.output)
    
    img_paths = list(input_dir.glob("*.jpg"))
    img_paths.sort()
    
    if args.smoke:
        img_paths = img_paths[:20]
        
    print(f"Total input images: {len(img_paths)}")
    
    all_results = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(process_image, str(p)) for p in img_paths]
        completed = 0
        for future in as_completed(futures):
            all_results.extend(future.result())
            completed += 1
            if completed % 1000 == 0 or completed == len(img_paths):
                print(f"Processed {completed}/{len(img_paths)} images")
            
    # filter and count
    non_empty = 0
    empty = 0
    unique_strings = set()
    
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "source_image", "preprocess_variant", "psm", 
            "raw_text", "clean_text", "ocr_confidence"
        ])
        writer.writeheader()
        for r in all_results:
            writer.writerow(r)
            if r["clean_text"]:
                non_empty += 1
                unique_strings.add(r["clean_text"])
            else:
                empty += 1
                
    print(f"Total preprocessing images: {len(img_paths)}")
    print(f"Total OCR attempts (rows): {len(all_results)}")
    print(f"Non-empty OCR outputs: {non_empty}")
    print(f"Empty OCR outputs: {empty}")
    print(f"Unique OCR strings: {len(unique_strings)}")
    print(f"Output saved to {output_csv}")
    
    if args.smoke:
        print("\nSample Candidates:")
        # print up to 5 non-empty
        count = 0
        for r in all_results:
            if r["clean_text"]:
                print(f"Source: {r['source_image']}, Var: {r['preprocess_variant']}, PSM: {r['psm']}, Clean: {r['clean_text']}, Conf: {r['ocr_confidence']}")
                count += 1
                if count >= 5:
                    break

if __name__ == "__main__":
    main()
