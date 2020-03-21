import json
import os
from django.core.exceptions import ValidationError


def validate_json_formatted(filefield):
    try:
        l = json.loads(filefield.read().decode())
        if not isinstance(l, list):
            raise ValidationError('The outer JSON type must be a list')
        if len(l) == 0:
            raise ValidationError('Empty submission')
        expected_fields = set(['image_id', 'bboxes'])
        expected_bbox_fields = set(['xmin', 'xmax', 'ymin', 'ymax', 'confidence', 'label'])
        for image_annotation in l:
            if not isinstance(image_annotation, dict):
                raise ValidationError('Invalid annotation JSON')
            if not set(image_annotation.keys()) == expected_fields:
                 raise ValidationError('Invalid annotation JSON')
            if not isinstance(image_annotation['image_id'], int):
                raise ValidationError('Invalid annotation JSON')
            if image_annotation['image_id'] >= len(l):
                raise ValidationError('Invalid annotation JSON')
            if not isinstance(image_annotation['bboxes'], list):
                raise ValidationError('Invalid annotation JSON')
            for bbox in image_annotation['bboxes']:
                if not isinstance(bbox, dict):
                    raise ValidationError('Invalid annotation JSON')
                if not set(bbox.keys()) == expected_bbox_fields:
                    raise ValidationError('Invalid annotation JSON')
    except Exception as e:
        raise ValidationError('Expected a UTF-8 formatted JSON file. '+str(e))
