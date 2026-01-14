"""Generate colorful icons for the UI."""
from PIL import Image, ImageDraw
import io
import tkinter as tk
from pathlib import Path


class IconGenerator:
    """Generate colorful icons for UI elements."""
    
    @staticmethod
    def create_circle_icon(color: str, size: int = 16) -> tk.PhotoImage:
        """Create a filled circle icon."""
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw filled circle
        margin = 2
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=color,
            outline=color
        )
        
        return IconGenerator._pil_to_photoimage(img)
    
    @staticmethod
    def create_search_icon(size: int = 16) -> tk.PhotoImage:
        """Create a search/magnifying glass icon."""
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw magnifying glass circle (blue)
        circle_size = int(size * 0.6)
        draw.ellipse(
            [2, 2, circle_size, circle_size],
            outline='#2196F3',
            width=2
        )
        
        # Draw handle
        handle_start = int(circle_size * 0.7)
        draw.line(
            [handle_start, handle_start, size - 2, size - 2],
            fill='#2196F3',
            width=2
        )
        
        return IconGenerator._pil_to_photoimage(img)
    
    @staticmethod
    def create_list_icon(size: int = 16) -> tk.PhotoImage:
        """Create a list/template icon."""
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw three horizontal lines (orange)
        color = '#FF9800'
        y_positions = [3, 7, 11]
        for y in y_positions:
            draw.rectangle([2, y, size - 2, y + 2], fill=color)
        
        return IconGenerator._pil_to_photoimage(img)
    
    @staticmethod
    def create_edit_icon(size: int = 16) -> tk.PhotoImage:
        """Create a pencil/edit icon."""
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw pencil (green)
        color = '#4CAF50'
        # Pencil body
        draw.polygon(
            [(size - 4, 2), (2, size - 4), (4, size - 2), (size - 2, 4)],
            fill=color,
            outline=color
        )
        # Pencil tip
        draw.polygon(
            [(2, size - 4), (2, size - 2), (4, size - 2)],
            fill='#FFC107'
        )
        
        return IconGenerator._pil_to_photoimage(img)
    
    @staticmethod
    def create_play_icon(size: int = 16) -> tk.PhotoImage:
        """Create a play/start icon."""
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw play triangle (green)
        margin = 2
        draw.polygon(
            [
                (margin, margin),
                (margin, size - margin),
                (size - margin, size // 2)
            ],
            fill='#4CAF50',
            outline='#4CAF50'
        )
        
        return IconGenerator._pil_to_photoimage(img)
    
    @staticmethod
    def create_stop_icon(size: int = 16) -> tk.PhotoImage:
        """Create a stop icon."""
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw square (red)
        margin = 3
        draw.rectangle(
            [margin, margin, size - margin, size - margin],
            fill='#F44336',
            outline='#F44336'
        )
        
        return IconGenerator._pil_to_photoimage(img)
    
    @staticmethod
    def create_chart_icon(size: int = 16) -> tk.PhotoImage:
        """Create a chart/stats icon."""
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw bar chart (blue)
        color = '#2196F3'
        bar_width = 3
        heights = [12, 8, 10, 6]
        x = 2
        for h in heights:
            draw.rectangle(
                [x, size - h - 2, x + bar_width, size - 2],
                fill=color
            )
            x += bar_width + 1
        
        return IconGenerator._pil_to_photoimage(img)
    
    @staticmethod
    def create_eye_icon(size: int = 16) -> tk.PhotoImage:
        """Create an eye/vision icon."""
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw eye shape (blue)
        color = '#2196F3'
        # Eye outline
        draw.ellipse([2, 5, size - 2, 11], outline=color, width=2)
        # Pupil
        draw.ellipse([6, 6, 10, 10], fill=color)
        
        return IconGenerator._pil_to_photoimage(img)
    
    @staticmethod
    def create_book_icon(size: int = 16) -> tk.PhotoImage:
        """Create a book/learning icon."""
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw book (purple)
        color = '#9C27B0'
        # Book cover
        draw.rectangle([3, 2, size - 3, size - 2], fill=color, outline=color)
        # Pages
        draw.line([size // 2, 2, size // 2, size - 2], fill='white', width=1)
        
        return IconGenerator._pil_to_photoimage(img)
    
    @staticmethod
    def create_gear_icon(size: int = 16) -> tk.PhotoImage:
        """Create a gear/settings icon."""
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw gear (gray)
        color = '#607D8B'
        center = size // 2
        
        # Outer circle with teeth
        draw.ellipse([3, 3, size - 3, size - 3], outline=color, width=2)
        # Inner circle
        draw.ellipse([6, 6, size - 6, size - 6], fill=color)
        
        # Teeth (4 directions)
        tooth_length = 2
        positions = [
            (center, 1, center, 3),  # top
            (center, size - 3, center, size - 1),  # bottom
            (1, center, 3, center),  # left
            (size - 3, center, size - 1, center),  # right
        ]
        for pos in positions:
            draw.line(pos, fill=color, width=2)
        
        return IconGenerator._pil_to_photoimage(img)
    
    @staticmethod
    def _pil_to_photoimage(pil_image: Image.Image) -> tk.PhotoImage:
        """Convert PIL Image to Tkinter PhotoImage."""
        # Convert to bytes
        with io.BytesIO() as output:
            pil_image.save(output, format='PNG')
            data = output.getvalue()
        
        # Create PhotoImage
        return tk.PhotoImage(data=data)


# Icon cache to prevent garbage collection
_icon_cache = {}


def get_icon(name: str, size: int = 16) -> tk.PhotoImage:
    """Get or create an icon by name."""
    cache_key = f"{name}_{size}"
    
    if cache_key not in _icon_cache:
        generator = IconGenerator()
        
        if name == "circle_green":
            _icon_cache[cache_key] = generator.create_circle_icon('#4CAF50', size)
        elif name == "circle_orange":
            _icon_cache[cache_key] = generator.create_circle_icon('#FF9800', size)
        elif name == "circle_red":
            _icon_cache[cache_key] = generator.create_circle_icon('#F44336', size)
        elif name == "circle_blue":
            _icon_cache[cache_key] = generator.create_circle_icon('#2196F3', size)
        elif name == "circle_purple":
            _icon_cache[cache_key] = generator.create_circle_icon('#9C27B0', size)
        elif name == "circle_gray":
            _icon_cache[cache_key] = generator.create_circle_icon('#9E9E9E', size)
        elif name == "search":
            _icon_cache[cache_key] = generator.create_search_icon(size)
        elif name == "list":
            _icon_cache[cache_key] = generator.create_list_icon(size)
        elif name == "edit":
            _icon_cache[cache_key] = generator.create_edit_icon(size)
        elif name == "play":
            _icon_cache[cache_key] = generator.create_play_icon(size)
        elif name == "stop":
            _icon_cache[cache_key] = generator.create_stop_icon(size)
        elif name == "chart":
            _icon_cache[cache_key] = generator.create_chart_icon(size)
        elif name == "eye":
            _icon_cache[cache_key] = generator.create_eye_icon(size)
        elif name == "book":
            _icon_cache[cache_key] = generator.create_book_icon(size)
        elif name == "gear":
            _icon_cache[cache_key] = generator.create_gear_icon(size)
        else:
            # Default: gray circle
            _icon_cache[cache_key] = generator.create_circle_icon('#9E9E9E', size)
    
    return _icon_cache[cache_key]

