# player.py （直接複製全部覆蓋舊檔即可）
import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.speed = 200
        self.running_speed = 300
        self.running = False
        
        self.x = 0
        self.y = 0
        
        self.just_spawned = True
        self.was_in_portal = False
        
        # 預設載入騎士角色
        self.set_character("knight")

    def render(self, surface):
        surface.blit(self.image, self.rect)

    def set_character(self, character_name: str):
        """根據角色名稱載入圖片"""
        try:
            image_path = f"./assets/{character_name}.png"
            original_image = pygame.image.load(image_path).convert_alpha()
        except FileNotFoundError:
            print(f"錯誤：找不到角色圖片檔案 {image_path}。將使用預設圖片。")
            original_image = pygame.Surface((32, 48), pygame.SRCALPHA)
            original_image.fill((255, 0, 255))

        # 根據角色調整縮放因子，讓 Magician 更小
        if character_name == "knight":
            scale_factor = 1.5
        elif character_name == "magician":
            scale_factor = 0.1  # 調整為更小的值，讓 Magician 變得更小，如果仍太大，可再調小如 0.05
        else:
            scale_factor = 1.0

        original_size = original_image.get_size()
        new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
        self.image = pygame.transform.scale(original_image, new_size)
        # 創建 rect，但位置將由 game.py 的 change_map 統一管理
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def handle_movement(
        self,
        delta_time: float,
        actions: dict,
        tiles: pygame.sprite.Group,
        metadata: dict,
        game=None
    ):
        dx = 0
        dy = 0
        
        # 根據是否按下 Shift 鍵來決定速度
        current_speed = self.running_speed if actions.get(pygame.K_LSHIFT) or actions.get(pygame.K_RSHIFT) else self.speed
        
        if actions.get(pygame.K_a) or actions.get(pygame.K_LEFT):
            dx -= current_speed * delta_time
        if actions.get(pygame.K_d) or actions.get(pygame.K_RIGHT):
            dx += current_speed * delta_time
        if actions.get(pygame.K_w) or actions.get(pygame.K_UP):
            dy -= current_speed * delta_time
        if actions.get(pygame.K_s) or actions.get(pygame.K_DOWN):
            dy += current_speed * delta_time

        # X軸移動與碰撞
        if dx != 0:
            old_x = self.x
            self.x += dx
            self.rect.centerx = self.x
            hit_tiles = pygame.sprite.spritecollide(self, tiles, False)
            blocked_tiles = [t for t in hit_tiles if t.gid in metadata["collision_gid"]]
            if blocked_tiles:
                print("X collision detected with blocked tiles at positions:", [(t.rect.x, t.rect.y) for t in blocked_tiles])  # 更詳細 debug: 打印阻擋 tile 的位置
                self.x = old_x
                self.rect.centerx = self.x

        # Y軸移動與碰撞
        if dy != 0:
            old_y = self.y
            self.y += dy
            self.rect.centery = self.y
            hit_tiles = pygame.sprite.spritecollide(self, tiles, False)
            blocked_tiles = [t for t in hit_tiles if t.gid in metadata["collision_gid"]]
            if blocked_tiles:
                print("Y collision detected with blocked tiles at positions:", [(t.rect.x, t.rect.y) for t in blocked_tiles])  # 更詳細 debug: 打印阻擋 tile 的位置
                self.y = old_y
                self.rect.centery = self.y

        # 最終同步
        self.rect.center = (self.x, self.y)

        # 檢查傳送門（移到移動後，並加入初始生成檢查邏輯）
        if game and "exit" in metadata:
            hit_tiles = pygame.sprite.spritecollide(self, tiles, False)
            matched_exit = None
            for tile in hit_tiles:
                for exit_info in metadata["exit"]:
                    if tile.x == exit_info["x"] and tile.y == exit_info["y"]:
                        matched_exit = exit_info
                        break
                if matched_exit:
                    break
            
            is_in_portal = matched_exit is not None
            
            if is_in_portal and not self.was_in_portal and not self.just_spawned:
                target_map = matched_exit["to"]
                player_start_pos = (matched_exit["start_pos"]["x"], matched_exit["start_pos"]["y"]) if "start_pos" in matched_exit else None
                game.change_map(target_map, player_start_pos)
                return  # 觸發後返回，避免繼續執行
            
            self.was_in_portal = is_in_portal
            
            if self.just_spawned:
                self.just_spawned = False

    def update(self, delta_time: float, actions: dict):
        pass