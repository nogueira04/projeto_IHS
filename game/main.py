import pygame
import random
import time
from control import read_button, write_right_display, write_left_display, digit_to_7seg, write_green_leds, write_red_leds

pygame.init()

GAME_DURATION = 120
start_time = time.time()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Drone")

running = True

write_green_leds(0b0)
write_red_leds(0b0)

cloud_image = pygame.image.load("cloud.png").convert_alpha()  # Assuming you have a 'cloud.png'

# Define a Cloud class
class Cloud:
    def __init__(self):
        self.x = random.randint(screen_width, screen_width + 100)  # Start offscreen
        self.y = random.randint(10, screen_height - 100)
        self.speed = random.uniform(0.5, 1.5)  # Randomize speed
        self.image = cloud_image

    def update(self):
        self.x -= self.speed
        if self.x < -self.image.get_width():  # Offscreen?  Respawn!
            self.x = random.randint(screen_width, screen_width + 100)
            self.y = random.randint(10, screen_height - 100)  
            self.speed = random.uniform(0.5, 1.5) 

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

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
        start_time = time.time()
        

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
        key = read_button()
        if key == 'UP':
            upward_thrust += 50
            self.generate_particles(1)
            self.generate_particles(-1)
        if key == 'DOWN':
            upward_thrust -= 50
            self.generate_particles(1)
            self.generate_particles(-1)
        if key == 'LEFT':
            upward_thrust -= self.left_thrust
            self.generate_particles(-1)  
        if key == 'RIGHT':
            upward_thrust -= self.right_thrust
            self.generate_particles(1)  

        self.y_acceleration -= upward_thrust
        thrust_difference = self.right_thrust * (1 if key == 'RIGHT' else 0) - self.left_thrust * (1 if key == 'LEFT' else 0)
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
    global score, drone, coins
    for coin in coins:
        if drone.rect.colliderect(coin.rect):
            coins.remove(coin)
            drone.score += 1
            spawn_coin() 
            write_green_leds(0b11111111)
            

def generate_time_binary(remaining_time, total_time, num_bits=18):
    filled_bits = int((num_bits * remaining_time) / total_time)
    empty_bits = num_bits - filled_bits

    binary_string = '1' * filled_bits + '0' * empty_bits
    return int(binary_string, 2)  # Convert binary string to integer

font = pygame.font.SysFont('Arial', 30) 

last_led_update = time.time()
led_update_interval = 0.7

clouds = [Cloud() for _ in range(5)]

last_time = time.time()
while running:
    dt = time.time() - last_time
    last_time = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    elapsed_time = time.time() - start_time
    remaining_time = GAME_DURATION - elapsed_time
    if remaining_time <= 0:
        drone.reset()
        coins = []
        start_time = time.time()

    current_time = time.time()
    if current_time - last_led_update >= led_update_interval:
        write_green_leds(0b0)
        last_led_update = current_time

    screen.fill((135, 206, 250))

    for cloud in clouds:
        cloud.update()
        cloud.draw(screen)

    check_coin_collision() 
    spawn_coin() 

    time_text = font.render('Time: ' + str(int(remaining_time)), True, (255, 255, 255))
    score_text = font.render('Score: ' + str(drone.score), True, (255, 255, 255)) 

    for coin in coins: 
        coin.draw(screen) 

    drone.update(dt)
    drone.draw(screen)

    minutes = int(remaining_time // 60)
    seconds = int(remaining_time % 60)

    minutes_seconds = int(str(minutes) + str(seconds if seconds >= 10 else '0' + str(seconds)))

    write_left_display(digit_to_7seg(abs(minutes_seconds)))

    write_right_display(digit_to_7seg(drone.score))

    write_red_leds(generate_time_binary(remaining_time, GAME_DURATION))

    pygame.display.flip()

