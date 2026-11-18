import argparse
import sys
from pathlib import Path

from src.xml_writer import create_lmd_xml_from_mask

def parse_calib_points(point_str: str) -> list:
    """Parses a string like '10,10 900,10 900,700' into a list of tuples."""
    try:
        points = []
        for pair in point_str.split():
            x, y = map(int, pair.split(','))
            points.append((x, y))
        if len(points) != 3:
            raise ValueError
        return points
    except Exception:
        raise argparse.ArgumentTypeError(
            "Calibration points must be exactly three x,y pairs separated by spaces. "
            "Example: '100,100 9000,100 9000,7000'"
        )

def main():
    parser = argparse.ArgumentParser(
        description="LMD XML Generator: Convert segmentation masks to Leica LMD shape lists."
    )
    
    parser.add_argument(
        "-m", "--mask", 
        type=Path, 
        required=True, 
        help="Path to the binary segmentation mask image."
    )
    
    parser.add_argument(
        "-o", "--output", 
        type=Path, 
        default=Path("lmd_shapes.xml"), 
        help="Output XML filename (default: lmd_shapes.xml)."
    )
    
    parser.add_argument(
        "-c", "--calib", 
        type=parse_calib_points, 
        required=True, 
        help="Three calibration points as 'X1,Y1 X2,Y2 X3,Y3' (Top-Left, Top-Right, Bottom-Right)."
    )

    args = parser.parse_args()

    if not args.mask.exists():
        print(f"Error: Mask file '{args.mask}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Processing mask: {args.mask}...")
    
    try:
        shape_count = create_lmd_xml_from_mask(args.mask, args.output, args.calib)
        print(f"Success: Exported {shape_count} shapes to {args.output}")
    except Exception as e:
        print(f"Failed to generate XML: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()