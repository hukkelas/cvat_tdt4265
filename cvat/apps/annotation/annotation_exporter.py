from cvat.apps.engine.models import Task, StatusChoice
from django.db import transaction
from cvat.apps.engine.annotation import TaskAnnotation
from cvat.apps.annotation.annotation import Annotation
from django.conf import settings
from cvat.apps.engine.log import slogger


def get_annotation(task, include_test):
    with transaction.atomic():
        task_ann = TaskAnnotation(task.id, "")
        task_ann.init_from_db()
    annotation = Annotation(
        task_ann.ir_data,
        task_ann.db_task
    )
    converted_annotation = [
    ]
    for frame in annotation.group_by_frame():
        frame_idx = frame.frame
        annotation_completed = task.status == StatusChoice.COMPLETED
        frame_annotation = {}
        frame_annotation["image_id"] = task.get_global_image_id(frame_idx)
        frame_annotation["video_id"] = task.id
        frame_annotation["annotation_completed"] = annotation_completed
        frame_annotation["bounding_boxes"] = []
        frame_annotation["is_test"] = task.is_test()
        converted_annotation.append(frame_annotation)
        if task.is_test() and not include_test:
            continue
        for labeled_shape in frame.labeled_shapes:
            if labeled_shape.type != "rectangle":
                slogger.task[task.id].info(
                    "Got unexpected label type. Expected rectangle, but got:"
                    + labeled_shape.type
                )
                continue
            xmin, ymin, xmax, ymax = labeled_shape.points
            bbox = {
                "label": labeled_shape.label,
                "label_id": settings.LABEL_MAP[labeled_shape.label],
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmax,
                "ymax": ymax
            }
            frame_annotation["bounding_boxes"].append(bbox)
    return converted_annotation


def get_all_annotations(include_test):
    annotations = []
    for task in Task.objects.all():
        annotations.extend(
            get_annotation(task, include_test)
        )
    return annotations
