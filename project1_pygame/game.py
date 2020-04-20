import pygame
import time
import random
 
# 初始化
pygame.init()
pygame.mixer.init()

# 螢幕長寬
display_width = 800
display_height = 800

# 顯示畫面
gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('405262180 資工四乙 劉育騏 凱留下樓梯 - by 尾玉')

# 設定時間
clock = pygame.time.Clock()

# 玩家
is2P = False
kai_len = 50
kaiImg = pygame.image.load('pic/kailiu-removebg-preview.png')
kaiImg = pygame.transform.scale(kaiImg, (kai_len, kai_len))

# 聲音
start_music = pygame.mixer.Sound("music/start_talk.wav")
dead_music = pygame.mixer.Sound("music/dead.wav")
recover_music = pygame.mixer.Sound("music/recover.wav")
hurt_music = pygame.mixer.Sound("music/hurt.wav")
bump_music = pygame.mixer.Sound("music/bump.wav")
turn_music = pygame.mixer.Sound("music/turn.wav")

background_music = "music/Short Trip - Roa [Vlog No Copyright Music].mp3"
background_music2 = "music/Dragon War.mp3"

# 背景圖片
backImg = pygame.image.load('pic/background.jpg').convert()
backImg = pygame.transform.scale(backImg, (display_width, display_height))

# y邊界, UI介面
ui_len = display_width
y_side = 100

#最多x個樓梯
max_num = 20

# 樓梯 長寬
wall_width = 100
wall_height = 25

# 模式
Hardmode = False

# 顏色
black = (0,0,0)
bright_black = (50,50,50)
white = (255,255,255)
red = (200,0,0)
green = (0,200,0)
gray = (192,192,192)
bright_red = (255,0,0)
bright_green = (0,255,0)
block_color = (53,115,255)
yellow = (200, 200, 0)
bright_yellow = (255, 255, 0)

# 牆壁顏色 gray:0, green:1, red:2, yellow:3, purple: 4,5, black 6,7 blue 8, white 9
wall_colors = [[128, 138, 135], [0, 200, 0], [200, 0, 0], [255, 255, 0], [162, 32, 240], [162, 32, 240], [0, 0, 0], [0, 0, 0], [65, 105, 225], [255, 255, 255]]

