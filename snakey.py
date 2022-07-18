import pygame as pg
import sys, copy, os, random

pg.init()
# initiate pygame font lib
pg.font.init()
game_over_font=pg.font.SysFont('comicsans',40)
foods_eaten=pg.font.SysFont('comicsans', 30)

class Settings:
    def __init__(self, caption, icon_name, foodname, width=600, height=500, bg_color=(255, 255, 255), 
    head_color=(240, 15, 25), body_color=(244, 198, 200),snake_size=20,vel=10,FPS=60):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.caption = caption
        self.icon = pg.image.load(os.path.join(
            os.path.dirname(__file__), icon_name))
        self.head_color=head_color
        self.body_color=body_color
        self.snake_size=snake_size
        self.vel=vel
        self.direction=(0,-1)  # default direction is set to up
        self.FPS=FPS
        self.food=pg.image.load(os.path.join(
            os.path.dirname(__file__), foodname))


class Snake:
    def __init__(self, stgs):
        self.stgs = stgs
        self.direction=self.stgs.direction

        # initialize screen
        self.screen = pg.display.set_mode((self.stgs.width, self.stgs.height))
        pg.display.set_caption(self.stgs.caption)
        pg.display.set_icon(self.stgs.icon)
        

        # initialize the snake
        self.snake = [pg.Rect(self.stgs.width//2-self.stgs.snake_size//2,self.stgs.height//2-self.stgs.snake_size//2, 
                                self.stgs.snake_size, self.stgs.snake_size),]
        self.snake.append(self.create_snake(self.snake,self.stgs.snake_size))
        self.snake.append(self.create_snake(self.snake,self.stgs.snake_size))
        
        # initialize food
        self.food=pg.transform.scale(self.stgs.food,(self.stgs.snake_size,self.stgs.snake_size))
        self.shadowfood=pg.Rect(random.randint(0,self.stgs.width-self.stgs.snake_size),
                                random.randint(0,self.stgs.height-self.stgs.snake_size), 
                                self.stgs.snake_size, self.stgs.snake_size)
        # check collision on initialization
        self.create_food()

        # initialize game over status
        self.game_over=False

        # initialize food count
        self.eaten=0

        # run mainloop of the game
        self.run_mainloop()

    @staticmethod
    def create_snake(snake,snake_size):
        last_snake = snake[-1]
        # create a body part based on the last snake body
        return pg.Rect(last_snake.bottomleft[0],last_snake.bottomleft[1],snake_size,snake_size)
    
    def update_snake(self):
        # this refresh the snake by one step
        # the logic is to move the snake head to the direction
        # then replace from the first body with the next body

        new_head=copy.deepcopy(self.snake)[0]
        new_head.x+=self.direction[0]*self.stgs.snake_size
        new_head.y+=self.direction[1]*self.stgs.snake_size

        self.snake=[new_head,] + self.snake[:-1]
        del new_head


    def draw_screen(self):
        # draw background
        self.screen.fill(self.stgs.bg_color)
        
        # draw food
        self.draw_food()

        # draw snake body
        for i, body in enumerate(self.snake):
            pg.draw.rect(self.screen,self.stgs.head_color,body) if i==0 else pg.draw.rect(self.screen,self.stgs.body_color,body)
        
        # update snake position
        self.update_snake()
        
        # check eat food
        self.eat_food()

        # draw labels
        foods_eaten_text=foods_eaten.render(f"{self.eaten} foods eaten",1,(25,35,112))
        self.screen.blit(foods_eaten_text,(10,10))

        # refresh screen
        pg.display.update()

    def create_food(self):
        # keep generating food til no collision with snake
        while any(map(self.shadowfood.colliderect,self.snake)):
            topleft=(random.randint(0,self.stgs.width-self.stgs.snake_size), random.randint(0,self.stgs.height-self.stgs.snake_size))
            self.shadowfood.topleft=topleft
        
    
    def draw_food(self):
        self.screen.blit(self.food,self.shadowfood.topleft)


    def eat_food(self):
        if self.shadowfood.colliderect(self.snake[0]):
            # if collide, remove food->increase snake length by 1->add new food
            self.eaten+=1
            self.create_food()
            self.snake.append(self.create_snake(self.snake,self.stgs.snake_size))


    def check_keyboard(self,event,mode=0):
        if mode==0:
            keys=pg.key.get_pressed()
            if keys[pg.K_UP] and self.direction!=(0,1):
                self.direction=(0,-1)
            elif keys[pg.K_DOWN] and self.direction!=(0,-1):
                self.direction=(0,1)
            elif keys[pg.K_LEFT] and self.direction!=(1,0):
                self.direction=(-1,0)
            elif keys[pg.K_RIGHT] and self.direction!=(-1,0):
                self.direction=(1,0)
        else:
            if event.key==pg.K_UP and self.direction!=(0,1):
                self.direction=(0,-1)
            elif event.key==pg.K_DOWN and self.direction!=(0,-1):
                self.direction=(0,1)
            elif event.key==pg.K_LEFT and self.direction!=(1,0):
                self.direction=(-1,0)
            elif event.key==pg.K_RIGHT and self.direction!=(-1,0):
                self.direction=(1,0)

    def handle_game_over(self):
        head=self.snake[0]
        if head.x < 0 or head.x > self.stgs.width-self.stgs.snake_size: # collide with left/right border
            self.game_over=True
        elif head.y<0 or head.y>self.stgs.height-self.stgs.snake_size: # collide with upper/lower border
            self.game_over=True
        else:
            if head.collidelistall(self.snake[1:]):
                self.game_over=True
        
        # output banner
        if self.game_over:
            game_over_text=game_over_font.render(f"Game Over!",1,(167,45,99))
            self.screen.blit(game_over_text,((self.stgs.width-game_over_text.get_width())//2,self.stgs.height//2-game_over_text.get_height()//2))
            pg.display.update()
            pg.time.delay(3000)
            sys.exit()

    def run_mainloop(self):
        running = True
        while running:
            # run the main loop of the game
            pg.time.Clock().tick(self.stgs.FPS)
            # check user inputs
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    sys.exit()
                # check if user change snake direction
                if event.type==pg.KEYDOWN:
                    self.check_keyboard(event,1)

            # handle game over events
            self.handle_game_over()

            # draw screen
            self.draw_screen()

            # delay
            pg.time.delay(int(1000/self.stgs.vel))
            


if __name__ == '__main__':
    settings = Settings(caption="Snakeyyyy!", icon_name='icon.png',
                        width=1200, height=1000, bg_color=(220, 240, 235),foodname='xjp.jpg',snake_size=40)
    myGame = Snake(settings)
