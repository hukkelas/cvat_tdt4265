from cvat.apps.engine.models import Task

t = Task.objects.all()
num_completed = len([x for x in t if x.status == "completed"])
num_test = len([x for x in t if x.status == "completed" and x.is_test()])
total_test = len([x for x in t if x.is_test()])
print("percentage:", num_completed / len(t))
print("percentage where they are test", num_test / len(t))
print("Of the test set:", num_test / total_test)
