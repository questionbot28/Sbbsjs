import xml.etree.ElementTree as ET
from typing import Tuple

class AchievementBadgeGenerator:
    def __init__(self):
        self.namespace = {"svg": "http://www.w3.org/2000/svg"}
        ET.register_namespace("", self.namespace["svg"])

    def create_sparkle(self, x: int, y: int, size: int = 10) -> ET.Element:
        """Create a sparkle star effect"""
        sparkle = ET.Element("path")
        sparkle.set("d", f"M {x},{y-size} L {x+size/4},{y-size/4} L {x+size},{y} L {x+size/4},{y+size/4} "
                   f"L {x},{y+size} L {x-size/4},{y+size/4} L {x-size},{y} L {x-size/4},{y-size/4} Z")
        sparkle.set("fill", "gold")
        sparkle.set("class", "achievement-sparkle")
        return sparkle

    def generate_badge(self, emoji: str, color: str = "#4CAF50", size: Tuple[int, int] = (60, 60)) -> str:
        """Generate an animated achievement badge with sparkles"""
        width, height = size
        
        # Create SVG root
        svg = ET.Element("svg")
        svg.set("width", str(width))
        svg.set("height", str(height))
        svg.set("viewBox", f"0 0 {width} {height}")
        svg.set("class", "achievement-badge")

        # Create circular background
        circle = ET.SubElement(svg, "circle")
        circle.set("cx", str(width//2))
        circle.set("cy", str(height//2))
        circle.set("r", str(min(width, height)//2 - 5))
        circle.set("fill", color)
        circle.set("class", "achievement-glow")

        # Add text (emoji)
        text = ET.SubElement(svg, "text")
        text.set("x", str(width//2))
        text.set("y", str(height//2))
        text.set("text-anchor", "middle")
        text.set("dominant-baseline", "central")
        text.set("font-size", "30")
        text.text = emoji

        # Add sparkles
        sparkle_positions = [
            (10, 10), (width-10, 10),
            (10, height-10), (width-10, height-10)
        ]
        for i, (x, y) in enumerate(sparkle_positions):
            sparkle = self.create_sparkle(x, y)
            sparkle.set("class", f"achievement-sparkle sparkle-{i+1}")
            svg.append(sparkle)

        # Convert to string with proper XML declaration
        return ET.tostring(svg, encoding="unicode", method="xml")

    def save_badge(self, badge_svg: str, filename: str):
        """Save the badge SVG to a file"""
        with open(f"static/badges/{filename}.svg", "w", encoding="utf-8") as f:
            f.write(badge_svg)
