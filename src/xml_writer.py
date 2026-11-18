import xml.etree.ElementTree as ET
import xml.dom.minidom
from pathlib import Path
from skimage import io, measure

def create_lmd_xml_from_mask(mask_path: Path, output_xml: Path, calib_points: list):
    """Extracts shapes from a binary mask and writes a Leica LMD XML."""
    try:
        mask = io.imread(str(mask_path))
    except Exception as e:
        raise ValueError(f"Could not load mask image at {mask_path}: {e}")
        
    # Convert to boolean array
    binary_mask = mask > 1
    
    # Extract raw boundaries (returns a list of (N, 2) arrays in (row, col) format)
    raw_contours = measure.find_contours(binary_mask, level=0.5)
    
    valid_contours = []
    for contour in raw_contours:
        if len(contour) > 20: 
            # approximate_polygon reduces vertices on straight lines
            simplified = measure.approximate_polygon(contour, tolerance=1.0)
            valid_contours.append(simplified)
            
    shape_count = len(valid_contours)

    root = ET.Element("ImageData")
    ET.SubElement(root, "GlobalCoordinates").text = "1"
    
    for i, (x, y) in enumerate(calib_points, start=1):
        ET.SubElement(root, f"X_CalibrationPoint_{i}").text = str(int(x))
        ET.SubElement(root, f"Y_CalibrationPoint_{i}").text = str(int(y))
        
    ET.SubElement(root, "ShapeCount").text = str(shape_count)
    
    for shape_idx, contour in enumerate(valid_contours, start=1):
        shape_node = ET.SubElement(root, f"Shape_{shape_idx}")
        
        ET.SubElement(shape_node, "PointCount").text = str(len(contour))
        ET.SubElement(shape_node, "TransferID").text = f"ROI_{shape_idx}"
        
        for point_idx, coords in enumerate(contour, start=1):
            y, x = coords  # Unpack (row, col) into (y, x)
            ET.SubElement(shape_node, f"X_{point_idx}").text = str(int(x))
            ET.SubElement(shape_node, f"Y_{point_idx}").text = str(int(y))
            
    xml_str = ET.tostring(root, encoding="utf-8")
    parsed_xml = xml.dom.minidom.parseString(xml_str)
    
    with open(output_xml, "w") as f:
        f.write(parsed_xml.toprettyxml(indent="  "))
        
    return shape_count