# 玩家物件
class Player(pygame.sprite.Sprite):
	
	def __init__(self, x, y):
		super().__init__()
		# 設定高, 寬
		self.image = kaiImg
		# 設高寬
		self.rect = self.image.get_rect()
		self.rect.y = y
		self.rect.x = x
		# Set speed vector
		self.change_x = 0
		# 石頭力量
		self.move_x = 0
		self.change_y = 0
		self.hp = 3
		self.maxHP = 3
		self.walls = None
		# 鎖
		self.mutex_key = False
		self.hot_time = 0
		self.isdead = False
		self.speed = False
	# 改變速度
	def changeSpeed(self, x, y):
		self.change_x += x
		self.change_y += y
	# 設定速度
	def setSpeed(self, x, y):
		self.change_x = x
		self.change_y = y
	def update(self):
		# 鎖
		if self.islock():
			self.count()
		self.calc_gavy()
		self.rect.y += self.change_y

		# 邊界 下降 死亡
		if (self.rect.top > display_height or self.hp <= 0) and not self.isdead:
			self.isdead = True
			self.hp = 0
			pygame.mixer.Sound.play(dead_music)
			self.kill()

		# 下落是否碰撞
		block_hit_list = pygame.sprite.spritecollide(self, self.walls, False)
		if len(block_hit_list) == 0:
			self.move_x = 0
		for block in block_hit_list:
			# 上至下
			if self.change_y > 0:
				self.change_y = block.change_y
				self.rect.bottom = block.rect.top
				#lock
				if block.kind == 2 and not self.islock():
					if not Hardmode:
						self.hp -= 1
					else:
						self.hp -= 2
					pygame.mixer.Sound.play(hurt_music)
					self.lock()
				elif block.kind == 1 and not self.islock():
					if self.hp < self.maxHP:
						self.hp += 1
						pygame.mixer.Sound.play(recover_music)
						self.lock()
				elif block.kind == 3:
					pygame.mixer.Sound.play(bump_music)
					block.kill()
				# 移動速度
				elif block.kind == 4:
					self.move_x = 1
				elif block.kind == 5:
					self.move_x = -1
				# black
				elif block.kind == 6:
					self.move_x = 1
					block.live_key = True
				elif block.kind == 7:
					self.move_x = -1
					block.live_key = True
				# white
				elif block.kind == 9:
					block.kill()
					self.rect.y -= 100
			elif self.change_y < 0:
				self.rect.top = block.rect.bottom
				
		# 移動
		self.rect.x += self.change_x + self.move_x
		if self.speed:
			self.rect.x += self.change_x

		# 邊界
		if self.rect.left < 0:
			self.rect.left = 0
		if self.rect.right > display_width:
			self.rect.right = display_width

		# 碰撞物件
		block_hit_list = pygame.sprite.spritecollide(self, self.walls, False)
		for block in block_hit_list:
			if self.change_x > 0:
				self.rect.right = block.rect.left
			elif self.change_x < 0:
				self.rect.left = block.rect.right
		
	# 重力
	def calc_gavy(self):
		if self.change_y <= 0:
			self.change_y = 1
		else:
			self.change_y += 0.2
	def lock(self):
		self.mutex_key = True
	def unlock(self):
		self.mutex_key = False
	def islock(self):
		return self.mutex_key
	def count(self):
		self.hot_time += 1
		if self.hot_time == 120:
			self.hot_time = 0
			self.unlock()
	# 卡到ui事件
	def hitUI(self, ui):
		if pygame.sprite.collide_rect(self, ui):
			self.rect.top = ui.rect.bottom
			if not self.islock():
				self.lock()
				pygame.mixer.Sound.play(hurt_music)
				if not Hardmode:
					self.hp -= 1
				else:
					self.hp -= 2
	# 其他物件碰撞
	def otherHit(self, other):
		if pygame.sprite.collide_rect(self, other):
			if self.change_x > 0:
				self.rect.right = other.rect.left
			elif self.change_x < 0:
				self.rect.left = other.rect.right

# 樓梯
class Wall(pygame.sprite.Sprite):
  	# 初始化
	def __init__(self, x, y, width, height, kind, image = None):
		super().__init__()
		if image == None:
			self.image = pygame.Surface([width, height])
			self.image.fill(wall_colors[kind])
		self.rect = self.image.get_rect()
		self.rect.y = y
		self.rect.x = x
		self.change_y = 0.0
		self.kind = kind
		self.livetime = 0
		self.live_key = False
	# 改變速度
	def changeSpeed(self, y):
		self.change_y += y
	# 設定速度
	def setSpeed(self, y):
		self.change_y = y
	def update(self):
		if (self.kind == 6 or self.kind == 7) and self.live_key:
			self.livetime += 1
			if self.livetime == 60:
				self.kill()
		self.rect.y += self.change_y
		if self.rect.bottom < y_side:
				self.kill()
	def draw(self, x=0, y=0):
		gameDisplay.blit(self.image, (x, y))
# 顯示矩形物件
def things(thingx, thingy, thingw, thingh, color):
    pygame.draw.rect(gameDisplay, color, [thingx, thingy, thingw, thingh])

# 貼圖
def show_img(x,y, img):
    gameDisplay.blit(img,(x,y))

# 文字物件
def text_objects(text, font, color=black):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

# 顯示訊息
def message_display(text, x, y, size, color = black):
    largeText = pygame.font.SysFont("comicsansms", size)
    TextSurf, TextRect = text_objects(text, largeText, color)
    TextRect.center = (x,y)
    # 顯示貼圖
    gameDisplay.blit(TextSurf, TextRect)

