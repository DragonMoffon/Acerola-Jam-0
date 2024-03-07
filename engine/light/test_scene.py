from pyglet.math import Vec2
from arcade import SpriteList, Sprite

from engine.scene_renderer import SceneRenderer

from engine.light.light_scene import LightScene
from engine.light.light_projector import LightProjector
from engine.light.light_interactors import LightInteractorManager, LightFilter


def generate_test_scene() -> LightScene:
    scene_renderer = SceneRenderer()

    # Baking Scene with the SceneRenderer for the projector
    scene_list = SpriteList()
    scene_list.extend(
        (
            Sprite(":r:danger_block.png", center_x=0, center_y=16),
            Sprite(":r:danger_block.png", center_x=0, center_y=0),
            Sprite(":r:danger_block.png", center_x=0, center_y=-16)
        )
    )
    _scene_texture = scene_renderer.bake_scene_texture(scene_list, "test_scene")

    # Projector
    projector: LightProjector = LightProjector(
        _scene_texture,
        (True, True, True),
        150.0,
        Vec2(0.0, 0.0),
        Vec2(1.0, 0.0)
    )
    projectors = (projector,)

    interactor_manager = LightInteractorManager()

    light_filter = LightFilter(Vec2(75, 30), Vec2(1.0, 0.0), 30, 100)
    interactor_manager.add_interactor(light_filter)

    scene = LightScene(
        scene_renderer,
        interactor_manager,
        projectors
    )

    projector.set_parent(scene)
    projector.turn_on()

    return scene
