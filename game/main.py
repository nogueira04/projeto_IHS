import pygame
import random
import time

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Drone")

running = True

class Particle:
    def __init__(self, x, y, color, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.time_alive = 0
        self.velocity = (random.uniform(-2, 2), random.uniform(1, 3))

    def update(self, dt):
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt

        self.time_alive += dt * 2
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 1)

class Coin:
    def __init__(self):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.image = pygame.image.load("coin.png")  # Load your coin image
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def respawn(self):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.rect.center = (self.x, self.y)


class Drone:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.original_image = image
        self.rect = self.image.get_rect(center=(self.x, self.y)) 
        self.rotation = 0  
        self.gravity = 9.8  
        self.left_thrust = 20
        self.right_thrust = 20
        self.rotation_factor = 5
        self.particles = [] 

        self.score = 0

        self.angular_speed = 0
        self.angular_acceleration = 0

        self.x_acceleration = 0
        self.y_acceleration = 0
        self.velocity_x = 0
        self.velocity_y = 0

    def reset(self):
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.x_acceleration = 0
        self.y_acceleration = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.rotation = 0
        self.score = 0
        self.angular_speed = 0
        self.angular_acceleration = 0
        

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.center = (self.x, self.y)
    
    def rotate(self, angle):
        self.rotation += angle
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, dt):
        keys = pygame.key.get_pressed() 


        upward_thrust = 0
        if keys[pygame.K_UP]:
            upward_thrust += 50
            self.generate_particles(1)
            self.generate_particles(-1)
        if keys[pygame.K_DOWN]:
            upward_thrust -= 50
            self.generate_particles(1)
            self.generate_particles(-1)
        if keys[pygame.K_LEFT]:
            upward_thrust -= self.left_thrust
            self.generate_particles(-1)  
        if keys[pygame.K_RIGHT]:
            upward_thrust -= self.right_thrust
            self.generate_particles(1)  

        self.y_acceleration -= upward_thrust
        thrust_difference = self.right_thrust * keys[pygame.K_RIGHT] - self.left_thrust * keys[pygame.K_LEFT]
        self.x_acceleration += (thrust_difference / 0.5)  
        self.y_acceleration += self.gravity

        lever_arm = self.image.get_width() / 12  # Adjust as needed
        torque = thrust_difference * lever_arm  

        I = 0.5  # Estimated moment of inertia (adjust for your drone shape)
        self.angular_acceleration = torque / I


        # Update velocity based on acceleration
        self.velocity_x += self.x_acceleration * dt
        self.velocity_y += self.y_acceleration * dt
        self.angular_speed += self.angular_acceleration * dt 

        self.rotation += self.angular_speed * dt 

        self.move(self.velocity_x * dt, self.velocity_y * dt)

        # Apply friction 
        self.velocity_x *= 0.95
        self.velocity_y *= 0.95  

        # Apply rotation
        self.image = pygame.transform.rotate(self.original_image, self.rotation)

        # Update and draw particles
        self.update_particles(dt)
        if self.rect.top <= -20 or self.rect.bottom >= screen_height + 20:
            self.reset()

        if self.rect.left <= -20 or self.rect.right >= screen_width + 20:
            self.reset()
        
    
    def generate_particles(self, direction):
        for _ in range(2): 
            if direction == -1:
                x_offset = -(self.image.get_width()) // 2
            else:
                x_offset = (self.image.get_width()) // 2
            
            y_offset = random.randint(5, 15)
            particle_color = (random.randint(100, 255), 255, 255) 
            self.particles.append(Particle(self.x + x_offset, self.y + y_offset, particle_color, 1))  

    def update_particles(self, dt):
        for particle in self.particles:
            particle.update(dt)
            particle.draw(screen)
            if particle.time_alive > particle.lifetime:
                self.particles.remove(particle)  


drone_image = pygame.image.load("drone.png")
drone = Drone(screen_width // 2, screen_height // 2, drone_image)
drone.original_image = drone_image

coins = [] 

def spawn_coin():
    if len(coins) < 3:  # Keep a maximum of 3 coins on screen
        coins.append(Coin())

def check_coin_collision():
    global score 
    for coin in coins:
        if drone.rect.colliderect(coin.rect):
            coins.remove(coin)
            drone.score += 1
            spawn_coin() 

font = pygame.font.SysFont('Arial', 30) 

last_time = time.time()
while running:
    dt = time.time() - last_time
    last_time = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((135, 206, 250))

    check_coin_collision() 
    spawn_coin() 

    score_text = font.render('Score: ' + str(drone.score), True, (255, 255, 255)) 
    screen.blit(score_text, (10, 10))

    for coin in coins: 
        coin.draw(screen) 

    drone.update(dt)
    drone.draw(screen)

    pygame.display.flip()

