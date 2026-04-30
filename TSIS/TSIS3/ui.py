# This file has small UI tools.
# UI means User Interface: buttons, text, panels.
import pygame


# Basic colors in RGB format.
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (110, 110, 110)
LIGHT_GRAY = (190, 190, 190)
DARK_GRAY = (45, 45, 45)
GREEN = (40, 170, 80)
RED = (210, 60, 60)
BLUE = (60, 120, 220)
YELLOW = (230, 200, 60)


class Button:
    """This class creates a clickable button."""

    def __init__(self, rect, text, font, color=GRAY, hover_color=LIGHT_GRAY):
        # Button rectangle: x, y, width, height.
        self.rect = pygame.Rect(rect)

        # Text on the button.
        self.text = text

        # Font for the button text.
        self.font = font

        # Normal button color.
        self.color = color

        # Button color when mouse is on it.
        self.hover_color = hover_color

    def draw(self, screen):
        """Draw the button on the screen."""

        # Get mouse position.
        mouse_pos = pygame.mouse.get_pos()

        # If mouse is on the button, use hover color. Else, use normal color.
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color

        # Draw filled button rectangle.
        pygame.draw.rect(screen, current_color, self.rect, border_radius=12)

        # Draw white border around the button.
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=12)

        # Make text image.
        label = self.font.render(self.text, True, WHITE)

        # Put text in the center of the button.
        label_rect = label.get_rect(center=self.rect.center)

        # Draw text on the screen.
        screen.blit(label, label_rect)

    def clicked(self, event):
        """Return True if the button is clicked by left mouse button."""

        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def draw_text(screen, text, font, color, center=None, topleft=None):
    """Draw text on the screen."""

    # Create text image.
    image = font.render(text, True, color)

    # Get rectangle of text image.
    rect = image.get_rect()

    # Put text by center if center is given.
    if center:
        rect.center = center

    # Put text by top-left corner if topleft is given.
    if topleft:
        rect.topleft = topleft

    # Draw text image on the screen.
    screen.blit(image, rect)

    # Return text rectangle. It can be useful later.
    return rect


def draw_panel(screen, rect):
    """Draw a dark rounded panel with white border."""

    # Draw dark panel.
    pygame.draw.rect(screen, DARK_GRAY, rect, border_radius=16)

    # Draw white border.
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=16)
