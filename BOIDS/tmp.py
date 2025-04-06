import pygame

# Initialize Pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()


# Define the rotating sprite class
class RotatingSprite(pygame.sprite.Sprite):
    def __init__(self, image, position, rotation_speed):
        super().__init__()
        self.original_image = image  # Store the original image for rotation
        self.image = self.original_image
        self.rect = self.image.get_rect(center=position)  # Set initial position
        self.rotation_angle = 0  # Initial rotation angle
        self.rotation_speed = rotation_speed  # Speed of rotation

    def update(self):
        """Rotate the sprite each frame"""
        self.rotation_angle += self.rotation_speed
        if self.rotation_angle >= 360:
            self.rotation_angle -= 360

        # Rotate the image and update the rect
        rotated_image = pygame.transform.rotate(
            self.original_image, -self.rotation_angle
        )  # Negative for clockwise rotation
        self.image = rotated_image  # Set the new rotated image
        self.rect = self.image.get_rect(center=self.rect.center)  # Re-center the rect


# Create a red square sprite
sprite_image = pygame.Surface((50, 50), pygame.SRCALPHA)  # Transparent background
pygame.draw.rect(sprite_image, (255, 0, 0), (0, 0, 50, 50))  # Draw a red square

# Create a sprite group
sprite_group = pygame.sprite.Group()

# Add rotating sprites to the group
sprite1 = RotatingSprite(sprite_image, (400, 300), 2)  # Rotate by 2 degrees per frame
sprite2 = RotatingSprite(sprite_image, (200, 150), 4)  # Rotate by 4 degrees per frame

sprite_group.add(sprite1, sprite2)

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((255, 255, 255))

    # Update all sprites (this calls each sprite's `update()` method)
    sprite_group.update()

    # Draw all sprites (this blits them onto the screen)
    sprite_group.draw(screen)

    # Update the display
    pygame.display.flip()

    # Limit the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
