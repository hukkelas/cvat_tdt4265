from cvat.apps.project_submission.models import ProjectSubmission
from cvat.apps.engine.models import Task
from collections import defaultdict
groups = [
    64, 103, 101, 114, 120, 99, 109, 115, 125, 128, 1, 111, 44, 150, 69, 169, 42, 10, 110, 12, 140,
    106, 16, 197, 112, 100, 127, 105, 105, 13, 142, 107, 2, 123, 98, 14, 108, 90, 11, 166, 147, 113, 55, 149, 8]


annotation_complete_count = defaultdict(int)

for task in Task.objects.all():
    if task.status != "completed":
        continue
    user = task.assignee.username
    if "group" not in user:
        continue
    user = int(user.replace("group", ""))
    annotation_complete_count[user] += 1




group_to_max_map = defaultdict(float)
group_to_max_map_total = defaultdict(float)
for submission in ProjectSubmission.objects.all():
    user = submission.user.username
    if "group" not in user:
        continue
    user = int(user.replace("group", ""))
    mAP_tot = submission.mean_average_precision_total
    if mAP_tot is None:
        continue
    mAP = submission.mean_average_precision_leaderboard
    print(mAP_tot)
    group_to_max_map_total[user] = max(group_to_max_map_total[user], mAP_tot)
    group_to_max_map[user] = max(group_to_max_map[user], mAP)

print("Group", "Leaderboard mAP", "Total mAP")
import numpy as np
mean = np.mean(list(group_to_max_map_total.values()))
std = np.std(list(group_to_max_map_total.values()))
print("Mean:", mean, "STD:", std)
for group in groups:
    print(group, group_to_max_map[group], group_to_max_map_total[group], annotation_complete_count[group])
