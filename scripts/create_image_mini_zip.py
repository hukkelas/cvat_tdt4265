from django.conf import settings
from cvat.apps.engine.models import Task
import pathlib
import zipfile

archive_path = pathlib.Path(settings.DATA_ROOT, "images_mini.zip")
source_to_target_path = {}
for task in Task.objects.all():
    for frame_idx in range(task.size):
        global_id = task.get_global_image_id(frame_idx)
        if (global_id % 7) != 0:
            continue
        source_path = task.get_frame_path(frame_idx)
        suffix = pathlib.Path(source_path).suffix
        subfolder = "train"
        if task.is_test():
            subfolder = "test"
        target_path = pathlib.Path(
            subfolder, "images", str(task.get_global_image_id(frame_idx)) + suffix)
        source_to_target_path[source_path] = target_path

with zipfile.ZipFile(str(archive_path), "w") as fp:
    for spath, tpath in source_to_target_path.items():
        fp.write(str(spath), str(tpath))

