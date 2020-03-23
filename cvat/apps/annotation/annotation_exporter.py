import pathlib
import json
import os.path as osp
from cvat.apps.engine.models import Task, StatusChoice
from django.db import transaction
from cvat.apps.engine.annotation import TaskAnnotation
from cvat.apps.annotation.annotation import Annotation
from django.conf import settings
from cvat.apps.engine.log import slogger
from django.utils import timezone


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
    for frame_idx in range(task.size):
        frame_annotation = {}
        frame_annotation["image_id"] = task.get_global_image_id(frame_idx)
        frame_annotation["video_id"] = task.id
        annotation_completed = task.status == StatusChoice.COMPLETED
        frame_annotation["annotation_completed"] = annotation_completed
        frame_annotation["bounding_boxes"] = []
        frame_annotation["is_test"] = task.is_test()
        converted_annotation.append(frame_annotation)

    for frame in annotation.group_by_frame():
        frame_idx = frame.frame
        frame_annotation = converted_annotation[frame_idx]
        assert frame_annotation["image_id"] == task.get_global_image_id(frame_idx)
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


def get_json_path(include_test):
    label_name = "labels"
    if include_test:
        label_name = label_name + "_test"
    json_path = pathlib.Path(settings.DATA_ROOT, label_name + ".json")
    return str(json_path)


def should_update_annotation(include_test):
    json_path = get_json_path(include_test)
    tasks = Task.objects.all()
    if not osp.exists(json_path):
        return True
    max_time = max(timezone.localtime(t.updated_date).timestamp() for t in tasks)
    archive_time = osp.getmtime(json_path)
    # If max time is larger than archive time and 
    current_time = timezone.localtime().timestamp()
    if max_time > archive_time and archive_time > (current_time + 60*60*12):
        return True
    # Only update the zip file after waiting .5 hours from the last update
    next_update_time = archive_time + 60*30
    if max_time < next_update_time:
        return False

    return True


def get_annotation_filepath(include_test):
    json_path = get_json_path(include_test)
    if not should_update_annotation(include_test):
        return json_path
    annotations = get_all_annotations(include_test)
    with open(json_path, "w") as fp:
        json.dump(annotations, fp)
    return json_path


def annotation_file_ready(include_test):
    return not should_update_annotation(include_test)
