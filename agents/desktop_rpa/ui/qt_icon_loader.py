"""Load colorful emoji icons for Qt UI using Unicode emoji rendering."""
from PySide6.QtGui import QIcon, QPixmap, QPainter, QFont, QColor
from PySide6.QtCore import Qt, QSize


class EmojiIconLoader:
    """Load colorful emoji icons for Qt UI."""
    
    # Emoji mappings
    EMOJIS = {
        'gear': '⚙️',
        'search': '🔍',
        'list': '📋',
        'edit': '✏️',
        'play': '▶️',
        'stop': '⏹️',
        'chart': '📊',
        'eye': '👁️',
        'book': '📚',
        'rocket': '🚀',
        'check': '✅',
        'cross': '❌',
        'warning': '⚠️',
        'thinking': '💭',
        'camera': '📸',
        'circle_green': '🟢',
        'circle_orange': '🟡',
        'circle_red': '🔴',
        'circle_blue': '🔵',
        'circle_purple': '🟣',
        'circle_gray': '⚪',
    }
    
    @staticmethod
    def create_emoji_icon(emoji: str, size: int = 32) -> QIcon:
        """Create a QIcon from an emoji character."""
        # Create pixmap
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        # Draw emoji
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # Use Segoe UI Emoji font on Windows for colored emojis
        font = QFont("Segoe UI Emoji", int(size * 0.7))
        painter.setFont(font)
        
        # Draw emoji centered
        painter.drawText(pixmap.rect(), Qt.AlignCenter, emoji)
        painter.end()
        
        return QIcon(pixmap)
    
    @staticmethod
    def get_icon(name: str, size: int = 32) -> QIcon:
        """Get an emoji icon by name."""
        emoji = EmojiIconLoader.EMOJIS.get(name, '❓')
        return EmojiIconLoader.create_emoji_icon(emoji, size)
    
    @staticmethod
    def create_status_icon(color: str, size: int = 16) -> QIcon:
        """Create a colored circle status icon."""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw filled circle
        painter.setBrush(QColor(color))
        painter.setPen(Qt.NoPen)
        margin = 2
        painter.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)
        painter.end()
        
        return QIcon(pixmap)


# Icon cache
_icon_cache = {}


def get_emoji_icon(name: str, size: int = 24) -> QIcon:
    """Get or create an emoji icon."""
    cache_key = f"{name}_{size}"
    
    if cache_key not in _icon_cache:
        _icon_cache[cache_key] = EmojiIconLoader.get_icon(name, size)
    
    return _icon_cache[cache_key]


def get_status_icon(color: str, size: int = 16) -> QIcon:
    """Get or create a status icon."""
    cache_key = f"status_{color}_{size}"
    
    if cache_key not in _icon_cache:
        _icon_cache[cache_key] = EmojiIconLoader.create_status_icon(color, size)
    
    return _icon_cache[cache_key]