# 按鈕事件
def button(msg,x,y,w,h,ic,ac,action=None, color=black):
	mouse = pygame.mouse.get_pos()
	click = pygame.mouse.get_pressed()
	global is2P
	if x+w > mouse[0] > x and y+h > mouse[1] > y:
		pygame.draw.rect(gameDisplay, ac,(x,y,w,h))

		if click[0] == 1 and action != None:
			if msg == "GO! 2P":
				is2P = True
			else:
				is2P = False
			action()        
	else:
		pygame.draw.rect(gameDisplay, ic,(x,y,w,h))

	smallText = pygame.font.SysFont("comicsansms",20)
	textSurf, textRect = text_objects(msg, smallText, color)
	textRect.center = ( (x+(w/2)), (y+(h/2)) )
	gameDisplay.blit(textSurf, textRect)

# 離開遊戲
def quitgame():
	pygame.quit()
	quit()

def changeMode():
	global Hardmode
	Hardmode ^= 1   

# 遊戲介紹
def game_intro():
	
	back_music = "music/[Non-Copyrighted Music] Chill Jazzy Lofi Hip Hop (Royalty Free) Jazz Hop Music.mp3"
	pygame.mixer.music.load(back_music)
	pygame.mixer.music.play(-1)

	intro = True
	# 滑鼠隱藏
	pygame.mouse.set_visible(False)

	while intro:
		mouse = pygame.mouse.get_pos()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
			    pygame.quit()
			    quit()

		show_img(0, 0, backImg)
		largeText = pygame.font.SysFont("comicsansms",50)
		TextSurf, TextRect = text_objects("Kai Liu Going Down", largeText, white)
		TextRect.center = ((display_width/2),(display_height/2))
		gameDisplay.blit(TextSurf, TextRect)

		if not Hardmode:
			msg = "easy"
		else:
			msg = "hard"
		# 顯示按鈕
		button("GO! 1P",150,display_height-150,100,50,green,bright_green,game_loop)
		button("GO! 2P",350,display_height-150,100,50,yellow,bright_yellow,game_loop)
		button(msg, 350, display_height-300, 100, 50,black, bright_black,changeMode, white)
		button("Quit",display_width-250,display_height-150,100,50,red,bright_red,quitgame)

		# 滑鼠圖
		show_img(mouse[0]-kai_len/2, mouse[1]-kai_len/2, kaiImg)

		pygame.display.update()
		clock.tick(60)  

