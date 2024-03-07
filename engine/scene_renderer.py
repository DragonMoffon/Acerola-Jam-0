from PIL import Image

from arcade import TextureAtlas, Texture, get_window, SpriteList


class SceneRenderer:

    def __init__(self):
        self._win = get_window()
        self._scene_atlas: TextureAtlas = TextureAtlas((2000, 2000))

    def bake_scene_texture(self, scene_list: SpriteList, scene_name: str | None = None) -> Texture:
        assert len(scene_list) > 0, "Trying to bake a scene with no sprites in it!"

        # Make sure the values are well above/below what is possible
        left = bottom = 100000000000
        right = top = -100000000000

        # Find the bounding box of the scene
        for sprite in scene_list:
            if sprite.left < left:
                left = int(sprite.left)
            if sprite.right > right:
                right = int(sprite.right)
            if sprite.top > top:
                top = int(sprite.top)
            if sprite.bottom < bottom:
                bottom = int(sprite.bottom)

        # Create an empty texture
        scene_size = (right - left, top - bottom)
        scene_image = Image.new("RGBA", scene_size, (0, 0, 0, 0))
        scene_texture = Texture(scene_image, hash=scene_name)

        # Add empty texture to atlas
        self._scene_atlas.add(scene_texture)

        # Render sprites into texture
        with self._scene_atlas.render_into(scene_texture, (left, right, bottom, top)) as atlas:
            scene_list.draw(pixelated=True)
        self._scene_atlas.update_texture_image_from_atlas(scene_texture)

        return scene_texture

    def update_scene_texture(self, scene_texture, scene_list):
        raise NotImplementedError("Can't update scene's yet")

    @property
    def atlas(self):
        return self._scene_atlas