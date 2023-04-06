import json
from dataclasses import dataclass
from typing import List, Dict

from pycat.debug import print_warning
from pycat.experimental.ldtk_parser import ImageExportMode, ldtk_from_dict

from pycat.core import Window, Sprite, Label, Color, Point


@dataclass
class Entity:
    id: str
    x: float
    y: float
    width: float
    height: float
    tags: List[str]


@dataclass
class LevelData:
    id: str
    x: float
    y: float
    width: float
    height: float
    entities: List[Entity]


def get_levels_entities(
    ldtk_file_path: str, 
    enforced_export_mode: ImageExportMode = ImageExportMode.ONE_IMAGE_PER_LAYER
) -> List[LevelData]:
    json_string = open(ldtk_file_path, 'r').read()
    data = ldtk_from_dict(json.loads(json_string))
    level_data = []
    for level in data.levels:
        entities = []
        for layer in level.layer_instances:
            for e in layer.entity_instances:
                entities.append(
                    Entity(
                        e.identifier,
                        e.px[0] + e.width/2,
                        level.px_hei-e.px[1] - e.height/2,
                        e.width,
                        e.height,
                        e.tags)
                )
        level_data.append(
            LevelData(
                level.identifier,
                level.world_x,
                level.world_y,
                level.px_wid,
                level.px_hei,
                entities)
        )
    if data.image_export_mode is not enforced_export_mode:
        print_warning('Ensure you select '+str(enforced_export_mode)+' for "Export as PNG" in project settings.')
    return level_data

class LdtkLayeredLevel:
    @classmethod
    def from_file(cls, ldtk_file_path: str, level_id: str, image_path: str, layer_ordering: Dict[str,int]):
        all_level_data = get_levels_entities(ldtk_file_path, ImageExportMode.ONE_IMAGE_PER_LAYER)
        for level_data in all_level_data:
            if level_data.id == level_id:
                return cls(level_data, image_path, layer_ordering)
        print_warning('No level named '+level_id+' in file '+ldtk_file_path)
        print_warning('Possible levels: '+', '.join([l.id for l in all_level_data]))

    def __init__(self, level_data: LevelData, image_path: str, layer_ordering: Dict[str,int]):
        self.image_path = image_path
        self.level_data = level_data
        self.layer_ordering = layer_ordering

        self.layer_sprites: dict[str,Sprite] = {}
        self.entities: list[Sprite] = []
        self.entity_debug_labels: list[Label] = []

    def render(self, window: Window, scale: int = 1, debug_entities: bool = False, debug_entities_layer: int = 1000):
        for layer_name, layer_order in self.layer_ordering.items():
            sprite = window.create_sprite(
                layer=layer_order,
                image=self.image_path+self.level_data.id+'__'+layer_name+'.png',
                scale=scale)
            sprite.x = sprite.width/2
            sprite.y = sprite.height/2
            self.layer_sprites[layer_name] = sprite

        tags_for_debug = set()
        for e in self.level_data.entities:
            s = window.create_sprite(
                x=scale*e.x,
                y=scale*e.y,
                scale_x=scale*e.width,
                scale_y=scale*e.height,
                tags=['ldtk_'+t for t in e.tags],
                opacity=100 if debug_entities else 0,
                layer=debug_entities_layer)
            
            tags_for_debug.update(s.tags)
            if debug_entities:
                s.color = Color.random_rgb()
                label = window.create_label(text=str(s.tags), position=s.position, layer=debug_entities_layer)
                label.position += Point(-label.content_width/2, label.content_height/2)

            self.entities.append(s)

        if debug_entities:
            print_warning('Rendering LDTK level')
            print_warning('Level name: '+self.level_data.id)
            print_warning('Tags in level: '+', '.join([str(tag) for tag in tags_for_debug]))

        