# 遊戲 - 主程式
def game_loop():
	# 偵數
	fps = 60
	# 開始音樂
	pygame.mixer.Sound.play(start_music)
	pygame.mixer.music.stop()

	# 層數 初始化, 字體顏色
	floor = 0
	floor_color = black
	
	# 樓梯位置, 間距, 速度
	if not Hardmode:
		rb, re, dis = 1, 6, 50
		wall_speed = -1
		pygame.mixer.music.load(background_music)
	else:
		rb, re, dis = 0, 7, 100
		wall_speed = -2
		pygame.mixer.music.load(background_music2)
	mx_rand_int = 5

	# 背景音樂
	pygame.mixer.music.play(-1)

	# 現在時間
	start_time = pygame.time.get_ticks()
	gen_time = start_time

	# 結束變數
	gameExit = False

	# 玩家物件
	kai = Player(10, y_side)
	kai2 = Player(60, y_side)
	kai_speed = 3

	# ui 物件
	ui = Wall(0, 0, ui_len, y_side, 0)

	# 牆壁
	tmpWall = Wall(0, display_height, wall_width, wall_height, 0)
	tmpWall.setSpeed(wall_speed)

	# 所有物件列表
	all_sprite_list = pygame.sprite.Group()
	# 樓梯列表
	wall_list = pygame.sprite.Group()

	all_sprite_list.add(kai)
	# 2P
	if is2P:
		all_sprite_list.add(kai2)
	all_sprite_list.add(tmpWall)
	wall_list.add(tmpWall)

	while not gameExit:
		# 事件
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quitgame()
			# 往左速度 +3, 反之亦同
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					kai.changeSpeed(-kai_speed, 0)
				if event.key == pygame.K_RIGHT:
					kai.changeSpeed(kai_speed, 0)
				if event.key == pygame.K_a:
					kai2.changeSpeed(-kai_speed, 0)
				if event.key == pygame.K_d:
					kai2.changeSpeed(kai_speed, 0)
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT:
					kai.changeSpeed(kai_speed, 0)
				if event.key == pygame.K_RIGHT:
					kai.changeSpeed(-kai_speed, 0)
				if event.key == pygame.K_a:
					kai2.changeSpeed(kai_speed, 0)
				if event.key == pygame.K_d:
					kai2.changeSpeed(-kai_speed, 0)
		
		# 每次重新
		kai.walls = wall_list
		kai2.walls = wall_list
		# 更新
		all_sprite_list.update()

		# 玩家撞到ui
		kai.hitUI(ui)
		# 玩家2 撞到ui
		if is2P:
			kai2.hitUI(ui)
		# 玩家互碰 1P, 2P 
		if is2P:
			kai.otherHit(kai2)
		if is2P:
			kai2.otherHit(kai)

		# ui 介面
		show_img(0, 0, backImg)
		all_sprite_list.draw(gameDisplay)
		ui.draw()
		message_display('floor ' + str(floor), ui_len/2, y_side/2, 50, floor_color)

		# 玩家血量 固定50
		for i in range(0, 50*kai.hp, 50):
			show_img(i, 0, kaiImg)
		if is2P:
			for i in range(650, 650+50*kai2.hp, 50):
				show_img(i, 0, kaiImg)

		# dead 判斷
		if not is2P:
			if kai.isdead:
				message_display('You Died!', display_width/2, display_height/2, 115, red)
				gameExit = True
		else:
			if kai.isdead and kai2.isdead:
				message_display('You Died!', display_width/2, display_height/2, 115, red)
				gameExit = True

		# 產物件
		if len(wall_list) < max_num:
			# 看最大Wall的距離
			mx = 0
			for each_wall in wall_list:
				mx = max(mx, each_wall.rect.bottom)
			# 每距離dis 產生
			if display_height - mx > dis:
				tmpWall = Wall(random.randint(rb, re)*wall_width, display_height, wall_width, wall_height, random.randint(0, mx_rand_int))
				# blue case
				if tmpWall.kind == 8:
					tmpWall.setSpeed(wall_speed-1)
				else:
					tmpWall.setSpeed(wall_speed)
				all_sprite_list.add(tmpWall)
				wall_list.add(tmpWall)
			
		# 算時間 2 秒
		if pygame.time.get_ticks() - start_time > 2000:
			start_time = pygame.time.get_ticks()
			floor += 1
			# 每50層 加速度 補血, 產道具(update...)
			if floor % 50 == 0:
				kai.maxHP += 1
				kai2.maxHP += 1
				kai.hp += 1
				kai2.hp += 1
				floor_color = [random.randint(0, 256), random.randint(0, 256), random.randint(0, 256)]
				if mx_rand_int < len(wall_colors)-1:
					mx_rand_int += 1
				wall_speed -= 1
				for wall in wall_list:
					wall.setSpeed(wall_speed)
			# 100 level 2倍速
			if floor == 100:
				kai.speed = True
				kai2.speed = True
				pygame.mixer.Sound.play(turn_music)

		# 刷新
		pygame.display.update()
		if gameExit:
			pygame.mixer.music.stop()
			pygame.time.delay(2000)
			game_intro()

		clock.tick(fps)

########### start #######
game_intro()

